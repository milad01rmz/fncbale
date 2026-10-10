import asyncio
import time
from types import SimpleNamespace

import pytest

from fncbale import AccountPool, Config, Session, contract
from fncbale.errors import RpcError
from fncbale.storage import Store


async def test_account_rate_gate_survives_restart_and_does_not_hold_global_rpc_slots(tmp_path):
    pool = AccountPool(data_dir=tmp_path, config=Config(global_rpc_limit=1))
    a, b = pool.add("a", Session(1, "synthetic")), pool.add("b", Session(2, "synthetic"))
    a.account, b.account = "a", "b"
    calls = []

    async def request(service, method, payload):
        calls.append(payload)
        return payload

    a._ws = b._ws = SimpleNamespace(request=request)
    try:
        await pool.store.limit_account("a", 0.2)
        waiting = asyncio.create_task(a.invoke_raw("s", "read", b"a", retry_policy="none"))
        await asyncio.sleep(0.01)
        assert await asyncio.wait_for(b.invoke_raw("s", "read", b"b", retry_policy="none"), 0.1) == b"b"
        assert not waiting.done() and calls == [b"b"]
        assert await asyncio.wait_for(waiting, 1) == b"a"
        await pool.store.limit_account("a", 1)
        deadline = pool.store.rate_deadline("a")
    finally:
        a._ws = b._ws = None
        await pool.close()
    store = Store(tmp_path / "pool.sqlite3")
    try:
        await store.start()
        assert store.rate_deadline("a") == deadline > time.time()
    finally:
        await store.close()


async def test_read_rpc_rate_rejection_is_shared_with_other_methods(tmp_path):
    pool = AccountPool(data_dir=tmp_path)
    client = pool.add("a", Session(1, "synthetic"))
    client.account = "a"
    calls = []

    async def request(service, method, payload):
        calls.append((method, time.time()))
        if len(calls) == 1:
            raise RpcError(8, method, retry_after=0.15)
        return contract(method).response().SerializeToString()

    client._ws = SimpleNamespace(request=request)
    try:
        with pytest.raises(RpcError):
            await client._call_bytes("GetRoutesStates", b"", "websocket")
        await client._call_bytes("GetRoutesStates", b"", "websocket")
        assert calls[1][1] - calls[0][1] >= 0.15
    finally:
        client._ws = None
        await pool.close()


async def test_cancelled_deadline_waiter_still_updates_committed_gate(tmp_path):
    store = Store(tmp_path / "db", commit_window=0.04)
    await store.start()
    task = asyncio.create_task(store.limit_account("a", 60))
    try:
        # Cancel after admission, then await actual commit completion. A fixed
        # 70-ms sleep did not establish completion of a Windows FULL commit.
        async with asyncio.timeout(3):
            while not store._queue._unfinished_tasks:
                await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        await asyncio.wait_for(store._queue.join(), 3)
        deadline = store.rate_deadline("a")
        assert deadline > time.time()
        assert (
            await store.run(
                lambda db: db.execute("SELECT not_before FROM account_limits WHERE account='a'").fetchone()[
                    0
                ],
                write=False,
            )
            == deadline
        )
    finally:
        await store.close()


async def test_cancelled_close_waiter_cannot_cancel_store_writer(tmp_path):
    store = Store(tmp_path / "db", commit_window=0.06)
    await store.start()
    accepting = asyncio.create_task(store.enqueue("a", "p", "SendMessage", b"frozen", "{}"))
    async with asyncio.timeout(2):
        while not store._queue._unfinished_tasks:
            await asyncio.sleep(0)
    closing = asyncio.create_task(store.close())
    await asyncio.sleep(0)
    closing.cancel()
    with pytest.raises(asyncio.CancelledError):
        await closing
    operation = await accepting
    await store.close()
    reopened = Store(tmp_path / "db")
    try:
        assert (await reopened.operation("a", operation))["payload"] == b"frozen"
    finally:
        await reopened.close()
