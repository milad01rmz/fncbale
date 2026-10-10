import pytest

from fncbale import Client, MessageRef, Peer, PeerKind, Session, contract


@pytest.mark.parametrize("kind", ["history", "albums", "members", "views", "search", "search-messages"])
@pytest.mark.parametrize("boundary", ["identity", "close"])
async def test_buffered_public_stream_ends_at_lifecycle_boundary(tmp_path, kind, boundary):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    client.account = "original"
    peer = Peer(PeerKind.CHANNEL, 10, 12)
    calls = []

    async def rpc(method, request, **kwargs):
        calls.append((method, client.account))
        response = contract(method).response()
        for index in range(3):
            rid, date = index + 1, 50 - index
            if method == "LoadHistory":
                item = response.history.add(rid=rid, date=date)
                item.message.textMessage.text = "synthetic original"
                item.groupedId.value = index + 10
            elif method == "LoadMembers":
                response.members.add(uid=rid)
            elif method == "GetMessagesViews":
                item = response.containers.add()
                item.mId.rid, item.mId.date = rid, date
                item.views.value = 2
            elif method == "SearchMessages":
                value = response.searchResults.add().result
                value.rid, value.date = rid, date
                value.peer.type, value.peer.id = peer.wire_type, peer.id
                item = value.messageContainer
                item.rid, item.date = rid, date
                item.message.textMessage.text = "synthetic original"
            else:
                raise AssertionError(method)
        return response

    client._rpc = rpc
    refs = [MessageRef(peer, i + 1, 50 - i) for i in range(3)]
    streams = {
        "history": lambda: client.iter_history(peer, limit=6, page_size=3),
        "albums": lambda: client.iter_albums(peer, limit=6),
        "members": lambda: client.iter_members(peer, page_size=3),
        "views": lambda: client.iter_views(peer, refs, batch_size=3),
        "search": lambda: client.iter_search(peer, "synthetic"),
        "search-messages": lambda: client.iter_search_messages(peer, "synthetic"),
    }
    stream = streams[kind]()
    try:
        await anext(stream)
        if boundary == "identity":
            client.account = "new-account"
        else:
            await client.close()
        with pytest.raises(StopAsyncIteration):
            await anext(stream)
        assert len(calls) == 1 and calls[0][1] == "original"
    finally:
        await stream.aclose()
        await client.close()


async def test_stale_view_stream_does_not_consume_next_application_input(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    client.account = "original"
    peer = Peer(PeerKind.CHANNEL, 10, 12)
    consumed, requests = [], []

    def source():
        for rid in range(1, 4):
            consumed.append(rid)
            yield MessageRef(peer, rid, rid)

    async def views(*args, **kwargs):
        requests.append(client.account)
        return contract("GetMessagesViews").response()

    client.get_views = views
    stream = client.iter_views(peer, source(), batch_size=1)
    try:
        await anext(stream)
        client.account = "new-account"
        with pytest.raises(StopAsyncIteration):
            await anext(stream)
        assert consumed == [1] and requests == ["original"]
    finally:
        await stream.aclose()
        await client.close()
