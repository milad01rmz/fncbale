from dataclasses import replace
import asyncio
import threading

import pytest

from fncbale import AccountPool, Client, Config, Media, Peer, PeerKind, Session
from fncbale.errors import PeerKindRequired
from fncbale.proto import struct_pb2 as s


async def test_identity_refresh_removes_old_alias_and_uses_latest_hash(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    try:
        old = client._cache_peer(Peer(PeerKind.CHANNEL, 10, 11, username="old"))
        updated = client._cache_peer(replace(old, username="new", access_hash=22))
        assert "@old" not in client._peer_cache
        assert (await client.resolve_peer("@new")) == updated
        assert (await client.resolve_peer(10)).access_hash == 22
        client._cache_peer(replace(updated, username=None))
        assert "@new" not in client._peer_cache
    finally:
        await client.close()


async def test_expired_identity_does_not_enrich_durable_event(tmp_path, monkeypatch):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path, config=Config(peer_cache_ttl=1))
    update = s.WebUpdate()
    update.message.peer.type, update.message.peer.id = 2, 10
    update.message.rid, update.message.date = 20, 30
    update.message.message.textMessage.text = "raw event"
    row = {"id": "event", "kind": "new", "raw": update.SerializeToString(), "attempts": 0}
    try:
        with monkeypatch.context() as clock:
            clock.setattr("time.monotonic", lambda: 10.0)
            client._cache_peer(Peer(PeerKind.CHANNEL, 10, 99, username="old"))
            clock.setattr("time.monotonic", lambda: 12.0)
            event = client._decode_event(row)
            assert event.peer.access_hash == 0  # Incoming short peer has no hash field.
            assert event.peer.username is None
            assert event.message.text == "raw event" and event.message.rid == 20
    finally:
        await client.close()


async def test_lru_bound_is_by_identity_and_evicts_aliases_together(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path, config=Config(peer_cache_size=2))
    try:
        first = client._cache_peer(Peer(PeerKind.USER, 10, 11, username="first"))
        second = client._cache_peer(Peer(PeerKind.CHANNEL, 20, 22, username="second"))
        assert await client.resolve_peer("@first") == first
        third = client._cache_peer(Peer(PeerKind.USER, 30, 33, username="third"))
        assert first.key in client._peer_cache and third.key in client._peer_cache
        assert second.key not in client._peer_cache and "@second" not in client._peer_cache
        assert client._peer_cache.peer_count == 2 and client._peer_cache.alias_count == 2
        with pytest.raises(PeerKindRequired):
            await client.resolve_peer(20)
        assert await client.resolve_peer(third) == third
    finally:
        await client.close()


async def test_username_reassignment_and_numeric_kind_ambiguity(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    try:
        user = client._cache_peer(Peer(PeerKind.USER, 10, username="shared"))
        channel = client._cache_peer(Peer(PeerKind.CHANNEL, 20, username="shared"))
        assert await client.resolve_peer("@shared") == channel
        assert user.key not in client._peer_cache  # Stale alias owner cannot be reused.
        client._cache_peer(Peer(PeerKind.CHANNEL, 10))
        client._cache_peer(Peer(PeerKind.USER, 10))
        with pytest.raises(PeerKindRequired):
            await client.resolve_peer(10)
    finally:
        await client.close()


async def test_ttl_zero_retains_no_identity_or_alias(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path, config=Config(peer_cache_ttl=0))
    try:
        peer = client._cache_peer(Peer(PeerKind.CHANNEL, 10, 99, username="not-retained"))
        assert not client._peer_cache
        assert await client.resolve_peer(peer) == peer
        with pytest.raises(PeerKindRequired):
            await client.resolve_peer(10)
    finally:
        await client.close()


async def test_close_releases_caches_and_pool_identities_are_account_local(tmp_path):
    pool = AccountPool(data_dir=tmp_path)
    a, b = pool.add("a", Session(1, "synthetic-a")), pool.add("b", Session(2, "synthetic-b"))
    a._cache_peer(Peer(PeerKind.CHANNEL, 10, 11, username="same"))
    b._cache_peer(Peer(PeerKind.USER, 20, 22, username="same"))
    a.media._metadata_cache["synthetic"] = {}
    assert (await a.resolve_peer("@same")).id == 10
    assert (await b.resolve_peer("@same")).id == 20
    await pool.close()
    assert not a._peer_cache and not b._peer_cache and not a.media._metadata_cache


@pytest.mark.parametrize("value", [0, -1, 1.5, True])
def test_peer_cache_size_is_validated(value):
    with pytest.raises((TypeError, ValueError)):
        Config(peer_cache_size=value)


async def test_late_metadata_completion_cannot_refill_closed_client_cache(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    entered, release = asyncio.Event(), threading.Event()
    loop, original = asyncio.get_running_loop(), client.media._extract

    def paused(path, kind):
        loop.call_soon_threadsafe(entered.set)
        assert release.wait(3)
        return original(path, kind)

    client.media._extract = paused
    task = asyncio.create_task(client.media.prepare(Media(b"owned bytes", filename="qa.txt")))
    try:
        await asyncio.wait_for(entered.wait(), 3)
        await asyncio.wait_for(client.close(), 2)
        release.set()
        info = await asyncio.wait_for(task, 3)
        assert info["size"] == len(b"owned bytes")
        assert not client.media._metadata_cache
        assert not client.media.in_use
    finally:
        release.set()
        await asyncio.gather(task, return_exceptions=True)
        await client.close()
