import asyncio
from pathlib import Path

import pytest

from fncbale import AccountPool, Session
from fncbale.errors import ClientClosed


async def test_portable_names_cannot_escape_or_alias_account_directories(tmp_path):
    pool = AccountPool(data_dir=tmp_path / "pool")
    try:
        for name in ("", ".", "..", "../outside", "a/b", "a\\b", "a:b", "NUL.txt", "COM1", "account "):
            with pytest.raises(ValueError):
                pool.add(name, Session(1, "synthetic"))
        client = pool.add("حساب-۱", Session(1, "synthetic"))
        assert client.data_dir.parent == pool.root
        pool.add("Test", Session(2, "synthetic"))
        with pytest.raises(ValueError):
            pool.add("test", Session(3, "synthetic"))
        assert len(pool.clients) == 2 and not (tmp_path / "outside").exists()
    finally:
        await pool.close()


async def test_symlink_account_directory_is_rejected(tmp_path):
    root, outside = tmp_path / "pool", tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    try:
        (root / "alias").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Symlink creation not permitted on this host")
    pool = AccountPool(data_dir=root)
    try:
        with pytest.raises(ValueError):
            pool.add("alias", Session(1, "synthetic"))
        assert not list(outside.iterdir())
    finally:
        await pool.close()


async def test_cancel_pool_close_waiter_keeps_all_cleanup_running(tmp_path):
    pool = AccountPool(data_dir=tmp_path)
    clients = [pool.add(str(i), Session(i + 1, "synthetic")) for i in range(3)]
    entered, release = asyncio.Event(), asyncio.Event()
    original = clients[0]._grpc.close

    async def slow_close():
        entered.set()
        await release.wait()
        await original()

    clients[0]._grpc.close = slow_close
    waiter = asyncio.create_task(pool.close())
    await entered.wait()
    waiter.cancel()
    with pytest.raises(asyncio.CancelledError):
        await waiter
    with pytest.raises(ClientClosed):
        pool.add("late", Session(9, "synthetic"))
    release.set()
    await asyncio.wait_for(pool.close(), 5)
    assert all(client._closed for client in clients)
    assert pool.store._closed and pool.resources.http.is_closed


async def test_failed_client_cleanup_does_not_abandon_siblings_or_shared_resources(tmp_path):
    pool = AccountPool(data_dir=tmp_path)
    one, two = (pool.add(str(i), Session(i + 1, "synthetic")) for i in range(2))
    original = one._grpc.close

    async def faulty():
        await original()
        raise RuntimeError("synthetic close fault")

    one._grpc.close = faulty
    with pytest.raises(ExceptionGroup):
        await pool.close()
    assert one._closed and two._closed
    assert pool.store._closed and pool.resources.http.is_closed


async def test_close_does_not_delete_persistent_account_data(tmp_path):
    pool = AccountPool(data_dir=tmp_path)
    client = pool.add("a", Session(1, "synthetic"))
    operation = await pool.store.enqueue("a", "p", "SendMessage", b"frozen", "{}")
    await pool.close()
    assert Path(client.data_dir).parent == tmp_path
    from fncbale.storage import Store

    reopened = Store(tmp_path / "pool.sqlite3")
    try:
        assert (await reopened.operation("a", operation))["payload"] == b"frozen"
    finally:
        await reopened.close()
