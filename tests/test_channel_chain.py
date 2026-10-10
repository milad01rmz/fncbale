import asyncio

import pytest

from examples.channel_chain import DestinationFence, poll_recent, seed_recent
from fncbale import Client, PeerKind, Session, contract
from fncbale.errors import PeerNotFound, RpcError
from fncbale.proto import struct_pb2 as s


@pytest.mark.parametrize("method", ["SendMessage", "SendMultiMediaMessage", "UpdateMessage", "DeleteMessage"])
def test_chain_never_mutates_upstream_or_unknown_destinations(method):
    fence = DestinationFence((100, 200))
    request = contract(method).request()
    request.peer.type = 3 if method == "SendMultiMediaMessage" else 2
    for peer_id in (300, 0):
        request.peer.id = peer_id
        with pytest.raises(RpcError):
            fence.check(method, request.SerializeToString())
    for peer_id in (100, 200):
        request.peer.id = peer_id
        assert fence.check(method, request.SerializeToString()) == peer_id
    request.peer.type = 1
    with pytest.raises(RpcError):
        fence.check(method, request.SerializeToString())


def test_chain_rejects_unrelated_mutations_and_allows_source_history_reads():
    fence = DestinationFence((100, 200))
    for method in ("ForwardMessages", "JoinPublicGroup", "SetRestriction", "GetNasimFileUploadUrl"):
        with pytest.raises(RpcError):
            fence.check(method, contract(method).request().SerializeToString())
    assert fence.check("LoadHistory", contract("LoadHistory").request().SerializeToString()) is None


@pytest.mark.parametrize("matching", [True, False])
async def test_search_user_references_hydrate_typed_peers_before_exact_match(tmp_path, matching):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    called = []

    async def rpc(method, request, **kwargs):
        called.append(method)
        response = contract(method).response()
        if method in ("SearchPeer", "SearchContacts"):
            response.userPeers.add(uid=20, accessHash=30)
        elif method == "LoadUsers":
            assert list(request.peers) == [s.WebUserPeer(uid=20, accessHash=30)]
            user = response.users.add(id=20, accessHash=30)
            user.nick.value = "exact" if matching else "unrelated"
        return response

    client._rpc = rpc
    try:
        if matching:
            peer = await client.resolve_peer("@exact")
            assert peer.kind == PeerKind.USER and peer.id == 20 and peer.access_hash == 30
        else:
            with pytest.raises(PeerNotFound):
                await client.resolve_peer("@exact")
        assert "LoadUsers" in called
    finally:
        await client.close()


async def test_recent_seed_counts_albums_as_posts_and_restart_does_not_resend():
    class Mirror:
        def __init__(self):
            self.lock = asyncio.Lock()
            self.state = {}
            self.delivered = []

        async def get(self, key):
            return self.state.get(key)

        async def put(self, key, value):
            self.state[key] = value

        async def history(self):
            rows = [s.WebHistory(rid=index, date=index) for index in range(1, 6)]
            for row in rows[2:4]:
                row.groupedId.value = 100
            return rows

        async def deliver(self, rows):
            self.delivered.append([row.rid for row in rows])

        def report(self, **kwargs):
            pass

    mirror = Mirror()
    await seed_recent(mirror, 2)
    assert mirror.delivered == [[3, 4], [5]]
    assert mirror.state["chain-seeded"] == {"posts": 2, "items": 3, "since": 3}
    await seed_recent(mirror, 2)
    assert mirror.delivered == [[3, 4], [5]]


async def test_poll_reports_unmapped_late_album_sibling_instead_of_ignoring_it():
    class Mirror:
        lock = asyncio.Lock()

        async def get(self, key):
            return {"since": 1}

        async def history(self):
            rows = [s.WebHistory(rid=1, date=1), s.WebHistory(rid=2, date=2)]
            for row in rows:
                row.groupedId.value = 100
            return rows

        async def mapping(self, rid):
            return {"content_hash": "same"} if rid == 1 else None

        def content_hash(self, wire):
            return "same"

        async def deliver(self, items):
            assert [row.rid for row in items] == [1, 2]
            raise ValueError("Source album expanded; explicit repair required")

    with pytest.raises(ValueError, match="expanded"):
        await poll_recent(Mirror())
