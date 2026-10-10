import asyncio
import threading
import uuid

import pytest

from fncbale import Client, Config, ProtocolProfile, Session
from fncbale.errors import ClientClosed, SessionInUse
from fncbale.session import AccountLock
from fncbale.transports import WebSocketTransport


def client_for(tmp_path):
    profile = ProtocolProfile(grpc_url=f"https://synthetic-{uuid.uuid4().hex}.invalid")
    return Client(Session(60606012, "synthetic"), config=Config(profile=profile), data_dir=tmp_path)


class Socket:
    async def close(self):
        pass


async def no_recovery(client):
    pass


async def test_close_serializes_with_connection_in_progress(tmp_path, monkeypatch):
    entered, release = asyncio.Event(), asyncio.Event()

    async def connect(transport):
        entered.set()
        await release.wait()
        transport.socket = Socket()
        transport.disconnected.clear()

    monkeypatch.setattr(WebSocketTransport, "connect", connect)
    monkeypatch.setattr(Client, "recover", no_recovery)
    monkeypatch.setattr(Client, "_bootstrap_routes", no_recovery)
    client = client_for(tmp_path)
    connecting = asyncio.create_task(client.connect())
    await entered.wait()
    closing = asyncio.create_task(client.close())
    await asyncio.sleep(0)
    release.set()
    await asyncio.wait_for(asyncio.gather(connecting, closing), 5)
    assert client._closed and not client.connected and client._lock is None
    assert client.store._closed and not client._tasks
    with pytest.raises(ClientClosed):
        await client.connect()


async def test_cancel_close_waiter_still_finishes_cleanup(tmp_path):
    client = client_for(tmp_path)
    entered, release = asyncio.Event(), asyncio.Event()
    original = client._grpc.close

    async def close():
        entered.set()
        await release.wait()
        await original()

    client._grpc.close = close
    waiter = asyncio.create_task(client.close())
    await entered.wait()
    waiter.cancel()
    with pytest.raises(asyncio.CancelledError):
        await waiter
    with pytest.raises(ClientClosed):
        await client.connect()
    release.set()
    await asyncio.wait_for(client.close(), 5)
    assert client._closed and client.store._closed


async def test_cancel_disconnect_waiter_does_not_repeat_or_abandon_socket_cleanup(tmp_path):
    client = client_for(tmp_path)
    entered, release = asyncio.Event(), asyncio.Event()
    calls = []

    class ClosingSocket:
        async def close(self):
            calls.append(True)
            entered.set()
            await release.wait()

    client._ws, client._active = ClosingSocket(), True
    first, second = asyncio.create_task(client.disconnect()), None
    try:
        await asyncio.wait_for(entered.wait(), 2)
        first.cancel()
        with pytest.raises(asyncio.CancelledError):
            await first
        second = asyncio.create_task(client.disconnect())
        await asyncio.sleep(0.05)
        assert len(calls) == 1 and not second.done()
        release.set()
        await asyncio.wait_for(second, 2)
        assert not client._active and not client._tasks
    finally:
        release.set()
        await asyncio.gather(first, *([second] if second else []), return_exceptions=True)
        await client.close()


async def test_reconnect_waits_for_disconnect_and_cancelled_connect_does_not_abort_it(tmp_path, monkeypatch):
    client = client_for(tmp_path)
    entered, release, network = asyncio.Event(), asyncio.Event(), asyncio.Event()

    class ClosingSocket:
        async def close(self):
            entered.set()
            await release.wait()

    async def connect(transport):
        network.set()
        transport.socket = Socket()
        transport.disconnected.clear()

    monkeypatch.setattr(WebSocketTransport, "connect", connect)
    monkeypatch.setattr(Client, "recover", no_recovery)
    monkeypatch.setattr(Client, "_bootstrap_routes", no_recovery)
    client._ws, client._active = ClosingSocket(), True
    stopping = asyncio.create_task(client.disconnect())
    connecting, restarted = None, None
    try:
        await asyncio.wait_for(entered.wait(), 2)
        connecting = asyncio.create_task(client.connect())
        await asyncio.sleep(0.05)
        assert not network.is_set() and not connecting.done()
        connecting.cancel()
        with pytest.raises(asyncio.CancelledError):
            await connecting
        assert not stopping.done()
        restarted = asyncio.create_task(client.connect())
        release.set()
        await asyncio.wait_for(asyncio.gather(stopping, restarted), 3)
        assert network.is_set() and client.connected
    finally:
        release.set()
        await asyncio.gather(
            stopping,
            *([connecting] if connecting else []),
            *([restarted] if restarted else []),
            return_exceptions=True,
        )
        await client.close()


async def test_cancel_during_account_lock_acquisition_releases_native_lock(tmp_path, monkeypatch):
    entered, release = threading.Event(), threading.Event()
    locks = []
    original = AccountLock.acquire

    def acquire(lock):
        original(lock)
        locks.append(lock)
        entered.set()
        assert release.wait(5)

    monkeypatch.setattr(AccountLock, "acquire", acquire)
    client = client_for(tmp_path)
    connecting = asyncio.create_task(client.connect())
    try:
        assert await asyncio.to_thread(entered.wait, 5)
        connecting.cancel()
        await asyncio.sleep(0.01)
        assert not connecting.done()
        release.set()
        with pytest.raises(asyncio.CancelledError):
            await connecting
        assert client._lock is None and locks[0].stream is None
        contender = AccountLock(locks[0].path)
        original(contender)
        contender.release()
    finally:
        release.set()
        await client.close()


async def test_failed_account_acquire_cannot_bypass_lock_on_reconnect(tmp_path, monkeypatch):
    import hashlib
    from pathlib import Path

    client = client_for(tmp_path)
    key = hashlib.sha256(client.config.profile.grpc_url.encode()).hexdigest()[:12]
    owner = AccountLock(Path.home() / ".cache/fncbale/locks" / f"{key}-{client.session.user_id}.lock")
    owner.acquire()
    try:
        for _ in range(2):
            with pytest.raises(SessionInUse):
                await client.connect()
            assert client._lock is None
    finally:
        owner.release()
        await client.close()


async def test_closing_rejects_cached_peer_writes_before_commit_or_media_io(tmp_path):
    from fncbale import Media, MediaKind, Peer, PeerKind

    client = client_for(tmp_path)
    client.account, client._active = "closing", True
    await client.store.start()
    entered, release = asyncio.Event(), asyncio.Event()
    original = client._disconnect_unlocked

    async def slow_disconnect():
        entered.set()
        await release.wait()
        await original()

    async def unexpected_prepare(*_):
        pytest.fail("Closing must reject before media I/O")

    client._disconnect_unlocked, client.media.prepare = slow_disconnect, unexpected_prepare
    closing = asyncio.create_task(client.close())
    try:
        await entered.wait()
        assert client._closing and client._active
        peer = Peer(PeerKind.USER, 10)
        with pytest.raises(ClientClosed):
            await client.enqueue_message(peer, "late write")
        media = Media(b"synthetic", MediaKind.PHOTO)
        with pytest.raises(ClientClosed):
            await client.enqueue_media(peer, media)
        with pytest.raises(ClientClosed):
            await client.enqueue_album(peer, [media, media])
        assert (
            await client.store.run(
                lambda db: db.execute("SELECT count(*) FROM operations").fetchone()[0], write=False
            )
            == 0
        )
    finally:
        release.set()
        await closing
