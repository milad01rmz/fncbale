import asyncio

import pytest

from fncbale.errors import IdempotencyConflict, SessionInUse
from fncbale.session import AccountLock
from fncbale.storage import Store


async def test_commit_reopen_and_crash_state(tmp_path):
    store = Store(tmp_path / "db")
    first = await store.enqueue("a", "p", "SendMessage", b"frozen", "{}", "key")
    assert await store.enqueue("a", "p", "SendMessage", b"frozen", "{}", "key") == first
    with pytest.raises(IdempotencyConflict):
        await store.enqueue("a", "p", "SendMessage", b"changed", "{}", "key")
    claimed = await store.claim("a")
    assert claimed["id"] == first
    await store.attempted("a", first)
    await store.close()
    reopened = Store(tmp_path / "db")
    await reopened.recover_operations("a")
    assert (await reopened.operation("a", first))["status"] == "uncertain"
    next_id = await reopened.enqueue("a", "p", "SendMessage", b"next", "{}")
    assert await reopened.claim("a") is None  # uncertain predecessor blocks only its peer
    other = await reopened.enqueue("a", "q", "SendMessage", b"other", "{}")
    assert (await reopened.claim("a"))["id"] == other
    assert await reopened.cancel_unsent("a", next_id)
    await reopened.close()


async def test_inbox_checkpoint_atomic_dedupe_and_retention(tmp_path):
    store = Store(tmp_path / "db")
    from fncbale.proto.struct_pb2 import WebUpdate

    update = WebUpdate()
    update.message.rid = 1
    event = ("p", "new", update.SerializeToString(), "identity")
    ids = await store.record("a", b"journal", [event], [("r", b"state", 4)])
    assert len(ids) == 1
    assert not await store.record("a", b"repeat", [event], [("r", b"older", 3)])
    assert (await store.routes("a"))[0]["state"] == b"state"
    assert len(await store.pending_events("a")) == 1
    await store.fail_event("a", ids[0], 1)
    assert not await store.pending_events("a")
    assert await store.replay_event("a", ids[0])
    await store.ack("a", ids[0])
    assert not await store.pending_events("a")
    await store.close()


async def test_group_commit_one_error_does_not_rollback_other_callers(tmp_path):
    store = Store(tmp_path / "db", commit_window=0.01)
    good = asyncio.create_task(store.enqueue("a", "p", "SendMessage", b"x", "{}"))
    bad = asyncio.create_task(store.run(lambda db: db.execute("INSERT INTO nonexistent VALUES(1)")))
    result = await asyncio.gather(good, bad, return_exceptions=True)
    assert isinstance(result[0], str)
    assert isinstance(result[1], Exception)
    assert (await store.operation("a", result[0]))["payload"] == b"x"
    await store.close()


async def test_cancel_waiter_does_not_cancel_commit(tmp_path):
    store = Store(tmp_path / "db", commit_window=0.03)
    task = asyncio.create_task(store.enqueue("a", "p", "SendMessage", b"x", "{}", "one"))
    await asyncio.sleep(0.01)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    await asyncio.sleep(0.05)
    same = await store.enqueue("a", "p", "SendMessage", b"x", "{}", "one")
    assert (await store.operation("a", same))["status"] == "queued"
    await store.close()


def test_account_lock(tmp_path):
    one, two = AccountLock(tmp_path / "lock"), AccountLock(tmp_path / "lock")
    one.acquire()
    with pytest.raises(SessionInUse):
        two.acquire()
    one.release()
    two.acquire()
    two.release()


async def test_durable_deadline_budget_account_isolation_and_confirmation_fence(tmp_path, monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr("fncbale.storage.time.time", lambda: clock[0])
    store = Store(tmp_path / "db")
    try:
        one = await store.enqueue("a", "p", "SendMessage", b"one", "{}")
        await store.enqueue("a", "q", "SendMessage", b"two", "{}")
        other = await store.enqueue("b", "p", "SendMessage", b"other", "{}")
        assert (await store.claim("a"))["id"] == one
        assert await store.attempted("a", one) == 1
        await store.reschedule("a", one, delay=60, account_wait=True)
        assert await store.claim("a") is None
        assert (await store.claim("b"))["id"] == other
        clock[0] += 60
        assert (await store.claim("a"))["cycle_attempts"] == 1
        assert await store.attempted("a", one) == 2
        await store.reschedule("a", one)
        await store.claim("a")
        assert await store.attempted("a", one) == 3
        await store.reschedule("a", one)
        assert (await store.operation("a", one))["status"] == "failed"
        assert await store.retry("a", one)
        await store.claim("a")
        assert await store.attempted("a", one) == 1
        await store.finish("a", one, "confirmed", response=b"ack")
        await store.finish("a", one, "uncertain", error="late worker")
        assert not await store.retry("a", one, allow_uncertain=True)
        assert (await store.operation("a", one))["response"] == b"ack"
    finally:
        await store.close()


async def test_schema_one_migration_is_conservative(tmp_path):
    import sqlite3

    database = tmp_path / "db"
    with sqlite3.connect(database) as db:
        db.executescript("""
            CREATE TABLE operations (
              id TEXT PRIMARY KEY, account TEXT, peer TEXT, method TEXT, payload BLOB,
              digest TEXT, idem TEXT, context TEXT, status TEXT, attempts INTEGER,
              response BLOB, error TEXT, created REAL, updated REAL, UNIQUE(account,idem));
            INSERT INTO operations VALUES('old','a','p','SendMessage',X'01','d',NULL,'{}',
              'running',2,NULL,NULL,1,1);
            PRAGMA user_version=1;
        """)
    store = Store(database)
    try:
        await store.recover_operations("a")
        row = await store.operation("a", "old")
        assert row["status"] == "uncertain" and row["cycle_attempts"] == 2
        assert await store.run(lambda db: db.execute("PRAGMA user_version").fetchone()[0], write=False) == 3
    finally:
        await store.close()


async def test_sqlite_full_does_not_accept_partial_inbox_or_checkpoint(tmp_path):
    import sqlite3
    from fncbale.errors import StorageError

    store = Store(tmp_path / "db")
    try:
        await store.start()
        await store.run(
            lambda db: db.execute(
                f"PRAGMA max_page_count={db.execute('PRAGMA page_count').fetchone()[0]}"
            ).fetchone()
        )
        with pytest.raises((StorageError, sqlite3.Error)):
            await store.record(
                "a",
                b"x" * (1024 * 1024),
                [("p", "unknown", b"event", "one")],
                [("global", b"checkpoint", 42)],
            )
        assert not await store.pending_events("a") and not await store.routes("a")
        # Writer remains usable after SQLite rolls back a FULL transaction.
        await store.run(lambda db: db.execute("PRAGMA max_page_count=100000").fetchone())
        assert len(await store.record("a", b"x", [("p", "unknown", b"event", "one")])) == 1
    finally:
        await store.close()


async def test_spool_retention_keeps_uncertain_waiting_and_active_preparations(tmp_path):
    import json
    import os
    import time

    store = Store(tmp_path / "db")
    spool = tmp_path / "spool"
    spool.mkdir()
    paths = []
    old = time.time() - 8 * 86400
    for n in range(7):
        path = spool / (f"{n:032x}.media")
        path.write_bytes(b"content")
        os.utime(path, (old, old))
        paths.append(path)
    # Unknown names and unregistered folders are never scanned for orphans.
    unknown = spool / "user-document.media"
    unknown.write_bytes(b"owned by user")
    os.utime(unknown, (old, old))
    outside = tmp_path / "other"
    outside.mkdir()
    (outside / paths[0].name).write_bytes(b"keep")
    leased, another_owner = {paths[4].resolve()}, {paths[5].resolve()}
    store.register_spool(spool, leased)
    store.register_spool(spool, another_owner)
    os.utime(paths[6], None)  # young orphan
    try:
        for index, status in [(1, "uncertain"), (2, "waiting"), (3, "confirmed")]:
            operation = await store.enqueue(
                "a",
                str(index),
                "SendMessage",
                b"frozen",
                json.dumps({"media": [{"path": str(paths[index])}]}),
            )
            await store.finish("a", operation, status)
        await store.run(lambda db: db.execute("UPDATE operations SET updated=0"))
        assert await store.purge(7) == 2  # abandoned orphan and expired final record
        assert not paths[0].exists() and not paths[3].exists()
        assert all(paths[index].exists() for index in (1, 2, 4, 5, 6))
        assert unknown.exists() and (outside / paths[0].name).exists()
    finally:
        await store.close()


async def test_pool_maintenance_runs_once_for_concurrent_supervisors(tmp_path, monkeypatch):
    import asyncio

    store = Store(tmp_path / "db")
    entered, release = asyncio.Event(), asyncio.Event()
    calls = []

    async def purge(days):
        calls.append(days)
        entered.set()
        await release.wait()

    monkeypatch.setattr(store, "purge", purge)
    store._last_purge = -3601
    tasks = [asyncio.create_task(store.maintain(7)) for _ in range(100)]
    try:
        await asyncio.wait_for(entered.wait(), 3)
        # Independent supervisors have all had a chance to enter the same pass.
        await asyncio.sleep(0)
        release.set()
        await asyncio.gather(*tasks)
        assert calls == [7]
        await store.maintain(7)
        assert calls == [7]
    finally:
        release.set()
        await asyncio.gather(*tasks, return_exceptions=True)
        await store.close()


@pytest.mark.parametrize("mode", ["error", "cancel"])
async def test_failed_maintenance_releases_gate_without_advancing_schedule(tmp_path, monkeypatch, mode):
    import asyncio
    from fncbale.errors import StorageError

    store = Store(tmp_path / "db")
    entered = asyncio.Event()
    calls = []
    initial = store._last_purge = -3601

    async def purge(days):
        calls.append(days)
        if len(calls) == 1:
            entered.set()
            if mode == "cancel":
                await asyncio.Event().wait()
            raise StorageError("modeled purge failure")

    monkeypatch.setattr(store, "purge", purge)
    first = asyncio.create_task(store.maintain(7))
    try:
        await asyncio.wait_for(entered.wait(), 3)
        if mode == "cancel":
            first.cancel()
        with pytest.raises(asyncio.CancelledError if mode == "cancel" else StorageError):
            await first
        assert store._last_purge == initial
        await asyncio.wait_for(store.maintain(7), 3)
        assert store._last_purge > initial and calls == [7, 7]
        await store.maintain(7)
        assert calls == [7, 7]
    finally:
        first.cancel()
        await asyncio.gather(first, return_exceptions=True)
        await store.close()
