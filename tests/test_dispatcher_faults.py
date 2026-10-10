import asyncio
import sqlite3
import pytest

from fncbale import Client, Config, Session
from fncbale.events import journal_events
from fncbale.proto.struct_pb2 import WebUpdate


async def seed(client, rid):
    update = WebUpdate()
    update.message.peer.type, update.message.peer.id = 1, 10
    update.message.rid, update.message.date = rid, 1
    return (await client.store.record("a", update.SerializeToString(), journal_events(update)))[0]


async def settled(client, ids):
    async with asyncio.timeout(4):
        while True:
            rows = await client.store.run(
                lambda db: [dict(row) for row in db.execute("SELECT id,status,attempts FROM inbox")],
                write=False,
            )
            if len(rows) == len(ids) and all(row["status"] != "pending" for row in rows):
                return {row["id"]: row for row in rows}
            await asyncio.sleep(0.01)


@pytest.mark.parametrize("committed", [False, True])
async def test_ack_storage_fault_does_not_reinvoke_successful_handler(tmp_path, committed):
    client = Client(Session(15, "synthetic"), data_dir=tmp_path, config=Config(queue_size=2))
    client.account, client._active = "a", True
    calls, failures = [], 0
    real_ack = client.store.ack

    async def ack(*args):
        nonlocal failures
        if failures == 0:
            failures += 1
            if committed:
                await real_ack(*args)
            raise sqlite3.OperationalError("synthetic commit failure")
        return await real_ack(*args)

    client.store.ack = ack

    @client.router.on("new")
    async def handler(event):
        calls.append(event.message.rid)

    try:
        ids = [await seed(client, rid) for rid in (1, 2)]
        client.start_handlers()
        rows = await settled(client, ids)
        assert calls == [1, 2]
        assert all(row["status"] == "acked" and row["attempts"] == 0 for row in rows.values())
    finally:
        await client.close()


@pytest.mark.parametrize("committed", [False, True])
async def test_failed_handler_storage_fault_keeps_worker_and_peer_order(tmp_path, committed):
    client = Client(
        Session(15, "synthetic"), data_dir=tmp_path, config=Config(queue_size=2, handler_attempts=2)
    )
    client.account, client._active = "a", True
    calls, failures = [], 0
    real_fail = client.store.fail_event

    async def fail(*args, **kwargs):
        nonlocal failures
        if failures == 0:
            failures += 1
            if committed:
                await real_fail(*args, **kwargs)
            raise sqlite3.OperationalError("synthetic failure-counter commit fault")
        return await real_fail(*args, **kwargs)

    client.store.fail_event = fail

    @client.router.on("new")
    async def handler(event):
        calls.append(event.message.rid)
        if event.message.rid == 1:
            raise ValueError("application failure")

    try:
        ids = [await seed(client, rid) for rid in (1, 2)]
        client.start_handlers()
        rows = await settled(client, ids)
        assert calls == [1, 1, 2]
        assert rows[ids[0]]["status"] == "quarantine" and rows[ids[0]]["attempts"] == 2
        assert rows[ids[1]]["status"] == "acked"
        assert not client._handler_task.done()
    finally:
        await client.close()


async def test_application_cancelled_future_is_a_bounded_handler_failure(tmp_path):
    client = Client(
        Session(15, "synthetic"), data_dir=tmp_path, config=Config(queue_size=2, handler_attempts=2)
    )
    client.account, client._active = "a", True
    calls = []

    @client.router.on("new")
    async def handler(event):
        calls.append(event.message.rid)
        if event.message.rid == 1:
            future = asyncio.get_running_loop().create_future()
            future.cancel()
            await future

    try:
        ids = [await seed(client, rid) for rid in (1, 2)]
        client.start_handlers()
        rows = await settled(client, ids)
        assert calls == [1, 1, 2]
        assert rows[ids[0]]["status"] == "quarantine" and rows[ids[1]]["status"] == "acked"
        assert not client._handler_task.done()
    finally:
        await client.close()


async def test_manual_ack_then_handler_error_does_not_resurrect_event(tmp_path):
    client = Client(Session(15, "synthetic"), data_dir=tmp_path)
    client.account, client._active = "a", True
    calls = []

    @client.router.on("new")
    async def handler(event):
        calls.append(event.event_id)
        await event.ack()
        raise ValueError("failed after explicit application acknowledgement")

    try:
        event_id = await seed(client, 1)
        client.start_handlers()
        await settled(client, [event_id])
        async with asyncio.timeout(3):
            while client._leased_events:
                await asyncio.sleep(0.01)
        assert calls == [event_id]
        assert await client.store.fail_event("a", event_id, 3) == {"status": "acked", "attempts": 0}
    finally:
        await client.close()


async def test_failed_event_inspection_replay_is_account_local_and_bounded(tmp_path):
    client = Client(Session(15, "synthetic"), data_dir=tmp_path)
    client.account = "a"
    try:
        ids = [await seed(client, rid) for rid in range(5)]
        for event_id in ids:
            await client.store.fail_event("a", event_id, 1)
        await client.store.record("other", b"", [("unknown", "unknown_decode", b"\xff", None)])
        await client.store.run(
            lambda db: db.execute("UPDATE inbox SET status='quarantine' WHERE account='other'")
        )
        snapshots = [event async for event in client.iter_failed_events(page_size=2)]
        assert [event.event_id for event in snapshots] == ids
        assert [event.message.rid for event in snapshots] == list(range(5))
        assert all(event.handler_failures == 1 for event in snapshots)
        assert not client._leased_events and not client._event_consumer
        assert len([event async for event in client.iter_failed_events(page_size=2, limit=3)]) == 3
        assert not [event async for event in client.iter_failed_events(limit=0)]
        for kwargs in ({"page_size": 0}, {"page_size": 1001}, {"limit": -1}):
            with pytest.raises(ValueError):
                _ = [event async for event in client.iter_failed_events(**kwargs)]
        await snapshots[0].ack()  # Explicitly discard this failed event.
        assert await client.replay_event(ids[1])
        assert not await client.replay_event(ids[0])
        assert [event.event_id async for event in client.iter_failed_events(page_size=1)] == ids[2:]
        assert (await client.store.pending_events("a"))[0]["id"] == ids[1]
    finally:
        await client.close()


async def test_lower_retry_limit_quarantines_existing_failures_without_erasing_count(tmp_path):
    client = Client(Session(15, "synthetic"), data_dir=tmp_path, config=Config(handler_attempts=1))
    client.account, client._active = "a", True
    calls = []

    @client.router.on("new")
    async def handler(event):
        calls.append(event.event_id)

    try:
        event_id = await seed(client, 1)
        await client.store.fail_event("a", event_id, 3)
        await client.store.fail_event("a", event_id, 3)
        client.start_handlers()
        rows = await settled(client, [event_id])
        assert not calls and rows[event_id] == {"id": event_id, "status": "quarantine", "attempts": 2}
    finally:
        await client.close()


async def test_handler_failure_budget_survives_restart(tmp_path):
    client = Client(Session(15, "synthetic"), data_dir=tmp_path, config=Config(handler_attempts=3))
    client.account = "a"
    event_id = await seed(client, 1)
    for _ in range(2):
        await client.store.fail_event("a", event_id, 3)
    await client.close()
    client = Client(Session(15, "synthetic"), data_dir=tmp_path, config=Config(handler_attempts=3))
    client.account, client._active = "a", True
    calls = []

    @client.router.on("new")
    async def handler(event):
        calls.append(event.event_id)
        raise ValueError("application failure after restart")

    try:
        client.start_handlers()
        rows = await settled(client, [event_id])
        await asyncio.sleep(0.3)
        assert calls == [event_id]
        assert rows[event_id]["attempts"] == 3
        assert await client.store.replay_event("a", event_id)
        rows = await settled(client, [event_id])
        assert calls == [event_id] * 4 and rows[event_id]["attempts"] == 3
    finally:
        await client.close()
