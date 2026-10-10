import asyncio

import pytest

from fncbale import Client, Config, Session
from fncbale.errors import BaleError, ClientClosed, RpcError, TransportError
from fncbale.contracts import contract


@pytest.mark.parametrize("gate", ["account", "pool"])
@pytest.mark.parametrize("boundary", ["close", "identity"])
async def test_queued_raw_rpc_checks_lifecycle_before_transport(tmp_path, gate, boundary):
    client = Client(
        Session(1, "synthetic"), data_dir=tmp_path, config=Config(rpc_limit=1, global_rpc_limit=1)
    )
    client.account = "original"
    semaphore = client._rpc_limit if gate == "account" else client.resources.rpc_limit
    await semaphore.acquire()
    calls = []

    async def request(*args):
        calls.append(client.account)
        return b"synthetic"

    client._grpc.request = request
    pending = asyncio.create_task(
        client.invoke_raw("synthetic", "method", b"frozen", route="http", retry_policy="none")
    )
    try:
        async with asyncio.timeout(2):
            while not semaphore._waiters:
                await asyncio.sleep(0)
        if boundary == "close":
            await client.close()
        else:
            client.account = "new-account"
        semaphore.release()
        with pytest.raises(ClientClosed if boundary == "close" else BaleError):
            await pending
        assert not calls
    finally:
        if semaphore.locked():
            semaphore.release()
        pending.cancel()
        await asyncio.gather(pending, return_exceptions=True)
        await client.close()


@pytest.mark.parametrize("api", ["typed", "raw"])
async def test_read_fallback_does_not_continue_under_another_account(tmp_path, api):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    client.account = "original"
    calls = []

    async def request(*args):
        calls.append(client.account)
        client.account = "new-account"
        raise TransportError("synthetic unsent failure")

    if api == "typed":
        client._call_bytes = request
        pending = client._rpc("GetContacts", contract("GetContacts").request())
    else:
        client._request = request
        pending = client.invoke_raw("synthetic", "method", b"frozen", retry_policy="readonly")
    try:
        with pytest.raises(BaleError, match="account"):
            await pending
        assert calls == ["original"]
    finally:
        await client.close()


async def test_late_rate_limit_is_recorded_for_the_request_account(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    client.account = "original"
    entered, release = asyncio.Event(), asyncio.Event()

    async def request(*args):
        entered.set()
        await release.wait()
        raise RpcError(8, "synthetic", retry_after=60)

    client._grpc.request = request
    pending = asyncio.create_task(
        client.invoke_raw("synthetic", "method", b"frozen", route="http", retry_policy="none")
    )
    try:
        await entered.wait()
        client.account = "new-account"
        release.set()
        with pytest.raises(RpcError):
            await pending
        assert client.store.rate_deadline("original") > 0
        assert client.store.rate_deadline("new-account") == 0
    finally:
        release.set()
        await asyncio.gather(pending, return_exceptions=True)
        await client.close()


async def test_late_typed_result_cannot_populate_a_new_identity(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    client.account = "original"

    async def request(*args):
        client.account = "new-account"
        return contract("GetContacts").response().SerializeToString()

    client._call_bytes = request
    try:
        with pytest.raises(BaleError, match="account"):
            await client._rpc("GetContacts", contract("GetContacts").request())
    finally:
        await client.close()


@pytest.mark.parametrize("api", ["typed", "raw-write"])
async def test_validated_response_is_preserved_when_close_begins(tmp_path, api):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)

    async def request(*args):
        await client.close()
        return (
            b"validated-ack" if api == "raw-write" else contract("GetContacts").response().SerializeToString()
        )

    try:
        if api == "typed":
            client._call_bytes = request
            result = await client._rpc("GetContacts", contract("GetContacts").request())
            assert isinstance(result, contract("GetContacts").response)
        else:
            client._grpc.request = request
            result = await client.invoke_raw(
                "synthetic", "method", b"frozen", route="http", retry_policy="none"
            )
            assert result == b"validated-ack"
        assert client._closed
    finally:
        await client.close()


async def test_late_rate_error_after_close_preserves_rpc_error(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    client.account = "original"
    error = RpcError(8, "synthetic", retry_after=60)

    async def request(*args):
        await client.close()
        raise error

    client._grpc.request = request
    try:
        with pytest.raises(RpcError) as caught:
            await client.invoke_raw("synthetic", "method", b"frozen", route="http", retry_policy="none")
        assert caught.value is error and client._closed
    finally:
        await client.close()
