import asyncio
from io import BytesIO

from PIL import Image
import pytest

from fncbale import Client, Media, MediaKind, Peer, PeerKind, Session
from fncbale.errors import BaleError


def photos(count):
    buffer = BytesIO()
    Image.new("RGB", (3, 2), "blue").save(buffer, format="PNG")
    return [Media(buffer.getvalue(), MediaKind.PHOTO, filename=f"item-{i}.png") for i in range(count)]


@pytest.mark.parametrize(
    "stage,count", [("resolve", 1), ("prepare", 1), ("resolve", 2), ("prepare", 2), ("second", 2)]
)
async def test_media_never_admits_prepared_content_into_a_changed_account(tmp_path, stage, count):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    client.account, client._active = "original", True
    entered, release = asyncio.Event(), asyncio.Event()
    resolve, prepare = client.resolve_peer, client.media.prepare
    preparations = 0

    async def paused_resolve(*args, **kwargs):
        result = await resolve(*args, **kwargs)
        if stage == "resolve":
            entered.set()
            await release.wait()
        return result

    async def paused_prepare(*args, **kwargs):
        nonlocal preparations
        result = await prepare(*args, **kwargs)
        preparations += 1
        if stage == "prepare" or stage == "second" and preparations == 2:
            entered.set()
            await release.wait()
        return result

    client.resolve_peer, client.media.prepare = paused_resolve, paused_prepare
    items = photos(count)
    call = (
        client.enqueue_media(Peer(PeerKind.CHANNEL, 10), items[0])
        if count == 1
        else client.enqueue_album(Peer(PeerKind.CHANNEL, 10), items)
    )
    task = asyncio.create_task(call)
    try:
        await asyncio.wait_for(entered.wait(), 2)
        # Models disconnect + committed login/reconnect while metadata/file IO is suspended.
        client.account = "new-account"
        release.set()
        with pytest.raises(BaleError, match="account"):
            await asyncio.wait_for(task, 2)
        assert not await client.store.operation_page("original")
        assert not await client.store.operation_page("new-account")
        assert not list((tmp_path / "spool").glob("*.media"))
        assert not client.media.in_use
    finally:
        release.set()
        await asyncio.gather(task, return_exceptions=True)
        await client.close()


async def test_committed_media_handle_keeps_original_account_and_spool(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    client.account, client._active = "original", True
    entered, release = asyncio.Event(), asyncio.Event()
    original = client.store.enqueue

    async def enqueue(*args, **kwargs):
        operation_id = await original(*args, **kwargs)
        entered.set()
        await release.wait()
        return operation_id

    client.store.enqueue = enqueue
    task = asyncio.create_task(
        client.enqueue_media(Peer(PeerKind.CHANNEL, 10), photos(1)[0], progress=lambda *args: None)
    )
    try:
        await asyncio.wait_for(entered.wait(), 2)
        client.account = "new-account"
        release.set()
        handle = await asyncio.wait_for(task, 2)
        with pytest.raises(BaleError, match="account"):
            await handle.status()
        assert not await client.store.operation_page("new-account")
        assert len(await client.store.operation_page("original")) == 1
        assert len(list((tmp_path / "spool").glob("*.media"))) == 1
        assert not client._progress
        client.account = "original"
        assert (await handle.status()).status == "queued"
    finally:
        release.set()
        await asyncio.gather(task, return_exceptions=True)
        await client.close()
