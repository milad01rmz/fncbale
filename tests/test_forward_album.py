import json

import pytest

from fncbale import Album, Client, MediaKind, Message, MessageRef, Peer, PeerKind, Session, contract
from fncbale.errors import IdempotencyConflict, MessageReferencesUnavailable
from fncbale.events import message_from_history
from fncbale.models import MediaInfo
from fncbale.proto import struct_pb2 as s


def setup_client(tmp_path):
    client = Client(Session(123, "fake"), data_dir=tmp_path)
    client.account, client._active = "test", True
    source = Peer(PeerKind.CHANNEL, 10, 12)
    target = Peer(PeerKind.CHANNEL, 20, 22)
    items = tuple(
        Message(
            MessageRef(source, 100 + index, 50 + index),
            media=MediaInfo(kind, 900 + index, 123, 100, "fixture", "application/octet-stream"),
            grouped_id=700,
        )
        for index, kind in enumerate((MediaKind.PHOTO, MediaKind.VIDEO))
    )
    return client, target, Album(items, 700)


async def test_grouped_forward_is_frozen_reusable_and_distinct_from_ordinary_forward(tmp_path):
    client, target, album = setup_client(tmp_path)
    try:
        handle = await client.enqueue_forward_album(target, album, idempotency_key="grouped")
        again = await client.enqueue_forward_album(target, album, idempotency_key="grouped")
        assert again.operation_id == handle.operation_id
        row = await client.store.operation(client.account, handle.operation_id)
        context = json.loads(row["context"])
        request = contract("ForwardMessages").request.FromString(row["payload"])
        assert request.groupedId.value == context["grouped_id"] != album.grouped_id
        assert list(request.rid) == context["rids"] and len(set(request.rid)) == 2
        assert [item.rid for item in request.forwardedMessages] == [100, 101]
        with pytest.raises(IdempotencyConflict):
            await client.enqueue_forward(target, album.messages, idempotency_key="grouped")
        ordinary = await client.enqueue_forward(target, album.messages)
        row = await client.store.operation(client.account, ordinary.operation_id)
        assert not contract("ForwardMessages").request.FromString(row["payload"]).HasField("groupedId")
    finally:
        await client.close()


async def test_forward_album_validates_before_durable_admission(tmp_path):
    client, target, album = setup_client(tmp_path)
    try:
        for invalid in (
            Album(album.messages[:1], 700),
            Album(album.messages * 6, 700),
            Album((album.messages[0], album.messages[0]), 700),
            Album(album.messages, 701),
        ):
            with pytest.raises(ValueError):
                await client.enqueue_forward_album(target, invalid)
        album.messages[1].media = None
        with pytest.raises(ValueError):
            await client.enqueue_forward_album(target, album)
        assert not [item async for item in client.iter_operations()]
    finally:
        await client.close()


async def test_grouped_forward_history_proof_requires_group_and_returns_exact_refs_after_restart(tmp_path):
    client, target, album = setup_client(tmp_path)
    try:
        handle = await client.enqueue_forward_album(target, album)
        row = await client.store.operation(client.account, handle.operation_id)
        context = json.loads(row["context"])
        received = []
        for index, rid in enumerate(context["rids"]):
            wire = s.WebHistory(rid=rid, date=60 + index)
            wire.seq.value = 500 + index
            wire.groupedId.value = context["grouped_id"]
            received.append(message_from_history(target, wire))

        async def history(*args, **kwargs):
            for message in received:
                yield message

        client.iter_history = history
        await client.store.finish(client.account, handle.operation_id, "uncertain", error="lost ACK")
        received[1].grouped_id = 999
        assert not await client._reconcile_row(
            await client.store.operation(client.account, handle.operation_id)
        )
        received[1].grouped_id = context["grouped_id"]
        assert await client._reconcile_row(await client.store.operation(client.account, handle.operation_id))
        result = await handle.wait()
        assert isinstance(result, Album) and result.grouped_id == context["grouped_id"]
        assert [message.ref for message in result.messages] == [message.ref for message in received]
        assert all(message.history_verified and not message.rpc_confirmed for message in result.messages)
        await client.close()
        client, _, _ = setup_client(tmp_path)
        restored = await client.wait_operation(handle.operation_id)
        assert isinstance(restored, Album) and [m.ref for m in restored.messages] == [m.ref for m in received]
    finally:
        await client.close()


async def test_grouped_forward_ack_without_matching_history_does_not_guess_or_resend(tmp_path):
    client, target, album = setup_client(tmp_path)
    try:
        handle = await client.enqueue_forward_album(target, album)
        row = await client.store.operation(client.account, handle.operation_id)
        context = json.loads(row["context"])

        async def history(*args, **kwargs):
            for rid in context["rids"]:
                yield Message(MessageRef(target, rid, 60), grouped_id=999)

        client.iter_history = history
        await client.store.finish(
            client.account,
            handle.operation_id,
            "confirmed",
            response=contract("ForwardMessages").response(date=60).SerializeToString(),
        )
        with pytest.raises(MessageReferencesUnavailable):
            await handle.wait()
        row = await client.store.operation(client.account, handle.operation_id)
        assert row["status"] == "confirmed" and row["attempts"] == 0
    finally:
        await client.close()
