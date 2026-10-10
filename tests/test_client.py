import asyncio

import pytest

from fncbale import Client, Config, Media, MediaKind, Peer, PeerKind, Session
from fncbale.contracts import contract
from fncbale.errors import DeliveryUncertain, TransportError, StorageError, RpcError


async def offline_client(tmp_path, calls):
    client = Client(Session(123, "fake-not-a-token"), data_dir=tmp_path, config=Config(outbox_workers=1))
    client.account, client._active = "test", True

    async def call(method, payload, route):
        calls.append((method, payload, route))
        return contract(method).response(date=42).SerializeToString()

    client._call_bytes = call
    client._tasks.append(asyncio.create_task(client._outbox_worker()))
    return client


async def test_durable_idempotency_cancel_and_edit(tmp_path):
    calls = []
    client = await offline_client(tmp_path, calls)
    try:
        peer = Peer(PeerKind.CHANNEL, 10, 12)
        one = await client.send_message(peer, "hello", idempotency_key="one")
        two = await client.send_message(peer, "hello", idempotency_key="one")
        assert one.rid == two.rid and len(calls) == 1
        assert not contract("SendMessage").request.FromString(calls[0][1]).HasField("exPeer")
        edit = await client.edit_message(one, "new")
        assert edit.text == "new" and edit.rid == one.rid
        await client.forward(peer, one)
        forward = contract("ForwardMessages").request.FromString(calls[-1][1])
        assert forward.peer.type == 3 and forward.forwardedMessages[0].peer.type == 2
        assert not forward.forwardedMessages[0].HasField("seq")
    finally:
        await client.close()


async def test_ambiguous_send_not_blindly_retried(tmp_path):
    calls = []
    client = await offline_client(tmp_path, calls)

    async def interrupted(method, payload, route):
        calls.append(payload)
        raise TransportError("lost ack", possibly_sent=True)

    async def missing(row):
        return False

    client._call_bytes, client._reconcile_row = interrupted, missing
    try:
        with pytest.raises(DeliveryUncertain):
            await client.send_message(Peer(PeerKind.USER, 10), "one")
        assert len(calls) == 1
    finally:
        await client.close()


async def test_verified_retry_preserves_exact_payload(tmp_path):
    calls = []
    client = await offline_client(tmp_path, calls)
    client.config = Config(verified_idempotent_methods=frozenset({"SendMessage"}))

    async def interrupted(method, payload, route):
        calls.append((payload, route))
        if len(calls) < 3:
            raise TransportError("lost", possibly_sent=True)
        return contract(method).response(date=7).SerializeToString()

    async def missing(row):
        return False

    client._call_bytes, client._reconcile_row = interrupted, missing
    try:
        await client.send_message(Peer(PeerKind.USER, 10), "one")
        assert [x[1] for x in calls] == ["websocket", "websocket", "http"]
        assert len({x[0] for x in calls}) == 1
    finally:
        await client.close()


async def test_album_invalid_before_prepare_or_upload(tmp_path):
    calls = []
    client = await offline_client(tmp_path, calls)
    try:
        with pytest.raises(ValueError):
            await client.send_album(Peer(PeerKind.USER, 10), [Media(b"invalid", MediaKind.PHOTO)])
        assert not calls and not (tmp_path / "spool").exists()
    finally:
        await client.close()


async def test_metadata_and_immutable_spool(tmp_path):
    from PIL import Image

    source = tmp_path / "photo.png"
    Image.new("RGB", (640, 480), "red").save(source)
    calls = []
    client = await offline_client(tmp_path, calls)
    try:
        info = await client.media.prepare(Media(source, MediaKind.PHOTO))
        assert (info["width"], info["height"]) == (640, 480)
        frozen = __import__("pathlib").Path(info["path"]).read_bytes()
        source.write_bytes(b"changed")
        assert __import__("pathlib").Path(info["path"]).read_bytes() == frozen
    finally:
        await client.close()


async def test_ack_commit_failure_retries_only_database(tmp_path):
    calls = []
    client = await offline_client(tmp_path, calls)
    original = client.store.finish
    failures = 0

    async def faulty(*args, **kwargs):
        nonlocal failures
        if args[2] == "confirmed" and failures < 2:
            failures += 1
            raise StorageError("synthetic disk unavailable")
        return await original(*args, **kwargs)

    client.store.finish = faulty
    try:
        message = await asyncio.wait_for(client.send_message(Peer(PeerKind.USER, 10), "one"), 5)
        assert len(calls) == 1 and failures == 2
        assert (await client.get_operation(message.operation_id)).status == "confirmed"
    finally:
        await client.close()


async def test_rate_wait_restart_uses_remaining_routes_and_same_payload(tmp_path):
    calls = []
    client = await offline_client(tmp_path, calls)

    async def rejected(method, payload, route):
        calls.append((payload, route))
        raise RpcError(8, method, retry_after=0.2)

    client._call_bytes = rejected
    handle = await client.enqueue_message(Peer(PeerKind.USER, 10), "one")
    try:
        async with asyncio.timeout(5):
            while (await handle.status()).status != "waiting":
                await asyncio.sleep(0.01)
        assert (await handle.status()).cycle_attempts == 1
    finally:
        await client.close()
    client = await offline_client(tmp_path, [])
    client._call_bytes = rejected
    try:
        from fncbale.errors import OperationFailed

        with pytest.raises(OperationFailed):
            await asyncio.wait_for(client.wait_operation(handle.operation_id), 5)
        assert [route for _, route in calls] == ["websocket", "websocket", "http"]
        assert len({payload for payload, _ in calls}) == 1
        assert (await client.get_operation(handle.operation_id)).attempts == 3
    finally:
        await client.close()


async def test_unexpected_exception_after_dispatch_is_uncertain(tmp_path):
    client = await offline_client(tmp_path, [])

    async def broken(method, payload, route):
        raise ValueError("unexpected decoder error")

    client._call_bytes = broken
    try:
        with pytest.raises(DeliveryUncertain):
            await client.send_message(Peer(PeerKind.USER, 10), "one")
    finally:
        await client.close()


async def test_empty_message_ack_is_uncertain_with_one_frozen_transmission(tmp_path):
    calls = []
    client = await offline_client(tmp_path, calls)

    async def empty(method, payload, route):
        calls.append(payload)
        return b""  # Valid protobuf, unusable as a new-message acknowledgement.

    async def missing(row):
        return False

    client._call_bytes, client._reconcile_row = empty, missing
    try:
        with pytest.raises(DeliveryUncertain) as caught:
            await client.send_message(Peer(PeerKind.USER, 10), "one")
        assert len(calls) == 1
        status = await client.get_operation(caught.value.operation_id)
        assert status.status == "uncertain" and not status.rpc_confirmed
    finally:
        await client.close()


async def test_edit_ack_mutation_time_does_not_replace_original_ref(tmp_path):
    from fncbale import MessageRef

    client = await offline_client(tmp_path, [])
    ref = MessageRef(Peer(PeerKind.CHANNEL, 10), 33, 10, 2**55 + 3)
    try:
        edited = await client.edit_message(ref, "changed")  # Offline ACK date is 42.
        assert edited.ref == ref and edited.text == "changed"
    finally:
        await client.close()


@pytest.mark.parametrize("fault", ["ws-send", "http-body", "http-redirect"])
async def test_real_transport_fault_keeps_durable_write_uncertain_without_resend(tmp_path, fault):
    import httpx
    from fncbale.protocol import grpc_frame
    from fncbale.transports import WebSocketTransport, GrpcTransport

    client = Client(Session(123, "synthetic"), data_dir=tmp_path, config=Config(rpc_timeout=0.03))
    client.account, client._active = "test", True
    calls = []
    closed = asyncio.Event()

    class Socket:
        async def send(self, payload):
            calls.append(payload)
            await asyncio.Event().wait()

        async def close(self):
            closed.set()

    class Body(httpx.AsyncByteStream):
        async def __aiter__(self):
            await asyncio.Event().wait()
            yield b""

        async def aclose(self):
            closed.set()

    async def respond(request):
        calls.append(request.content)
        if fault == "http-body":
            return httpx.Response(200, headers={"grpc-status": "0"}, stream=Body())
        # A plausible message ACK does not make a redirect a valid response.
        return httpx.Response(
            307,
            headers={"grpc-status": "0", "location": "/another-write"},
            content=grpc_frame(contract("SendMessage").response(date=42).SerializeToString()),
        )

    async def no_history(row):
        return False

    client._reconcile_row = no_history
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond), follow_redirects=True) as http:
        transport = (
            WebSocketTransport("synthetic", client.config)
            if fault == "ws-send"
            else GrpcTransport("synthetic", client.config, http)
        )
        if fault == "ws-send":
            transport.socket = Socket()
            transport.disconnected.clear()

        async def call(method, payload, route):
            return await transport.request(contract(method).service, method, payload)

        client._call_bytes = call
        client._tasks.append(asyncio.create_task(client._outbox_worker()))
        try:
            handle = await client.enqueue_message(Peer(PeerKind.USER, 10), "frozen", idempotency_key="fault")
            with pytest.raises(DeliveryUncertain):
                await asyncio.wait_for(handle.wait(), 2)
            status = await handle.status()
            assert status.status == "uncertain" and status.attempts == 1 and not status.rpc_confirmed
            assert len(calls) == 1
            replay = await client.enqueue_message(Peer(PeerKind.USER, 10), "frozen", idempotency_key="fault")
            assert replay.operation_id == handle.operation_id and len(calls) == 1
            if fault != "http-redirect":
                assert closed.is_set()
        finally:
            await client.close()
            await transport.close()


@pytest.mark.parametrize("error_name", ["PoolTimeout", "ConnectTimeout"])
async def test_unsent_http_exhaustion_allows_explicit_retry_with_original_operation(tmp_path, error_name):
    import httpx
    from fncbale.errors import OperationFailed
    from fncbale.protocol import grpc_frame
    from fncbale.transports import WebSocketTransport, GrpcTransport

    client = await offline_client(tmp_path, [])
    attempts, received = [], []
    rejecting = True

    def respond(request):
        received.append(request.content)
        if rejecting:
            raise getattr(httpx, error_name)("synthetic before headers", request=request)
        return httpx.Response(
            200,
            headers={"grpc-status": "0"},
            content=grpc_frame(contract("SendMessage").response(date=42).SerializeToString()),
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        ws, grpc = (
            WebSocketTransport("synthetic", client.config),
            GrpcTransport("synthetic", client.config, http),
        )

        async def call(method, payload, route):
            attempts.append((payload, route))
            transport = ws if route == "websocket" else grpc
            return await transport.request(contract(method).service, method, payload)

        client._call_bytes = call
        try:
            peer = Peer(PeerKind.USER, 10)
            handle = await client.enqueue_message(peer, "frozen", idempotency_key="unsent")
            with pytest.raises(OperationFailed):
                await asyncio.wait_for(handle.wait(), 5)
            status = await handle.status()
            assert status.status == "failed" and status.attempts == 3 and not status.rpc_confirmed
            assert [route for _, route in attempts] == ["websocket", "websocket", "http"]
            rejecting = False
            resumed = await client.retry_operation(handle.operation_id)
            message = await asyncio.wait_for(resumed.wait(), 5)
            recovered = await client.enqueue_message(peer, "frozen", idempotency_key="unsent")
            assert (
                recovered.operation_id == resumed.operation_id == handle.operation_id == message.operation_id
            )
            assert len(received) == 2 and received[0] == received[1]
            assert len(attempts) == 6 and len({payload for payload, _ in attempts}) == 1
            assert (await resumed.status()).status == "confirmed"
        finally:
            await client.close()
            await ws.close()
