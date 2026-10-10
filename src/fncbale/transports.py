from __future__ import annotations

import asyncio
import contextlib
import time

import httpx
from websockets.asyncio.client import connect

from .config import Config
from .errors import ProtocolError, RpcError, TransportError
from .protocol import grpc_decode, grpc_frame, parse, retry_delay
from .proto import request_pb2 as q, response_pb2 as r


def metadata(profile, session_id):
    items = {
        "app_version": profile.app_version,
        "browser_type": profile.browser_type,
        "browser_version": profile.browser_version,
        "os_type": profile.os_type,
        "session_id": session_id,
        "language": profile.language,
    }
    return {**items, **{"mt_" + key: value for key, value in items.items()}}


class WebSocketTransport:
    def __init__(self, token: str, config: Config):
        self._token, self.config = token, config
        self.socket = None
        self._reader = self._heartbeat = None
        self._pending = {}
        self._index = 0
        self.generation = 0
        self._send_lock = asyncio.Lock()
        self._lifecycle_lock = asyncio.Lock()
        self.updates = asyncio.Queue(config.queue_size)
        self.disconnected = asyncio.Event()
        self.disconnected.set()
        self._meta = q.Metadata()
        for key, value in metadata(config.profile, str(time.time_ns() // 1_000_000)).items():
            item = self._meta.key_values.add(key=key)
            item.value.string_value = value

    @property
    def pending_count(self):
        return len(self._pending)

    @property
    def connected(self):
        return self.socket is not None

    async def connect(self):
        async with self._lifecycle_lock:
            await self._connect_once()

    async def _connect_once(self):
        if self.socket:
            return
        try:
            socket = await connect(
                self.config.profile.websocket_url,
                origin=self.config.profile.origin,
                additional_headers={"Cookie": f"access_token={self._token}"},
                compression=None,
                open_timeout=self.config.rpc_timeout,
                close_timeout=3,
                max_size=self.config.max_frame_size,
                max_queue=16,
            )
        except Exception as exc:
            raise TransportError("WebSocket connection failed") from exc
        self.generation += 1
        generation = self.generation
        self.socket = socket
        self.disconnected.clear()
        # Observed current web handshake. Standard WS ping and application heartbeat are separate.
        try:
            async with asyncio.timeout(self.config.rpc_timeout):
                await socket.send(b"\x1a\x04\x08\x01\x10\x01")
        except BaseException as exc:
            self.socket = None
            self.disconnected.set()
            with contextlib.suppress(Exception):
                await socket.close()
            if isinstance(exc, asyncio.CancelledError):
                raise
            raise TransportError("WebSocket handshake failed") from None
        self._reader = asyncio.create_task(self._read(socket, generation), name="fncbale-ws-reader")
        self._heartbeat = asyncio.create_task(self._keepalive(socket), name="fncbale-heartbeat")

    async def request(self, service: str, method: str, payload: bytes):
        socket, generation = self.socket, self.generation
        if socket is None:
            raise TransportError("WebSocket is disconnected")
        self._index += 1
        index = self._index
        future = asyncio.get_running_loop().create_future()
        self._pending[(generation, index)] = future
        request = q.Request()
        request.ws_request.service_name = service
        request.ws_request.method = method
        request.ws_request.payload = payload
        request.ws_request.metadata.CopyFrom(self._meta)
        request.ws_request.index = index
        sent = send_completed = False
        try:
            async with asyncio.timeout(self.config.rpc_timeout):
                async with self._send_lock:
                    if self.socket is not socket:
                        raise TransportError("Connection changed before send")
                    sent = True  # send failure can occur after partial transfer
                    await socket.send(request.SerializeToString())
                    send_completed = True
                return await future
        except RpcError:
            raise
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            raise TransportError("WebSocket RPC interrupted", possibly_sent=sent) from exc
        finally:
            self._pending.pop((generation, index), None)
            if not future.done():
                future.cancel()
            elif not future.cancelled():
                # Reader may fail the future while send itself fails/cancels.
                # Retrieve that exception even if we never reached the await.
                future.exception()
            if sent and not send_completed:
                # A cancelled/failed send can leave a partial frame or a blocked
                # write buffer. Never reuse it, or close a replacement generation.
                async with self._lifecycle_lock:
                    if self.socket is socket and self.generation == generation:
                        await self._close_once()

    async def _read(self, socket, generation):
        try:
            async for raw in socket:
                if not isinstance(raw, bytes):
                    continue
                value = parse(r.Response, raw)
                if value.HasField("ws_response"):
                    response = value.ws_response
                    future = self._pending.get((generation, response.index))
                    if future and not future.done():
                        if response.HasField("error"):
                            future.set_exception(
                                RpcError(
                                    response.error.code,
                                    "websocket",
                                    reason=response.error.message,
                                    retry_after=retry_delay(None, reason=response.error.message),
                                )
                            )
                        else:
                            future.set_result(response.response)
                if value.HasField("ws_update"):
                    try:
                        self.updates.put_nowait(raw)
                    except asyncio.QueueFull:
                        # Stop this stream and recover via all persisted route cursors.
                        # Never silently evict an older update to make space.
                        await socket.close(code=1013, reason="durable consumer backpressure")
                        break
        except asyncio.CancelledError:
            raise
        except Exception:
            pass  # supervisor reconnects; pending calls receive sanitized failure
        finally:
            if self.socket is socket:
                self.socket = None
                self.disconnected.set()
                if self._heartbeat:
                    self._heartbeat.cancel()
            for key, future in list(self._pending.items()):
                if key[0] == generation:
                    if not future.done():
                        future.set_exception(TransportError("WebSocket closed", possibly_sent=True))
                    self._pending.pop(key, None)
            with contextlib.suppress(Exception):
                await socket.close()

    async def _keepalive(self, socket):
        request = q.KeepAliveRequest()
        request.payloads.value_should_2 = 2
        try:
            while self.socket is socket:
                async with asyncio.timeout(self.config.rpc_timeout):
                    async with self._send_lock:
                        if self.socket is not socket:
                            return
                        await socket.send(request.SerializeToString())
                await asyncio.sleep(self.config.heartbeat_interval)
        except asyncio.CancelledError:
            raise
        except Exception:
            # A stalled control write must unblock RPC capacity and signal the
            # supervisor. Retire only this socket, never a newer generation.
            async with self._lifecycle_lock:
                if self.socket is socket:
                    await self._close_once()

    async def close(self):
        async with self._lifecycle_lock:
            await self._close_once()

    async def _close_once(self):
        socket, self.socket = self.socket, None
        tasks = [t for t in (self._reader, self._heartbeat) if t and t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        if socket:
            with contextlib.suppress(Exception):
                await socket.close()
        for future in self._pending.values():
            if not future.done():
                future.set_exception(TransportError("WebSocket closed", possibly_sent=True))
        self._pending.clear()
        self.disconnected.set()


class GrpcTransport:
    def __init__(self, token, config, http=None, *, ssl_context=True):
        self._token, self.config = token, config
        self._owns_http = http is None
        self.http = http or httpx.AsyncClient(
            http2=True,
            verify=ssl_context,
            timeout=config.rpc_timeout,
            limits=httpx.Limits(max_connections=config.rpc_limit, max_keepalive_connections=2),
        )
        self._headers = metadata(config.profile, str(time.time_ns() // 1_000_000))
        self._headers.update({"origin": config.profile.origin, "content-type": "application/grpc-web+proto"})

    async def request(self, service, method, payload):
        try:
            async with asyncio.timeout(self.config.rpc_timeout):
                return await self._request_once(service, method, payload)
        except TimeoutError as exc:
            raise TransportError("HTTP RPC deadline exceeded", possibly_sent=True) from exc

    async def _request_once(self, service, method, payload):
        headers = dict(self._headers)
        # Explicit even when anonymous: HTTPX otherwise merges a Set-Cookie JWT
        # before the Client has durably adopted the validated session.
        headers["cookie"] = f"access_token={self._token}" if self._token else ""
        try:
            async with self.http.stream(
                "POST",
                f"{self.config.profile.grpc_url.rstrip('/')}/{service}/{method}",
                headers=headers,
                content=grpc_frame(payload),
                follow_redirects=False,
            ) as response:
                if response.status_code == 429:
                    wait = retry_delay(response.headers.get("retry-after"))
                    if wait is None:
                        wait = 1
                    raise RpcError(8, method, retry_after=wait)
                if response.status_code >= 400:
                    if response.status_code >= 500 or response.status_code == 408:
                        raise TransportError("HTTP server response is ambiguous", possibly_sent=True)
                    raise RpcError(response.status_code, method)
                if response.status_code != 200:
                    # Redirects can replay writes; asynchronous/partial 2xx are
                    # not final unary RPC acknowledgements, even with grpc-status0.
                    raise TransportError("HTTP RPC has no final response", possibly_sent=True)
                body = bytearray()
                async for chunk in response.aiter_bytes():
                    body.extend(chunk)
                    if len(body) > self.config.max_frame_size:
                        raise ProtocolError("gRPC response exceeds configured limit")
                return grpc_decode(bytes(body), response.headers, method, self.config.max_frame_size)
        except (RpcError, ProtocolError):
            raise
        except (httpx.ConnectError, httpx.ConnectTimeout, httpx.PoolTimeout) as exc:
            # HTTPX guarantees these phases precede application request headers.
            # The whole-attempt SDK deadline has no such stage proof and remains
            # possibly sent, as do write/read/remote-protocol failures below.
            raise TransportError("HTTP request could not acquire a connection") from exc
        except httpx.HTTPError as exc:
            raise TransportError("HTTP RPC interrupted", possibly_sent=True) from exc

    async def close(self):
        if self._owns_http:
            await self.http.aclose()
