import asyncio

import pytest
from websockets.asyncio.server import serve

from fncbale import Config, ProtocolProfile
from fncbale.errors import TransportError
from fncbale.proto import request_pb2 as q, response_pb2 as r
from fncbale.transports import WebSocketTransport


class BlockedSocket:
    def __init__(self):
        self.started = asyncio.Event()
        self.closed = False

    async def send(self, payload):
        self.started.set()
        await asyncio.Event().wait()

    async def close(self):
        self.closed = True


@pytest.mark.parametrize("blocked_send", [False, True])
async def test_ws_deadline_covers_send_lock_and_send(blocked_send):
    transport = WebSocketTransport("synthetic", Config(rpc_timeout=0.03))
    socket = BlockedSocket()
    transport.socket = socket
    transport.disconnected.clear()
    if not blocked_send:
        await transport._send_lock.acquire()
    try:
        async with asyncio.timeout(0.5):
            with pytest.raises(TransportError) as error:
                await transport.request("s", "write", b"frozen")
        assert error.value.possibly_sent is blocked_send
        assert socket.started.is_set() is blocked_send
        assert transport.pending_count == 0
        assert socket.closed is blocked_send
        assert transport.connected is (not blocked_send)
    finally:
        if transport._send_lock.locked():
            transport._send_lock.release()
        await transport.close()


async def test_ws_cancel_partial_send_closes_connection():
    transport = WebSocketTransport("synthetic", Config())
    socket = BlockedSocket()
    transport.socket = socket
    transport.disconnected.clear()
    task = asyncio.create_task(transport.request("s", "write", b"frozen"))
    try:
        await asyncio.wait_for(socket.started.wait(), 1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert socket.closed and not transport.connected and transport.disconnected.is_set()
        assert transport.pending_count == 0
    finally:
        await transport.close()


@pytest.mark.parametrize("status", [202, 204, 206, 301, 302, 307, 308])
async def test_grpc_requires_final_http_200_without_redirect(status):
    import httpx
    from fncbale.protocol import grpc_frame
    from fncbale.transports import GrpcTransport

    requests = []

    def respond(request):
        requests.append(request)
        if request.url.path.endswith("redirected"):
            return httpx.Response(200, headers={"grpc-status": "0"}, content=grpc_frame(b"false-success"))
        return httpx.Response(
            status,
            headers={"grpc-status": "0", "location": "/redirected"},
            content=grpc_frame(b"false-success"),
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond), follow_redirects=True) as http:
        transport = GrpcTransport("synthetic", Config(), http)
        with pytest.raises(TransportError) as error:
            await transport.request("s", "write", b"frozen")
        assert error.value.possibly_sent
        assert len(requests) == 1


@pytest.mark.parametrize("stage", ["headers", "body"])
async def test_grpc_deadline_covers_headers_and_stream_body(stage):
    import httpx
    from fncbale.transports import GrpcTransport

    started, closed = asyncio.Event(), asyncio.Event()

    class BlockedBody(httpx.AsyncByteStream):
        async def __aiter__(self):
            started.set()
            await asyncio.Event().wait()
            yield b""

        async def aclose(self):
            closed.set()

    async def respond(request):
        if stage == "headers":
            started.set()
            await asyncio.Event().wait()
        return httpx.Response(200, headers={"grpc-status": "0"}, stream=BlockedBody())

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond), timeout=None) as http:
        transport = GrpcTransport("synthetic", Config(rpc_timeout=0.03), http)
        async with asyncio.timeout(0.5):
            with pytest.raises(TransportError) as error:
                await transport.request("s", "write", b"frozen")
        assert started.is_set() and error.value.possibly_sent
        if stage == "body":
            assert closed.is_set()


async def test_grpc_cookie_jar_cannot_adopt_uncommitted_server_identity():
    import httpx
    from fncbale.protocol import grpc_frame
    from fncbale.transports import GrpcTransport

    cookies = []

    def response(request):
        cookies.append(request.headers.get("cookie"))
        return httpx.Response(
            200,
            headers={"set-cookie": "access_token=synthetic-uncommitted; Path=/", "grpc-status": "0"},
            content=grpc_frame(b""),
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as http:
        transport = GrpcTransport(None, Config(), http=http)
        await transport.request("auth", "validate", b"")
        await transport.request("read", "probe", b"")
        assert not cookies[0] and not cookies[1]
        transport._token = "synthetic-committed"
        await transport.request("read", "probe", b"")
        assert cookies[-1] == "access_token=synthetic-committed"


async def test_ws_correlation_timeout_cancel_and_reconnect():
    async def handler(socket):
        async for raw in socket:
            value = q.Request.FromString(raw)
            if not value.HasField("ws_request"):
                continue
            request = value.ws_request
            if request.method == "never":
                continue
            response = r.Response()
            response.ws_response.index = request.index
            response.ws_response.response = request.payload
            # A frame may have both RPC response and update.
            response.ws_update.update.composed_update.messageSent.rid = 7
            await socket.send(response.SerializeToString())

    async with serve(handler, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        config = Config(profile=ProtocolProfile(websocket_url=f"ws://127.0.0.1:{port}"), rpc_timeout=0.05)
        transport = WebSocketTransport("fake", config)
        try:
            await transport.connect()
            assert await asyncio.gather(*[transport.request("s", "echo", bytes([i])) for i in range(4)]) == [
                bytes([i]) for i in range(4)
            ]
            assert transport.updates.qsize() == 4
            with pytest.raises(TransportError) as exc:
                await transport.request("s", "never", b"x")
            assert exc.value.possibly_sent and transport.pending_count == 0
            task = asyncio.create_task(transport.request("s", "never", b"y"))
            await asyncio.sleep(0.01)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            assert transport.pending_count == 0
            old_generation = transport.generation
            await transport.close()
            await transport.connect()
            assert transport.generation > old_generation
            assert await transport.request("s", "echo", b"after") == b"after"
        finally:
            await transport.close()


async def test_http_status_and_grpc_status_are_separate():
    import httpx
    from fncbale.transports import GrpcTransport
    from fncbale.protocol import grpc_frame
    from fncbale.errors import RpcError

    def respond(request):
        if request.url.path.endswith("error"):
            return httpx.Response(200, headers={"grpc-status": "7"}, content=grpc_frame(b""))
        return httpx.Response(200, headers={"grpc-status": "0"}, content=grpc_frame(b"ok"))

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        transport = GrpcTransport("fake", Config(), http)
        assert await transport.request("s", "ok", b"request") == b"ok"
        with pytest.raises(RpcError):
            await transport.request("s", "error", b"request")


@pytest.mark.parametrize(
    "error_name,possibly_sent",
    [
        ("ConnectError", False),
        ("ConnectTimeout", False),
        ("PoolTimeout", False),
        ("ReadTimeout", True),
        ("WriteTimeout", True),
        ("ReadError", True),
        ("WriteError", True),
        ("RemoteProtocolError", True),
    ],
)
async def test_http_failure_stage_preserves_known_unsent_vs_ambiguous(error_name, possibly_sent):
    import httpx
    from fncbale.transports import GrpcTransport

    def respond(request):
        raise getattr(httpx, error_name)("synthetic", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        transport = GrpcTransport("synthetic", Config(), http)
        with pytest.raises(TransportError) as error:
            await transport.request("s", "write", b"frozen")
        assert error.value.possibly_sent is possibly_sent


async def test_actual_http_pool_timeout_sends_no_second_request():
    import httpx
    from fncbale.transports import GrpcTransport

    received, release = [], asyncio.Event()
    handlers = set()

    async def hold_connection(reader, writer):
        import contextlib

        handlers.add(asyncio.current_task())
        try:
            received.append(await reader.readuntil(b"\r\n\r\n"))
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Length: 1\r\n\r\n")
            await writer.drain()
            await release.wait()
            writer.write(b"x")
            await writer.drain()
        finally:
            writer.close()
            with contextlib.suppress(ConnectionError):
                await writer.wait_closed()
            handlers.discard(asyncio.current_task())

    server = await asyncio.start_server(hold_connection, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    config = Config(profile=ProtocolProfile(grpc_url=url), rpc_timeout=1)
    try:
        async with (
            asyncio.timeout(3),
            server,
            httpx.AsyncClient(
                limits=httpx.Limits(max_connections=1), timeout=httpx.Timeout(1, pool=0.03), trust_env=False
            ) as http,
        ):
            async with http.stream("GET", url + "/hold") as held:
                try:
                    transport = GrpcTransport("synthetic", config, http)
                    with pytest.raises(TransportError) as error:
                        await transport.request("s", "write", b"frozen")
                    assert not error.value.possibly_sent
                    assert len(received) == 1 and received[0].startswith(b"GET /hold ")
                finally:
                    release.set()
                    assert await held.aread() == b"x"
    finally:
        release.set()
        server.close()
        await server.wait_closed()
        if handlers:
            await asyncio.wait_for(asyncio.gather(*tuple(handlers), return_exceptions=True), 1)
