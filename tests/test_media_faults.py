import asyncio
import errno
import hashlib
import threading
from types import SimpleNamespace

import httpx
import pytest

from fncbale import Config, Media, MediaKind, Peer, PeerKind, Session, contract
from fncbale.errors import BaleError, TransportError
from fncbale.media import MediaPipeline, disk_call
from fncbale.models import MediaInfo
from fncbale.resources import Resources


class Chunks(httpx.AsyncByteStream):
    def __init__(self, values, failure=False):
        self.values, self.failure = values, failure

    async def __aiter__(self):
        for chunk in self.values:
            yield chunk
        if self.failure:
            raise httpx.ReadError("https://signed.invalid/file?secret=DO-NOT-LOG")


async def download_case(tmp_path, responses, *, expected=None):
    resources = Resources(Config(stream_chunk_size=3))
    await resources.http.aclose()
    requests, allocations = [], []

    def respond(request):
        requests.append(request)
        status, content, failure = responses[len(requests) - 1]
        return httpx.Response(status, stream=Chunks(content, failure))

    resources.http = httpx.AsyncClient(transport=httpx.MockTransport(respond))

    async def rpc(method, request):
        allocations.append(method)
        response = contract(method).response()
        response.fileUrl.url = f"https://signed.invalid/file?secret={len(allocations)}"
        return response

    target = tmp_path / "existing.bin"
    target.write_bytes(b"old")
    media = MediaInfo(MediaKind.DOCUMENT, 1, 2, 6, "file", "application/octet-stream")
    try:
        path = await MediaPipeline(tmp_path, Config(stream_chunk_size=3), resources).download(
            SimpleNamespace(_rpc=rpc),
            media,
            target,
            expected_sha256=expected,
        )
        return path, requests, allocations
    finally:
        await resources.close()


async def test_expired_url_reallocated_and_stream_hash(tmp_path):
    path, requests, allocations = await download_case(
        tmp_path,
        [(403, [], False), (200, [b"abc", b"def"], False)],
        expected=hashlib.sha256(b"abcdef").hexdigest(),
    )
    assert path.read_bytes() == b"abcdef" and len(allocations) == 2
    assert requests[0].url != requests[1].url and not list(tmp_path.glob("*.part"))


@pytest.mark.parametrize(
    "responses,error",
    [
        ([(200, [b"short"], False)], BaleError),
        ([(200, [b"too-long"], False)], BaleError),
        ([(200, [b"abc"], True), (200, [b"abc"], True)], TransportError),
    ],
)
async def test_incomplete_download_preserves_destination_and_hides_url(tmp_path, responses, error):
    with pytest.raises(error) as caught:
        await download_case(tmp_path, responses)
    assert "secret=" not in str(caught.value) and not caught.value.__cause__
    assert (tmp_path / "existing.bin").read_bytes() == b"old"
    assert not list(tmp_path.glob("*.part"))


async def test_cancellation_waits_for_outstanding_disk_write():
    entered, release, completed = threading.Event(), threading.Event(), threading.Event()

    def write():
        entered.set()
        assert release.wait(5)
        completed.set()

    task = asyncio.create_task(disk_call(write))
    assert await asyncio.to_thread(entered.wait, 5)
    task.cancel()
    await asyncio.sleep(0.02)
    assert not task.done()
    release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert completed.is_set()


async def test_disk_full_spool_is_removed_before_acceptance(tmp_path, monkeypatch):
    import fncbale.media as module

    original = module.disk_call

    async def full(function, *args, **kwargs):
        if function.__name__ == "write":
            raise OSError(errno.ENOSPC, "synthetic disk full")
        return await original(function, *args, **kwargs)

    resources = Resources(Config())
    monkeypatch.setattr(module, "disk_call", full)
    try:
        with pytest.raises(OSError) as error:
            await MediaPipeline(tmp_path, Config(), resources).prepare(Media(b"file"))
        assert error.value.errno == errno.ENOSPC and not list((tmp_path / "spool").iterdir())
    finally:
        await resources.close()


async def test_interrupted_put_reallocates_same_frozen_content(tmp_path):
    resources = Resources(Config())
    await resources.http.aclose()
    received = []

    async def respond(request):
        received.append(await request.aread())
        if len(received) == 1:
            raise httpx.WriteError("https://signed.invalid/?secret=DO-NOT-LOG")
        return httpx.Response(200)

    resources.http = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    allocations = []

    async def rpc(method, request, **kwargs):
        allocations.append(request)
        return contract(method).response(fileId=len(allocations), url="https://signed.invalid/upload")

    pipeline = MediaPipeline(tmp_path, Config(), resources)
    client = SimpleNamespace(session=Session(1, "synthetic"), _rpc=rpc, _upload_limit=asyncio.Semaphore(2))
    try:
        info = await pipeline.prepare(Media(b"unchanged-content"))
        document = await pipeline.upload(client, Peer(PeerKind.USER, 2), info)
        assert document.fileId == 2 and received == [b"unchanged-content"] * 2
        assert len(allocations) == 2
    finally:
        await resources.close()


@pytest.mark.parametrize("status", [101, 202, 204, 206, 301, 302, 307, 308])
async def test_download_requires_complete_http_response(tmp_path, status):
    # Matching length alone cannot turn a redirect/partial response into a file.
    with pytest.raises(TransportError) as caught:
        await download_case(tmp_path, [(status, [b"abcdef"], False)])
    assert str(status) in str(caught.value) and "secret=" not in str(caught.value)
    assert (tmp_path / "existing.bin").read_bytes() == b"old"
    assert not list(tmp_path.glob("*.part"))


@pytest.mark.parametrize("status", [101, 202, 205, 206, 301, 302, 307, 308])
async def test_upload_does_not_adopt_unfinished_allocation(tmp_path, status):
    resources = Resources(Config())
    await resources.http.aclose()
    requests = []

    async def respond(request):
        requests.append((request.url, await request.aread()))
        return httpx.Response(status, headers={"location": "https://other.invalid/?secret=REDIRECT"})

    resources.http = httpx.AsyncClient(transport=httpx.MockTransport(respond), follow_redirects=True)

    async def rpc(method, request, **kwargs):
        assert method == "GetNasimFileUploadUrl"
        return contract(method).response(fileId=1, url="https://signed.invalid/?secret=UPLOAD")

    pipeline = MediaPipeline(tmp_path, Config(), resources)
    client = SimpleNamespace(session=Session(1, "synthetic"), _rpc=rpc, _upload_limit=asyncio.Semaphore(2))
    try:
        info = await pipeline.prepare(Media(b"content"))
        with pytest.raises(TransportError) as caught:
            await pipeline.upload(client, Peer(PeerKind.USER, 2), info)
        assert "file_id" not in info and "access_hash" not in info
        assert len(requests) == 1 and requests[0][1] == b"content"
        assert str(status) in str(caught.value) and "secret=" not in str(caught.value)
    finally:
        await resources.close()


@pytest.mark.parametrize("status", [200, 201, 204])
async def test_completed_put_statuses_accept_allocation(tmp_path, status):
    resources = Resources(Config())
    await resources.http.aclose()
    resources.http = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(status)))

    async def rpc(method, request, **kwargs):
        return contract(method).response(fileId=7, url="https://signed.invalid/upload")

    pipeline = MediaPipeline(tmp_path, Config(), resources)
    client = SimpleNamespace(session=Session(1, "synthetic"), _rpc=rpc, _upload_limit=asyncio.Semaphore(2))
    try:
        info = await pipeline.prepare(Media(b"content"))
        document = await pipeline.upload(client, Peer(PeerKind.USER, 2), info)
        assert document.fileId == 7 and info["file_id"] == 7
    finally:
        await resources.close()


async def test_interrupted_transport_closes_owned_request_body_before_retry(tmp_path, monkeypatch):
    import fncbale.media as module

    opened, retained = [], []
    original = module.open_file

    async def tracking(path, mode):
        stream = await original(path, mode)
        if mode == "rb":
            opened.append(stream)
        return stream

    class Interrupted(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request):
            retained.append(request)
            if len(retained) == 1:
                iterator = request.stream.__aiter__()
                retained.append(iterator)
                assert await anext(iterator) == b"abcd"
                raise httpx.WriteError("modeled body interruption")
            async for _ in request.stream:
                pass
            return httpx.Response(200)

    monkeypatch.setattr(module, "open_file", tracking)
    resources = Resources(Config(stream_chunk_size=4))
    await resources.http.aclose()
    resources.http = httpx.AsyncClient(transport=Interrupted())

    async def rpc(method, request, **kwargs):
        return contract(method).response(fileId=7, url="https://signed.invalid/upload")

    pipeline = MediaPipeline(tmp_path, Config(stream_chunk_size=4), resources)
    client = SimpleNamespace(session=Session(1, "synthetic"), _rpc=rpc, _upload_limit=asyncio.Semaphore(2))
    try:
        info = await pipeline.prepare(Media(b"abcdefghijkl"))
        await pipeline.upload(client, Peer(PeerKind.USER, 2), info)
        assert len(opened) == 2 and all(stream.closed for stream in opened)
    finally:
        await resources.close()
        for retained_iterator in retained:
            if hasattr(retained_iterator, "aclose"):
                await retained_iterator.aclose()


async def test_cancelled_upload_closes_retained_body_before_releasing_slots(tmp_path, monkeypatch):
    import fncbale.media as module

    entered, opened, retained = asyncio.Event(), [], []
    original = module.open_file

    async def tracking(path, mode):
        stream = await original(path, mode)
        if mode == "rb":
            opened.append(stream)
        return stream

    class Blocked(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request):
            retained.append(request)
            iterator = request.stream.__aiter__()
            retained.append(iterator)
            assert await anext(iterator) == b"abcd"
            entered.set()
            await asyncio.Event().wait()

    monkeypatch.setattr(module, "open_file", tracking)
    config = Config(stream_chunk_size=4)
    resources = Resources(config)
    await resources.http.aclose()
    resources.http = httpx.AsyncClient(transport=Blocked())

    async def rpc(method, request, **kwargs):
        return contract(method).response(fileId=7, url="https://signed.invalid/upload")

    pipeline = MediaPipeline(tmp_path, config, resources)
    client = SimpleNamespace(session=Session(1, "synthetic"), _rpc=rpc, _upload_limit=asyncio.Semaphore(2))
    info = await pipeline.prepare(Media(b"abcdefghijkl"))
    task = asyncio.create_task(pipeline.upload(client, Peer(PeerKind.USER, 2), info))
    try:
        await asyncio.wait_for(entered.wait(), 3)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert len(opened) == 1 and opened[0].closed and "file_id" not in info
        assert (
            client._upload_limit._value == 2 and resources.upload_limit._value == config.global_upload_limit
        )
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        await resources.close()
        for iterator in retained:
            if hasattr(iterator, "aclose"):
                await iterator.aclose()
