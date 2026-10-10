import json

import pytest

from fncbale import Album, Client, MessageRef, Peer, PeerKind, Session, contract
from fncbale.errors import StorageError
from fncbale.events import message_from_history
from fncbale.events import Event
from fncbale.models import Message
from fncbale.proto import struct_pb2 as s
from fncbale.dispatcher import FSM


def fixture(tmp_path):
    client = Client(Session(123, "fake"), data_dir=tmp_path)
    client.account, client._active = "copy-test", True
    client.fsm = FSM(client.store, client.account)
    source, target = Peer(PeerKind.CHANNEL, 10, 12), Peer(PeerKind.CHANNEL, 20, 22)
    wires = []
    for index in range(2):
        wire = s.WebHistory(rid=100 + index, date=50 + index)
        wire.groupedId.value = 700
        doc = wire.message.documentMessage
        doc.fileId, doc.accessHash, doc.fileSize = 900 + index, 123, 100
        doc.caption.text = f"*caption {index}*"
        doc.mimeType, doc.name = "image/png", "one.png"
        doc.ext.documentExPhoto.w, doc.ext.documentExPhoto.h = 30, 20
        doc.ParseFromString(doc.SerializeToString() + b"\x98\x06\x01")
        wires.append(wire)
    messages = [message_from_history(source, wire) for wire in wires]

    async def history(peer, **kwargs):
        for message in messages:
            yield message

    client.iter_history = history
    return client, source, target, wires, Album(tuple(messages), 700)


async def test_copy_album_freezes_metadata_unknown_fields_reply_and_ids_without_upload(tmp_path):
    client, _, target, wires, album = fixture(tmp_path)
    try:
        reply = MessageRef(target, 999, 40, 8)
        handle = await client.enqueue_copy_album(target, album, reply_to=reply, idempotency_key="copy")
        same = await client.enqueue_copy_album(target, album, reply_to=reply, idempotency_key="copy")
        assert same.operation_id == handle.operation_id
        row = await client.store.operation(client.account, handle.operation_id)
        request = contract("SendMultiMediaMessage").request.FromString(row["payload"])
        context = json.loads(row["context"])
        assert context["grouped_id"] == request.groupedId != 700
        assert list(item.randomId for item in request.multiMedia) == context["rids"]
        assert request.repliedMessage.rid == reply.rid
        assert "media" not in context and not (tmp_path / "spool").exists()
        assert [item.media.SerializeToString() for item in request.multiMedia] == [
            wire.message.documentMessage.SerializeToString() for wire in wires
        ]
        wires[0].message.documentMessage.caption.text = "caller changed"
        assert request.multiMedia[0].media.caption.text == "*caption 0*"
        await client.close()
        client, _, _, _, _ = fixture(tmp_path)
        restored = await client.store.operation(client.account, handle.operation_id)
        assert restored["payload"] == row["payload"] and restored["status"] == "queued"
    finally:
        await client.close()


async def test_copy_rejects_missing_or_foreign_source_and_invalid_album_before_admission(tmp_path):
    client, source, target, _, album = fixture(tmp_path)
    try:
        with pytest.raises(ValueError):
            await client.enqueue_copy_message(target, MessageRef(source, 999, 50))
        with pytest.raises(ValueError):
            await client.enqueue_copy_album(target, Album(album.messages, 701))
        with pytest.raises(ValueError):
            await client._enqueue_copy_snapshots(target, [s.WebHistory(rid=1)])
        assert not [operation async for operation in client.iter_operations()]
    finally:
        await client.close()


async def test_mirror_replays_confirmed_copy_after_mapping_failure_without_another_send(tmp_path):
    from examples.channel_mirror import ChannelMirror

    client, source, target, wires, _ = fixture(tmp_path)
    mirror = ChannelMirror(client, source, target)
    original = client._enqueue_copy_snapshots
    calls = []

    async def enqueue(*args, **kwargs):
        handle = await original(*args, **kwargs)
        calls.append(handle.operation_id)
        await client.store.finish(
            client.account,
            handle.operation_id,
            "confirmed",
            response=contract("SendMessage").response(date=80).SerializeToString(),
        )
        return handle

    client._enqueue_copy_snapshots = enqueue
    put = mirror.put
    failed = False

    async def flaky(key, value):
        nonlocal failed
        if key.startswith("rid:") and not failed:
            failed = True
            raise StorageError("Injected map commit failure")
        return await put(key, value)

    mirror.put = flaky
    try:
        with pytest.raises(StorageError):
            await mirror.deliver(wires[:1])
        await mirror.deliver(wires[:1])
        assert len(calls) == 1
        mapping = await mirror.mapping(wires[0].rid)
        assert mapping["target"]["date"] == 80
        wires[1].quotedMessage.messageId.value = wires[0].rid
        wires[1].quotedMessage.quotedPeer.id = source.id
        reply = await mirror.reply(wires[1])
        assert reply.rid == mapping["target"]["rid"] and reply.peer == target
    finally:
        await client.close()


async def test_mirror_aggregate_album_ack_reads_all_siblings_without_timestamp_clipping(tmp_path):
    from examples.channel_mirror import ChannelMirror

    client, source, target, _, _ = fixture(tmp_path)
    mirror = ChannelMirror(client, source, target)
    wires = []
    for index in range(10):
        wire = s.WebHistory(rid=100 + index, date=50 + index)
        wire.groupedId.value = 700
        wires.append(wire)
    reads, delivered = [], []

    async def history(*, limit=100, before=-1):
        reads.append(before)
        return wires if before == -1 else [wire for wire in wires if wire.date <= before]

    async def deliver(items):
        delivered.append(items)

    mirror.history, mirror.deliver = history, deliver
    try:
        await mirror.on_event(
            Event("album-ack", "sent", source, b"", message=Message(MessageRef(source, 700, 55)))
        )
        assert reads == [-1] and [wire.rid for wire in delivered[0]] == list(range(100, 110))
    finally:
        await client.close()


async def test_duplicate_sent_ack_does_not_read_history_or_reissue_copy(tmp_path):
    from examples.channel_mirror import ChannelMirror

    client, source, target, _, _ = fixture(tmp_path)
    mirror = ChannelMirror(client, source, target)
    try:
        await mirror.put("rid:100", {"target": {"rid": 200, "date": 60, "seq": 0}})

        async def forbidden(**kwargs):
            pytest.fail("Mapped identity-only ACK must not trigger another read/send")

        mirror.history = forbidden
        await mirror.on_event(Event("ack", "sent", source, b"", message=Message(MessageRef(source, 100, 50))))
    finally:
        await client.close()
