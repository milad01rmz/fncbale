import asyncio
import hashlib

import httpx
import pytest

from fncbale import Client, Config, Session, BatchDownloadError, contract
from fncbale.errors import RpcError
from fncbale.models import MediaInfo, MediaKind
from fncbale.resources import Resources


class Stream(httpx.AsyncByteStream):
    def __init__(self, value, enter, leave):
        self.value, self.enter, self.leave = value, enter, leave

    async def __aiter__(self):
        self.enter()
        try:
            await asyncio.sleep(0.03)
            yield self.value
        finally:
            self.leave()


async def setup(tmp_path, config=None, resources=None):
    config = config or Config(download_limit=2, global_download_limit=3)
    resources = resources or Resources(config)
    await resources.http.aclose()
    active = peak = 0
    calls = []

    def enter():
        nonlocal active, peak
        active += 1
        peak = max(peak, active)

    def leave():
        nonlocal active
        active -= 1

    def get(request):
        return httpx.Response(200, stream=Stream(b"abc", enter, leave))

    resources.http = httpx.AsyncClient(transport=httpx.MockTransport(get))
    client = Client(Session(1, "synthetic"), data_dir=tmp_path, config=config, _resources=resources)

    async def rpc(method, request):
        calls.append((method, request))
        response = contract(method).response()
        if method == "GetNasimFileUrls":
            for file in reversed(request.files):
                response.fileUrls.add(
                    fileId=file.fileId, url=f"https://signed.invalid/{file.fileId}?secret=hidden"
                )
        else:
            response.fileUrl.url = "https://signed.invalid/single?secret=hidden"
        return response

    client._rpc = rpc

    def media(rid):
        return MediaInfo(MediaKind.DOCUMENT, rid, 2, 3, "file.bin", "application/octet-stream")

    return client, resources, calls, media, lambda: (active, peak)


async def test_batch_download_order_hashes_and_shared_concurrency(tmp_path):
    client, resources, calls, media, peaks = await setup(tmp_path)
    sibling = Client(
        Session(2, "synthetic"), data_dir=tmp_path / "other", config=client.config, _resources=resources
    )
    sibling._rpc = client._rpc
    try:
        jobs = [(media(rid), tmp_path / f"{rid}.bin") for rid in range(1, 6)]
        hashes = [hashlib.sha256(b"abc").hexdigest()] * 5
        one, two = await asyncio.gather(
            client.download_many(jobs, expected_sha256=hashes),
            sibling.download_many([(media(rid), tmp_path / f"other-{rid}.bin") for rid in range(1, 6)]),
        )
        assert one == tuple(path for _, path in jobs)
        assert all(path.read_bytes() == b"abc" for path in (*one, *two))
        assert [name for name, _ in calls] == ["GetNasimFileUrls", "GetNasimFileUrls"]
        assert peaks() == (0, 3)
    finally:
        await client.close()
        await sibling.close()
        await resources.close()


async def test_partial_allocation_expiry_and_failed_hash_report_ordered_results(tmp_path):
    client, resources, calls, media, peaks = await setup(tmp_path)
    original = client._rpc
    gets = 0

    async def rpc(method, request):
        response = await original(method, request)
        if method == "GetNasimFileUrls":
            del response.fileUrls[0]  # Missing second ID gets a singular allocation.
        return response

    def get(request):
        nonlocal gets
        gets += 1
        if "/1?" in str(request.url) and gets <= 2:
            return httpx.Response(403)
        return httpx.Response(200, content=b"abc")

    client._rpc = rpc
    await resources.http.aclose()
    resources.http = httpx.AsyncClient(transport=httpx.MockTransport(get))
    paths = [tmp_path / "first", tmp_path / "second"]
    paths[1].write_bytes(b"old")
    try:
        with pytest.raises(BatchDownloadError) as caught:
            await client.download_many(
                [(media(1), paths[0]), (media(2), paths[1])],
                expected_sha256=[hashlib.sha256(b"abc").hexdigest(), "0" * 64],
            )
        results = caught.value.results
        assert [item.completed for item in results] == [True, False]
        assert results[1].error_type == "BaleError" and paths[1].read_bytes() == b"old"
        assert paths[0].read_bytes() == b"abc" and not list(tmp_path.glob("*.part"))
        assert [name for name, _ in calls].count("GetNasimFileUrl") == 2
        assert "secret=" not in str(caught.value) and caught.value.__cause__ is None
    finally:
        await client.close()
        await resources.close()


@pytest.mark.parametrize("code", [12, 16])
async def test_batch_unsupported_fallback_respects_auth_errors(tmp_path, code):
    client, resources, calls, media, peaks = await setup(tmp_path)
    original = client._rpc

    async def rpc(method, request):
        if method == "GetNasimFileUrls":
            raise RpcError(code, method)
        return await original(method, request)

    client._rpc = rpc
    try:
        if code == 16:
            with pytest.raises(RpcError):
                await client.download_many([(media(1), tmp_path / "one")])
            assert not calls
        else:
            paths = await client.download_many([(media(1), tmp_path / "one")])
            assert paths[0].read_bytes() == b"abc" and [name for name, _ in calls] == ["GetNasimFileUrl"]
    finally:
        await client.close()
        await resources.close()


async def test_batch_validation_and_cancellation_preserve_destinations(tmp_path):
    client, resources, calls, media, peaks = await setup(tmp_path)
    path = tmp_path / "existing"
    path.write_bytes(b"old")
    try:
        for jobs, hashes in (
            ([(media(1), path), (media(2), path)], None),
            ([(media(1), path)], ["invalid"]),
            ([], None),
        ):
            with pytest.raises(ValueError):
                await client.download_many(jobs, expected_sha256=hashes)
        assert not calls
        entered, release = asyncio.Event(), asyncio.Event()

        async def progress(index, done, total):
            entered.set()
            await release.wait()

        task = asyncio.create_task(client.download_many([(media(1), path)], progress=progress))
        await entered.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert path.read_bytes() == b"old" and not list(tmp_path.glob("*.part"))
        assert peaks()[0] == 0
    finally:
        await client.close()
        await resources.close()


async def test_single_downloads_share_account_limit_across_callers(tmp_path):
    client, resources, calls, media, peaks = await setup(tmp_path)
    try:
        paths = await asyncio.gather(
            *[client.download(media(rid), tmp_path / str(rid)) for rid in range(1, 7)]
        )
        assert len(paths) == 6 and peaks() == (0, 2)
    finally:
        await client.close()
        await resources.close()


async def test_cancelled_progress_future_reports_partial_result_and_other_jobs_finish(tmp_path):
    client, resources, calls, media, peaks = await setup(tmp_path)

    async def progress(index, done, total):
        if index == 0:
            future = asyncio.get_running_loop().create_future()
            future.cancel()
            await future

    try:
        with pytest.raises(BatchDownloadError) as caught:
            await client.download_many(
                [(media(1), tmp_path / "one"), (media(2), tmp_path / "two")], progress=progress
            )
        assert [item.completed for item in caught.value.results] == [False, True]
        assert caught.value.results[0].error_type == "CancelledError"
        assert not list(tmp_path.glob("*.part")) and peaks()[0] == 0
    finally:
        await client.close()
        await resources.close()
