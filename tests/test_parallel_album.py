import asyncio
import json

import pytest
import httpx
from PIL import Image

from fncbale import Client, Config, Media, MediaKind, Peer, PeerKind, Session, contract
from fncbale.errors import StorageError, TransportError


async def album_client(tmp_path, *, count=4, upload_limit=2):
    path = tmp_path / "photo.png"
    Image.new("RGB", (12, 8), "red").save(path)
    client = Client(Session(123, "fake"), data_dir=tmp_path, config=Config(upload_limit=upload_limit))
    client.account, client._active = "test", True
    handle = await client.enqueue_album(
        Peer(PeerKind.CHANNEL, 10, 12),
        [Media(path, MediaKind.PHOTO, caption=str(index)) for index in range(count)],
    )
    return client, handle, await client.store.claim(client.account)


async def test_parallel_completion_preserves_order_and_retries_commit_only(tmp_path):
    client, handle, row = await album_client(tmp_path)
    active = peak = 0
    calls, completions = [], []
    original = client.store.commit_media_upload
    failed_once = False
    progress_active = progress_peak = progress_calls = 0

    async def progress(done, total):
        nonlocal progress_active, progress_peak, progress_calls
        progress_active += 1
        progress_peak = max(progress_peak, progress_active)
        await asyncio.sleep(0.01)
        progress_calls += 1
        progress_active -= 1

    client._progress[handle.operation_id] = progress

    async def upload(client, peer, info, progress):
        nonlocal active, peak
        index = int(info["caption"])
        if not info.get("file_id"):
            async with client._upload_limit, client.resources.upload_limit:
                active += 1
                peak = max(peak, active)
                calls.append(index)
                await asyncio.sleep(0.02 if index % 2 else 0.04)
                if progress:
                    await progress(info["size"], info["size"])
                info.update(file_id=100 + index, access_hash=123)
                completions.append(index)
                active -= 1
        return client.media.document(info)

    async def commit(*args, **kwargs):
        nonlocal failed_once
        if args[2] == 1 and not failed_once:
            failed_once = True
            # Another worker can commit siblings while this snapshot waits.
            await asyncio.sleep(0.08)
            raise StorageError("injected group commit failure")
        return await original(*args, **kwargs)

    client.media.upload, client.store.commit_media_upload = upload, commit
    try:
        prepared = await asyncio.wait_for(client._prepare_operation(row), 5)
        frozen = contract("SendMultiMediaMessage").request.FromString(prepared["payload"])
        assert [item.media.fileId for item in frozen.multiMedia] == [100, 101, 102, 103]
        assert [item.media.caption.text for item in frozen.multiMedia] == ["0", "1", "2", "3"]
        assert len(calls) == 4 and peak == 2 and completions[0] == 1 and active == 0
        assert progress_peak == 1 and progress_calls == 4
        saved = json.loads((await client.store.operation(client.account, handle.operation_id))["context"])
        assert [info["file_id"] for info in saved["media"]] == [100, 101, 102, 103]
        assert saved["rids"] == json.loads(row["context"])["rids"]
    finally:
        await client.close()


async def test_interrupted_partial_album_reuses_committed_items_after_restart(tmp_path):
    client, handle, row = await album_client(tmp_path)
    blocked, cancelled = asyncio.Event(), asyncio.Event()
    calls = []

    async def upload(client, peer, info, progress):
        index = int(info["caption"])
        if not info.get("file_id"):
            calls.append(index)
            if index == 0:
                info.update(file_id=100, access_hash=123)
            else:
                blocked.set()
                try:
                    await asyncio.Event().wait()
                finally:
                    cancelled.set()
        return client.media.document(info)

    client.media.upload = upload
    task = asyncio.create_task(client._prepare_operation(row))
    try:
        await asyncio.wait_for(blocked.wait(), 5)
        for _ in range(100):
            current = await client.store.operation(client.account, handle.operation_id)
            if json.loads(current["context"])["media"][0].get("file_id"):
                break
            await asyncio.sleep(0.01)
        else:
            pytest.fail("Completed upload was not durably merged")
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert cancelled.is_set() and not current["payload"]
    finally:
        await client.close()
    restarted = Client(Session(123, "fake"), data_dir=tmp_path, config=Config(upload_limit=2))
    restarted.account, restarted._active = "test", True
    new_transfers = []

    async def resume(client, peer, info, progress):
        if not info.get("file_id"):
            new_transfers.append(int(info["caption"]))
            info.update(file_id=100 + int(info["caption"]), access_hash=123)
        return client.media.document(info)

    restarted.media.upload = resume
    try:
        await restarted.store.recover_operations(restarted.account)
        recovered = await restarted.store.claim(restarted.account)
        assert recovered["id"] == handle.operation_id and not recovered["in_flight"]
        prepared = await restarted._prepare_operation(recovered)
        assert new_transfers == [1, 2, 3]
        assert len(contract("SendMultiMediaMessage").request.FromString(prepared["payload"]).multiMedia) == 4
    finally:
        await restarted.close()


async def test_failed_item_cancels_siblings_without_partial_send_or_overwriting_items(tmp_path):
    client, handle, row = await album_client(tmp_path)
    sibling_started, sibling_stopped = asyncio.Event(), asyncio.Event()

    async def fail(client, peer, info, progress):
        if info["caption"] == "0":
            await sibling_started.wait()
            raise TransportError("injected incomplete transfer")
        sibling_started.set()
        try:
            await asyncio.Event().wait()
        finally:
            sibling_stopped.set()

    client.media.upload = fail
    try:
        with pytest.raises(TransportError):
            await asyncio.wait_for(client._prepare_operation(row), 5)
        current = await client.store.operation(client.account, handle.operation_id)
        assert sibling_stopped.is_set() and not current["payload"] and current["attempts"] == 0
        original = json.loads(current["context"])["media"][0]
        with pytest.raises(StorageError):
            await client.store.commit_media_upload(
                client.account, handle.operation_id, 0, sha256="changed", file_id=999, access_hash=123
            )
        assert (
            json.loads((await client.store.operation(client.account, handle.operation_id))["context"])[
                "media"
            ][0]
            == original
        )
    finally:
        await client.close()


async def test_redirected_album_upload_fails_durably_before_message_dispatch(tmp_path):
    from fncbale.errors import OperationFailed

    client, handle, row = await album_client(tmp_path, count=2)
    calls, puts = [], []
    await client.resources.http.aclose()

    async def redirect(request):
        puts.append(await request.aread())
        return httpx.Response(308, headers={"location": "https://other.invalid/?secret=HIDDEN"})

    client.resources.http = httpx.AsyncClient(transport=httpx.MockTransport(redirect), follow_redirects=True)

    async def rpc(method, request, **kwargs):
        calls.append(method)
        assert method == "GetNasimFileUploadUrl"
        return contract(method).response(fileId=len(calls), url="https://signed.invalid/upload")

    async def no_dispatch(*args, **kwargs):
        pytest.fail("Failed upload must never dispatch a message RPC")

    client._rpc, client._call_bytes = rpc, no_dispatch
    try:
        await client.store.recover_operations(client.account)
        client._tasks.append(asyncio.create_task(client._outbox_worker()))
        with pytest.raises(OperationFailed):
            await asyncio.wait_for(handle.wait(), 5)
        current = await client.store.operation(client.account, handle.operation_id)
        assert current["status"] == "failed" and not current["payload"] and current["attempts"] == 0
        saved = json.loads(current["context"])
        assert saved["rids"] == json.loads(row["context"])["rids"]
        assert saved["grouped_id"] == json.loads(row["context"])["grouped_id"]
        assert all(not info.get("file_id") for info in saved["media"])
        assert 1 <= len(puts) <= 2 and all(method == "GetNasimFileUploadUrl" for method in calls)
    finally:
        await client.close()
