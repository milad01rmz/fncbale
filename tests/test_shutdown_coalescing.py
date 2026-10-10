import asyncio

import pytest

from fncbale import AccountPool, Client, Session


async def test_disconnect_after_permanent_close_does_not_start_new_cleanup(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    calls = []

    class Socket:
        async def close(self):
            calls.append(client._closed)

    client._ws = Socket()
    await client.close()
    await client.disconnect()
    assert calls == [False], "disconnect ran network cleanup after permanent close"
    assert client._disconnect_task is None


@pytest.mark.parametrize("pooled", [False, True])
async def test_cancel_disconnect_joined_to_close_cannot_leave_cleanup_after_store_close(tmp_path, pooled):
    pool = AccountPool(data_dir=tmp_path) if pooled else None
    client = (
        pool.add("one", Session(1, "synthetic"))
        if pool
        else Client(Session(1, "synthetic"), data_dir=tmp_path)
    )
    client.account, client._active = "a", True
    operation_id = await client.store.enqueue("a", "p", "SendMessage", b"frozen", "{}")
    entered, release = asyncio.Event(), asyncio.Event()
    calls = []

    class Socket:
        async def close(self):
            calls.append(client._closed)
            entered.set()
            await release.wait()

    client._ws = Socket()
    closing = asyncio.create_task(pool.close() if pool else client.close())
    joined = None
    try:
        await asyncio.wait_for(entered.wait(), 2)
        joined = asyncio.create_task(client.disconnect())
        await asyncio.sleep(0.05)
        joined.cancel()
        with pytest.raises(asyncio.CancelledError):
            await joined
        assert not closing.done()
        release.set()
        await asyncio.wait_for(closing, 2)
        await asyncio.sleep(0)
        if client._disconnect_task is not None:
            await asyncio.wait_for(client._disconnect_task, 2)
        assert calls == [False] and client._closed and client.store._closed
        assert client._disconnect_task is None
        reopened = (
            AccountPool(data_dir=tmp_path) if pooled else Client(Session(1, "synthetic"), data_dir=tmp_path)
        )
        try:
            row = await reopened.store.operation("a", operation_id)
            assert row["status"] == "queued" and bytes(row["payload"]) == b"frozen"
        finally:
            await reopened.close()
    finally:
        release.set()
        await asyncio.gather(closing, *([joined] if joined else []), return_exceptions=True)
        await (pool.close() if pool else client.close())


async def test_disconnect_after_failed_close_preserves_original_cleanup_error(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)

    async def failed_close():
        raise RuntimeError("modeled transport cleanup failure")

    client._grpc.close = failed_close
    with pytest.raises(ExceptionGroup) as first:
        await client.close()
    assert client._closed and client.store._closed
    with pytest.raises(ExceptionGroup) as joined:
        await client.disconnect()
    assert joined.value is first.value and client._disconnect_task is None


@pytest.mark.parametrize("failed", [False, True])
async def test_previously_queued_disconnect_does_not_run_after_close(tmp_path, monkeypatch, failed):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    entered, release = asyncio.Event(), asyncio.Event()
    calls = []
    original = client._disconnect_once

    async def paused():
        entered.set()
        await release.wait()
        await original()

    class Socket:
        async def close(self):
            calls.append(client._closed)

    async def failure():
        raise RuntimeError("modeled permanent-close failure")

    monkeypatch.setattr(client, "_disconnect_once", paused)
    client._ws = Socket()
    if failed:
        client._grpc.close = failure
    waiter = asyncio.create_task(client.disconnect())
    error = None
    try:
        await asyncio.wait_for(entered.wait(), 2)
        try:
            await client.close()
        except ExceptionGroup as exc:
            error = exc
        assert bool(error) == failed and client._closed
        release.set()
        result = (await asyncio.gather(waiter, return_exceptions=True))[0]
        assert result is error and calls == [False]
    finally:
        release.set()
        await asyncio.gather(waiter, return_exceptions=True)
        await asyncio.gather(client.close(), return_exceptions=True)
