import asyncio

import pytest

from fncbale import Config
from fncbale.errors import TransportError
from fncbale.transports import WebSocketTransport


class Socket:
    def __init__(self):
        self.started = asyncio.Event()
        self.closed = False
        self.sends = 0

    async def send(self, raw):
        self.sends += 1
        self.started.set()
        await asyncio.Event().wait()

    async def close(self):
        self.closed = True


async def test_blocked_web_handshake_obeys_rpc_deadline(monkeypatch):
    socket = Socket()

    async def opened(*args, **kwargs):
        return socket

    monkeypatch.setattr("fncbale.transports.connect", opened)
    transport = WebSocketTransport("synthetic", Config(rpc_timeout=0.03))
    try:
        async with asyncio.timeout(0.3):
            with pytest.raises(TransportError):
                await transport.connect()
        assert socket.started.is_set() and socket.closed
        assert not transport.connected and transport.disconnected.is_set()
        assert transport._reader is None and transport._heartbeat is None
    finally:
        await transport.close()


async def test_cancelled_web_handshake_preserves_cancellation_and_closes_socket(monkeypatch):
    socket = Socket()

    async def opened(*args, **kwargs):
        return socket

    monkeypatch.setattr("fncbale.transports.connect", opened)
    transport = WebSocketTransport("synthetic", Config())
    task = asyncio.create_task(transport.connect())
    try:
        await asyncio.wait_for(socket.started.wait(), 1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert socket.closed and not transport.connected and transport.disconnected.is_set()
        assert transport._reader is None and transport._heartbeat is None and transport.pending_count == 0
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        await transport.close()


@pytest.mark.parametrize("blocked_lock", [False, True])
async def test_stalled_heartbeat_releases_transport_and_pending_calls(blocked_lock):
    transport = WebSocketTransport("synthetic", Config(rpc_timeout=0.03))
    socket = Socket()
    transport.socket = socket
    transport.disconnected.clear()
    future = asyncio.get_running_loop().create_future()
    transport._pending[(transport.generation, 1)] = future
    if blocked_lock:
        await transport._send_lock.acquire()
    task = asyncio.create_task(transport._keepalive(socket))
    transport._heartbeat = task
    try:
        async with asyncio.timeout(0.3):
            await asyncio.shield(task)
        assert socket.closed and transport.disconnected.is_set() and not transport.connected
        assert socket.started.is_set() is (not blocked_lock)
        assert transport.pending_count == 0
        with pytest.raises(TransportError) as error:
            await future
        assert error.value.possibly_sent
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        if transport._send_lock.locked():
            transport._send_lock.release()
        if future.done() and not future.cancelled():
            future.exception()
        await transport.close()


async def test_heartbeat_rechecks_socket_identity_after_send_capacity():
    transport = WebSocketTransport("synthetic", Config(rpc_timeout=0.03))
    old, replacement = Socket(), Socket()
    transport.socket = old
    transport.disconnected.clear()
    await transport._send_lock.acquire()
    task = asyncio.create_task(transport._keepalive(old))
    try:
        await asyncio.sleep(0)
        transport.socket = replacement
        transport._send_lock.release()
        async with asyncio.timeout(0.3):
            await asyncio.shield(task)
        assert old.sends == 0 and not replacement.closed and transport.socket is replacement
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        if transport._send_lock.locked():
            transport._send_lock.release()
        await transport.close()
