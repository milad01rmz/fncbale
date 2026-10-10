import asyncio
import threading

import pytest
from google.protobuf.message import DecodeError

from fncbale import Client, Config, Session
from fncbale.events import journal_events
from fncbale.proto.struct_pb2 import WebUpdate
from fncbale.storage import Store


def update(rid=1):
    value = WebUpdate()
    value.message.peer.type, value.message.peer.id = 1, 10
    value.message.rid, value.message.date = rid, rid
    return value


async def record(store, account="a", rid=1):
    value = update(rid)
    return await store.record(account, value.SerializeToString(), journal_events(value))


async def test_idle_consumer_does_not_scan_sqlite_twenty_times_per_second(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path, config=Config(queue_size=2))
    client.account, client._active = "a", True
    original = client.store.pending_events
    calls = []
    entered = asyncio.Event()

    async def pending(*args, **kwargs):
        calls.append(True)
        result = await original(*args, **kwargs)
        entered.set()
        return result

    client.store.pending_events = pending
    iterator = client.events()
    task = asyncio.create_task(anext(iterator))
    try:
        await asyncio.wait_for(entered.wait(), 1)
        await asyncio.sleep(0.35)
        assert len(calls) <= 2, "Empty inbox still polls SQLite at20Hz"
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        await iterator.aclose()
        await client.close()


async def test_cancelled_record_waiter_notifies_only_origin_account_after_commit(tmp_path):
    store = Store(tmp_path / "state.sqlite3")
    wake_a, wake_b = asyncio.Event(), asyncio.Event()
    store._watch_inbox("a", wake_a)
    store._watch_inbox("b", wake_b)
    entered, release = threading.Event(), threading.Event()
    await store.start()

    def held(db):
        entered.set()
        assert release.wait(3)

    blocker = asyncio.create_task(store.run(held, write=False))
    writing = None
    try:
        assert await asyncio.to_thread(entered.wait, 1)
        writing = asyncio.create_task(record(store))
        async with asyncio.timeout(1):
            while store._queue.empty():
                await asyncio.sleep(0)
        writing.cancel()
        with pytest.raises(asyncio.CancelledError):
            await writing
        assert not wake_a.is_set() and not wake_b.is_set()
        release.set()
        await blocker
        await asyncio.wait_for(wake_a.wait(), 1)
        assert not wake_b.is_set()
        rows = await store.pending_events("a")
        assert len(rows) == 1 and WebUpdate.FromString(rows[0]["raw"]).message.rid == 1
        store._unwatch_inbox("a", wake_a)
        assert "a" not in store._inbox_watchers and "b" in store._inbox_watchers
    finally:
        release.set()
        await asyncio.gather(blocker, *([writing] if writing else []), return_exceptions=True)
        await store.close()
    assert wake_b.is_set() and not store._inbox_watchers


async def test_rolled_back_record_does_not_signal_or_deliver_inbox(tmp_path):
    store = Store(tmp_path / "state.sqlite3")
    wake = asyncio.Event()
    store._watch_inbox("a", wake)
    try:
        with pytest.raises(DecodeError):
            await store.record("a", b"invalid", [("p", "new", b"\xff", None)])
        assert not wake.is_set() and await store.pending_events("a") == []
    finally:
        await store.close()


async def test_commit_between_empty_scan_and_wait_cannot_lose_notification(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    client.account, client._active = "a", True
    original = client.store.pending_events
    first = True

    async def pending(*args, **kwargs):
        nonlocal first
        rows = await original(*args, **kwargs)
        if first:
            first = False
            assert not rows
            await record(client.store)
        return rows

    client.store.pending_events = pending
    iterator = client.events()
    try:
        event = await asyncio.wait_for(anext(iterator), 0.2)
        assert event.message.rid == 1
        await event.ack()
    finally:
        await iterator.aclose()
        await client.close()


async def test_ack_releases_full_delivery_capacity_without_waiting_for_safety_scan(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path, config=Config(queue_size=1))
    client.account, client._active = "a", True
    await record(client.store, rid=1)
    await record(client.store, rid=2)
    iterator = client.events()
    second = None
    try:
        first = await anext(iterator)
        second = asyncio.create_task(anext(iterator))
        await asyncio.sleep(0.02)
        assert not second.done()
        await first.ack()
        event = await asyncio.wait_for(second, 0.2)
        assert event.message.rid == 2
        await event.ack()
    finally:
        if second:
            second.cancel()
            await asyncio.gather(second, return_exceptions=True)
        await iterator.aclose()
        await client.close()


async def test_old_iterator_cannot_unsubscribe_new_consumer_after_disconnect(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    client.account, client._active = "a", True
    await record(client.store)
    old, new = client.events(), client.events()
    try:
        first = await anext(old)
        old_wake = client._inbox_wake
        await client.disconnect()
        assert not client.store._inbox_watchers and old_wake.is_set()
        client._active = True
        replayed = await anext(new)
        assert replayed.event_id == first.event_id
        new_wake = client._inbox_wake
        await old.aclose()
        assert client.store._inbox_watchers == {"a": {new_wake}}
        await replayed.ack()
        await new.aclose()
        assert not client.store._inbox_watchers
    finally:
        await old.aclose()
        await new.aclose()
        await client.close()


async def test_quarantine_replay_wakes_idle_original_event_id(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    client.account, client._active = "a", True
    event_id = (await record(client.store))[0]
    await client.store.fail_event("a", event_id, 1)
    entered = asyncio.Event()
    original = client.store.pending_events

    async def pending(*args, **kwargs):
        result = await original(*args, **kwargs)
        entered.set()
        return result

    client.store.pending_events = pending
    iterator = client.events()
    task = asyncio.create_task(anext(iterator))
    try:
        await asyncio.wait_for(entered.wait(), 1)
        assert await client.replay_event(event_id)
        event = await asyncio.wait_for(task, 0.2)
        assert event.event_id == event_id
        await event.ack()
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        await iterator.aclose()
        await client.close()
