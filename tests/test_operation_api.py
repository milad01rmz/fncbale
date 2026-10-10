import asyncio
import json

import pytest

from fncbale import Client, Config, MessageRef, OperationHandle, OperationStatus, Peer, PeerKind, Session
from fncbale.contracts import contract
from fncbale.events import message_from_history
from fncbale.proto import struct_pb2 as s


def paused_client(tmp_path):
    client = Client(Session(123, "fake-not-a-token"), data_dir=tmp_path, config=Config(outbox_workers=1))
    client.account, client._active = "test", True
    return client


async def test_all_message_mutations_return_committed_handles_and_survive_restart(tmp_path):
    client = paused_client(tmp_path)
    peer = Peer(PeerKind.CHANNEL, 10, 12)
    ref = MessageRef(peer, 99, 10, 2**55 + 3)
    history = s.WebHistory(rid=99, date=10)
    history.message.documentMessage.fileId = 123
    history.message.documentMessage.caption.text = "before"
    history.message.documentMessage.fileSize = 12
    photo = message_from_history(peer, history)

    async def history_iter(*args, **kwargs):
        yield photo

    client.iter_history = history_iter
    handles = []
    try:
        handles = [
            await client.enqueue_edit_message(ref, "edited", idempotency_key="edit"),
            await client.enqueue_edit_caption(ref, "caption", idempotency_key="caption"),
            await client.enqueue_delete_message(ref, idempotency_key="delete"),
            await client.enqueue_forward(peer, ref, idempotency_key="forward"),
        ]
        assert all(isinstance(handle, OperationHandle) for handle in handles)
        summaries = [item async for item in client.iter_operations(page_size=1)]
        assert {item.operation_id for item in summaries} == {handle.operation_id for handle in handles}
        assert all(item.status == OperationStatus.QUEUED and item.attempts == 0 for item in summaries)
        reused = await client.enqueue_forward(peer, ref, idempotency_key="forward")
        assert reused.operation_id == handles[-1].operation_id
        row = await client.store.operation(client.account, handles[-1].operation_id)
        forwarded = contract("ForwardMessages").request.FromString(row["payload"])
        assert list(forwarded.rid) == json.loads(row["context"])["rids"]
        assert forwarded.forwardedMessages[0].seq.value == ref.seq
        pending = asyncio.create_task(handles[0].wait())
        await asyncio.sleep(0)
        pending.cancel()
        with pytest.raises(asyncio.CancelledError):
            await pending
        assert (await handles[0].status()).status == OperationStatus.QUEUED
        assert not client._operation_waiters
    finally:
        await client.close()

    restarted = paused_client(tmp_path)
    calls = []

    async def call(method, payload, route):
        calls.append((method, payload))
        response = contract(method).response()
        if hasattr(response, "date"):
            response.date = 42
        return response.SerializeToString()

    restarted._call_bytes = call
    try:
        remaining = [item async for item in restarted.iter_operations(statuses="queued", page_size=2)]
        assert {item.operation_id for item in remaining} == {handle.operation_id for handle in handles}
        restarted._tasks.append(asyncio.create_task(restarted._outbox_worker()))
        results = await asyncio.wait_for(
            asyncio.gather(*(restarted.wait_operation(handle.operation_id) for handle in handles)), 10
        )
        assert len(calls) == 4 and results[0].ref == ref
        assert results[1].text == "caption" and results[1].media.file_id == 123
        assert results[2] == (99,) and len(results[3]) == 1
        assert all(item.rpc_confirmed for item in [x async for x in restarted.iter_operations()])
    finally:
        await restarted.close()


async def test_inspection_keyset_ties_filters_privacy_and_account_scope(tmp_path):
    client = paused_client(tmp_path)
    peer = Peer(PeerKind.CHANNEL, 10, 12)
    try:
        handles = [
            await client.enqueue_message(peer, "private payload", idempotency_key=str(i)) for i in range(6)
        ]
        await client.store.enqueue("other-account", peer.key, "SendMessage", b"secret", "{}")
        await client.store.run(lambda db: db.execute("UPDATE operations SET created=10"))
        assert await handles[2].cancel()
        await client.store.finish(client.account, handles[4].operation_id, "uncertain", error="ambiguous")
        all_ops = [item async for item in client.iter_operations(page_size=2)]
        assert len(all_ops) == 6 and len({item.operation_id for item in all_ops}) == 6
        assert [item.operation_id for item in all_ops] == sorted(handle.operation_id for handle in handles)
        selected = [
            item async for item in client.iter_operations(statuses=["cancelled", "uncertain"], page_size=1)
        ]
        assert {item.operation_id for item in selected} == {handles[2].operation_id, handles[4].operation_id}
        assert len([item async for item in client.iter_operations(limit=3, page_size=2)]) == 3
        assert not [item async for item in client.iter_operations(statuses=[])]
        assert not [item async for item in client.iter_operations(limit=0)]
        rows = await client.store.operation_page(client.account, limit=2)
        assert all(not {"payload", "response", "peer", "idem"} & row.keys() for row in rows)
        assert "private payload" not in repr(rows)
        for kwargs in ({"page_size": 0}, {"page_size": 1001}, {"limit": -1}, {"statuses": ["bogus"]}):
            with pytest.raises(ValueError):
                _ = [item async for item in client.iter_operations(**kwargs)]
    finally:
        await client.close()


async def test_album_exact_item_dates_commit_survive_restart_and_no_ack_fallback(tmp_path):
    from fncbale import MessageReferencesUnavailable

    peer = Peer(PeerKind.CHANNEL, 10, 12)
    client = paused_client(tmp_path)
    request = contract("SendMultiMediaMessage").request(groupedId=7)
    request.peer.type, request.peer.id, request.peer.accessHash = peer.out_type, peer.id, peer.access_hash
    request.multiMedia.add(randomId=101).media.caption.text = "first"
    request.multiMedia.add(randomId=102).media.caption.text = "second"
    refs = []
    for rid, date in ((101, 41), (102, 42)):
        history = s.WebHistory(rid=rid, date=date)
        history.groupedId.value = 7
        history.seq.value = rid + 100
        refs.append(message_from_history(peer, history))
    reads = []

    async def history_iter(*args, **kwargs):
        reads.append(kwargs)
        for message in refs:
            yield message

    client.iter_history = history_iter
    try:
        handle = await client._enqueue(
            peer,
            "SendMultiMediaMessage",
            request,
            {
                "kind": "album",
                "peer": {"kind": "channel", "id": 10, "access_hash": 12},
                "grouped_id": 7,
                "rids": [101, 102],
            },
        )
        await client.store.finish(
            client.account,
            handle.operation_id,
            "confirmed",
            response=contract("SendMultiMediaMessage").response(date=42).SerializeToString(),
        )
        album = await handle.wait()
        assert [item.ref.date for item in album.messages] == [41, 42]
        assert [item.ref.seq for item in album.messages] == [201, 202]
        assert len(reads) == 1 and reads[0]["before"] == 42 and reads[0]["limit"] == 100
        assert all(item.rpc_confirmed and item.history_verified for item in album.messages)
        await client.close()
        client = paused_client(tmp_path)
        # Stored references resolve even while disconnected, without another network read.
        client._active = False
        again = await client.wait_operation(handle.operation_id)
        assert [item.ref for item in again.messages] == [item.ref for item in album.messages]
        row = await client.store.operation(client.account, handle.operation_id)
        context = json.loads(row["context"])
        context.pop("_message_refs")
        await client.store.run(
            lambda db: db.execute(
                "UPDATE operations SET context=? WHERE id=?", (json.dumps(context), handle.operation_id)
            )
        )

        async def missing(*args, **kwargs):
            if False:
                yield

        client.iter_history = missing
        with pytest.raises(MessageReferencesUnavailable) as caught:
            await client.wait_operation(handle.operation_id)
        status = await client.get_operation(caught.value.operation_id)
        assert status.status == "confirmed" and status.rpc_confirmed and status.attempts == 0
    finally:
        await client.close()
