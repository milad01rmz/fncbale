from fncbale import Client, Session, Peer, PeerKind, contract
import asyncio
import json

import pytest

from fncbale import BaleError, MessageRef


async def test_member_cursor_is_opaque_bytes(tmp_path):
    client = Client(Session(13, "fake"), data_dir=tmp_path)
    seen = []

    async def rpc(method, request, **kwargs):
        seen.append(bytes(request.next.value))
        response = contract("LoadMembers").response()
        response.members.add(uid=len(seen))
        if len(seen) == 1:
            response.next.value = b"\x00\xffcursor"
        return response

    client._rpc = rpc
    try:
        members = [m async for m in client.iter_members(Peer(PeerKind.CHANNEL, 10), page_size=5)]
        assert [m.uid for m in members] == [1, 2]
        assert seen == [b"", b"\x00\xffcursor"]
    finally:
        await client.close()


@pytest.mark.parametrize("method", ["members", "search"])
async def test_binary_cursor_cycle_is_rejected(tmp_path, method):
    client = Client(Session(13, "synthetic"), data_dir=tmp_path)
    cursors = [b"\x00\xffa", b"\x80b", b"\x00\xffa"]
    calls = []

    async def rpc(name, request, **kwargs):
        calls.append(request.SerializeToString())
        result = contract(name).response()
        if method == "members":
            result.members.add(uid=7)  # Exact UID duplicates are suppressed.
            result.next.value = cursors[len(calls) - 1]
        else:
            assert request.query.HasField("searchAndCondition")
            assert len(request.query.searchAndCondition.andQuery) == 2
            assert request.query.searchAndCondition.andQuery[0].searchPeerCondition.peer.id == 10
            if name == "SearchMessageMore":
                assert request.query.searchAndCondition.andQuery[1].searchPieceText.query == "فارسی".encode()
                assert request.loadMoreState.value == cursors[len(calls) - 2]
            result.searchResults.add().result.rid = len(calls)
            result.loadMoreState.value = cursors[len(calls) - 1]
        return result

    client._rpc = rpc
    peer = Peer(PeerKind.CHANNEL, 10)
    try:
        with pytest.raises(BaleError, match="cursor did not advance"):
            if method == "members":
                assert [m.uid async for m in client.iter_members(peer)] == [7]
            else:
                [m async for m in client.iter_search(peer, "فارسی")]
        assert len(calls) == 3
    finally:
        await client.close()


async def test_empty_search_page_ends_even_with_server_state(tmp_path):
    client = Client(Session(13, "synthetic"), data_dir=tmp_path)
    calls = []

    async def rpc(name, request, **kwargs):
        calls.append(name)
        response = contract(name).response()
        if len(calls) == 1:
            response.searchResults.add().result.rid = 123
        response.loadMoreState.value = b"\x00\xffterminal-or-next"
        return response

    client._rpc = rpc
    try:
        result = [r async for r in client.iter_search(Peer(PeerKind.CHANNEL, 10), "text")]
        assert [r.result.rid for r in result] == [123]
        assert calls == ["SearchMessages", "SearchMessageMore"]
    finally:
        await client.close()


async def test_secondary_validation_precedes_dispatch(tmp_path):
    client = Client(Session(13, "synthetic"), data_dir=tmp_path)
    calls = []

    async def rpc(name, request, **kwargs):
        calls.append(name)
        return contract(name).response()

    client._rpc = rpc
    peer = Peer(PeerKind.CHANNEL, 10)
    try:
        assert not [r async for r in client.iter_search(peer, "text", limit=0)]
        assert not (await client.get_views(peer, [], increment=True)).containers
        with pytest.raises(ValueError):
            await anext(client.iter_search(peer, "text", limit=-1))
        with pytest.raises(ValueError):
            await client.get_views(peer, [MessageRef(Peer(PeerKind.USER, 10), 1, 2)])
        with pytest.raises(ValueError):
            await client.get_full_user(peer)
        with pytest.raises(ValueError):
            await client.get_dialogs(limit=0)
        assert not calls
        await client.get_views(peer, [MessageRef(peer, (1 << 60) + 1, 20)], increment=False)
        assert calls == ["GetMessagesViews"]
    finally:
        await client.close()


async def test_group_action_uses_target_peer_for_durable_ordering(tmp_path):
    client = Client(Session(13, "synthetic"), data_dir=tmp_path)
    client.account, client._active = "a", True
    peer = Peer(PeerKind.CHANNEL, 44, 99)
    client._cache_peer(peer)
    request = contract("EditGroupTitle").request(title="test", rid=101)
    request.groupPeer.groupId, request.groupPeer.accessHash = peer.id, peer.access_hash
    pending = asyncio.create_task(client.account_action("EditGroupTitle", request))
    try:
        async with asyncio.timeout(3):
            while not client._operation_waiters:
                await asyncio.sleep(0.01)
        row = await client.store.operation("a", next(iter(client._operation_waiters)))
        assert row["peer"] == peer.key and row["payload"] == request.SerializeToString()
        assert json.loads(row["context"])["peer"]["kind"] == "channel"
        await client.store.finish(
            "a", row["id"], "confirmed", response=contract("EditGroupTitle").response().SerializeToString()
        )
        client._notify_operation(row["id"])
        await asyncio.wait_for(pending, 1)
    finally:
        pending.cancel()
        await asyncio.gather(pending, return_exceptions=True)
        await client.close()
