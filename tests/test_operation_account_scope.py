import asyncio
import json

import pytest

from fncbale import Client, Peer, PeerKind, Session
from fncbale.contracts import contract
from fncbale.errors import BaleError
from fncbale.events import message_from_history
from fncbale.events import journal_events
from fncbale.proto import struct_pb2 as s


def client_for(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    client.account, client._active = "original", True
    return client


@pytest.mark.parametrize(
    "method", ["get_operation", "wait_operation", "retry_operation", "reconcile_operation"]
)
async def test_inflight_operation_read_rejects_switch_before_next_stage(tmp_path, method):
    client = client_for(tmp_path)
    handle = await client.enqueue_message(Peer(PeerKind.USER, 7), "frozen")
    status = {"retry_operation": "failed", "reconcile_operation": "uncertain"}.get(method, "queued")
    await client.store.finish("original", handle.operation_id, status)
    entered, release = asyncio.Event(), asyncio.Event()
    original = client.store.operation
    queries = []

    async def operation(account, operation_id):
        queries.append(account)
        row = await original(account, operation_id)
        entered.set()
        await release.wait()
        return row

    client.store.operation = operation
    task = asyncio.create_task(getattr(client, method)(handle.operation_id))
    try:
        await entered.wait()
        client.account = "new-account"
        release.set()
        with pytest.raises(BaleError, match="account"):
            await asyncio.wait_for(task, 0.5)
        assert queries == ["original"] and not client._operation_waiters
        assert (await original("original", handle.operation_id))["status"] == status
    finally:
        release.set()
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        await client.close()


@pytest.mark.parametrize("method", ["status", "wait", "cancel"])
async def test_retained_handle_rejects_changed_account_before_ledger_access(tmp_path, method):
    client = client_for(tmp_path)
    handle = await client.enqueue_message(Peer(PeerKind.USER, 7), "original")
    calls = []
    original = client.store.operation

    async def operation(account, operation_id):
        calls.append(account)
        return await original(account, operation_id)

    try:
        client.store.operation = operation
        client.account = "new-account"
        with pytest.raises(BaleError, match="account"):
            await getattr(handle, method)()
        assert not calls
        assert (await original("original", handle.operation_id))["status"] == "queued"
    finally:
        await client.close()


async def test_operation_page_does_not_yield_buffered_previous_account_rows(tmp_path):
    client = client_for(tmp_path)
    try:
        for i in range(3):
            await client.enqueue_message(Peer(PeerKind.USER, 7), str(i))
        iterator = client.iter_operations(page_size=3)
        await anext(iterator)
        client.account = "new-account"
        with pytest.raises(StopAsyncIteration):
            await anext(iterator)
        assert len(await client.store.operation_page("original")) == 3
    finally:
        await client.close()


async def test_failed_event_page_stops_at_account_change(tmp_path):
    client = client_for(tmp_path)
    try:
        update = s.WebUpdate()
        update.message.peer.type, update.message.peer.id = 1, 7
        for rid in range(3):
            update.message.rid, update.message.date = rid + 1, rid + 1
            event_id = (
                await client.store.record("original", update.SerializeToString(), journal_events(update))
            )[0]
            await client.store.fail_event("original", event_id, 1)
        iterator = client.iter_failed_events(page_size=3)
        await anext(iterator)
        client.account = "new-account"
        with pytest.raises(StopAsyncIteration):
            await anext(iterator)
        assert len(await client.store.failed_event_page("original")) == 3
    finally:
        await client.close()


async def test_committed_handle_keeps_account_at_admission(tmp_path):
    client = client_for(tmp_path)
    original = client.store.enqueue
    entered, release = asyncio.Event(), asyncio.Event()

    async def enqueue(*args, **kwargs):
        operation_id = await original(*args, **kwargs)
        entered.set()
        await release.wait()
        return operation_id

    client.store.enqueue = enqueue
    pending = asyncio.create_task(client.enqueue_message(Peer(PeerKind.USER, 7), "frozen"))
    try:
        await entered.wait()
        client.account = "new-account"
        release.set()
        handle = await pending
        with pytest.raises(BaleError, match="account"):
            await handle.status()
        client.account = "original"
        assert (await handle.status()).status == "queued"
    finally:
        release.set()
        await asyncio.gather(pending, return_exceptions=True)
        await client.close()


@pytest.mark.parametrize("mode", ["confirmed", "uncertain"])
async def test_history_completion_cannot_mutate_another_account_ledger(tmp_path, mode):
    client = client_for(tmp_path)
    peer = Peer(PeerKind.CHANNEL, 10, 12)
    request = contract("SendMultiMediaMessage").request(groupedId=7)
    request.peer.type, request.peer.id, request.peer.accessHash = peer.out_type, peer.id, peer.access_hash
    for rid in (101, 102):
        request.multiMedia.add(randomId=rid).media.caption.text = "original"
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
        "original",
        handle.operation_id,
        mode,
        response=contract("SendMultiMediaMessage").response(date=42).SerializeToString(),
    )
    entered, release = asyncio.Event(), asyncio.Event()
    writes = []
    original_refs, original_finish = client.store.save_message_refs, client.store.finish

    async def refs(account, *args):
        writes.append(account)
        return await original_refs(account, *args)

    async def finish(account, *args, **kwargs):
        writes.append(account)
        return await original_finish(account, *args, **kwargs)

    async def history(*args, **kwargs):
        entered.set()
        await release.wait()
        for rid in (101, 102):
            raw = s.WebHistory(rid=rid, date=42)
            raw.groupedId.value = 7
            yield message_from_history(peer, raw)

    client.store.save_message_refs, client.store.finish, client.iter_history = refs, finish, history
    pending = asyncio.create_task(
        handle.wait() if mode == "confirmed" else client.reconcile_operation(handle.operation_id)
    )

    async def recover():
        pass

    client.recover = recover
    try:
        await asyncio.wait_for(entered.wait(), 1)
        client.account = "new-account"
        release.set()
        with pytest.raises(BaleError, match="account"):
            await pending
        assert not writes
        row = await client.store.operation("original", handle.operation_id)
        assert row["status"] == mode and "_message_refs" not in json.loads(row["context"])
    finally:
        release.set()
        await asyncio.gather(pending, return_exceptions=True)
        await client.close()
