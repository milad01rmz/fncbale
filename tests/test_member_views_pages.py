import itertools

import pytest
from google.protobuf.unknown_fields import UnknownFieldSet

from fncbale import Client, MessageRef, Peer, PeerKind, Session, contract
from fncbale.errors import BaleError, ProtocolError, TransportError
from fncbale.proto import struct_pb2 as s

PEER = Peer(PeerKind.CHANNEL, 44, 99)


async def test_member_count_absent_is_not_reported_as_zero(tmp_path):
    client = Client(Session(42, "synthetic"), data_dir=tmp_path)
    full = s.WebFullGroup()

    async def get_full(peer):
        return full

    client.get_full_group = get_full
    try:
        with pytest.raises(ProtocolError):
            await client.member_count(PEER, source="full")
        full.membersCount.SetInParent()
        assert await client.member_count(PEER, source="full") == 0
        full.membersCount.value = -1
        with pytest.raises(ProtocolError):
            await client.member_count(PEER, source="full")
    finally:
        await client.close()


async def test_member_page_resume_after_fault_preserves_binary_cursor_and_wire(tmp_path):
    client = Client(Session(42, "synthetic"), data_dir=tmp_path)
    calls = []
    next_cursor = b"\x00\xffprivate-cursor\x80"

    async def rpc(method, request, **kwargs):
        calls.append(bytes(request.next.value))
        assert request.group.groupId == 44 and request.group.accessHash == 99
        response = contract(method).response()
        if len(calls) == 1:
            response.members.add(uid=5).isAdmin.SetInParent()
            response.next.value = next_cursor
            return type(response).FromString(response.SerializeToString() + b"\xfa\x3e\x02hi")
        if len(calls) == 2:
            raise TransportError("model read failed")
        response.members.add(uid=6)
        return response

    client._rpc = rpc
    try:
        first = await client.get_member_page(PEER, page_size=1)
        assert first.cursor == b"" and first.next_cursor == next_cursor and not first.complete
        assert first.members[0].HasField("isAdmin")
        assert list(UnknownFieldSet(contract("LoadMembers").response.FromString(first.raw)))
        assert "private-cursor" not in repr(first)
        with pytest.raises(TransportError):
            await client.get_member_page(PEER, cursor=first.next_cursor, page_size=1)
        resumed = await client.get_member_page(PEER, cursor=first.next_cursor, page_size=1)
        assert resumed.complete and resumed.cursor == next_cursor and resumed.members[0].uid == 6
        assert calls == [b"", next_cursor, next_cursor]
    finally:
        await client.close()


async def test_member_iteration_limit_overlap_and_resumed_cursor_cycle(tmp_path):
    client = Client(Session(42, "synthetic"), data_dir=tmp_path)
    calls = []

    async def rpc(method, request, **kwargs):
        calls.append(bytes(request.next.value))
        response = contract(method).response()
        response.members.add(uid=5)
        response.members.add(uid=6 if not request.next.value else 7)
        response.next.value = b"next"
        return response

    client._rpc = rpc
    try:
        assert not [m async for m in client.iter_members(PEER, limit=0)]
        assert not calls
        assert [m.uid async for m in client.iter_members(PEER, limit=3)] == [5, 6, 7]
        assert calls == [b"", b"next"]
        with pytest.raises(BaleError, match="cursor did not advance"):
            [m async for m in client.iter_members(PEER, cursor=b"next")]
        assert len(calls) == 3  # Detect return to the starting cursor on the first resumed page.
        for kwargs in ({"cursor": "text"}, {"page_size": 0}, {"limit": -1}):
            with pytest.raises(ValueError):
                await anext(client.iter_members(PEER, **kwargs))
        with pytest.raises(ValueError):
            await client.get_member_page(PEER, cursor="text")
        assert len(calls) == 3
    finally:
        await client.close()


async def test_view_stream_order_presence_duplicates_and_unknown_fields(tmp_path):
    client = Client(Session(42, "synthetic"), data_dir=tmp_path)
    refs = [MessageRef(PEER, i, 1000 + i) for i in range(1, 5)]
    calls = []

    async def rpc(method, request, **kwargs):
        assert method == "GetMessagesViews" and not request.increment
        calls.append([item.rid for item in request.mids])
        response = contract(method).response()
        for mid in reversed(request.mids):
            if mid.rid == 4:
                continue  # Missing record is unknown, not zero.
            item = response.containers.add()
            item.mId.CopyFrom(mid)
            item.mId.seq = 23  # A caller seq=0 is unspecified, not a fabricated server sequence.
            if mid.rid != 3:
                item.views.value = 0 if mid.rid == 1 else 17
            item.MergeFromString(b"\xfa\x3e\x02hi")
        return response

    client._rpc = rpc
    try:
        values = [v async for v in client.iter_views(PEER, [refs[0], refs[0], *refs[1:]], batch_size=3)]
        assert calls == [[1, 2], [3, 4]]
        assert [v.ref.rid for v in values] == [1, 1, 2, 3, 4]
        assert [v.count for v in values] == [0, 0, 17, None, None]
        assert [v.available for v in values] == [True, True, True, False, False]
        assert values[3].raw and not values[4].raw
        assert list(UnknownFieldSet(s.WebT_THn.FromString(values[0].raw)))
    finally:
        await client.close()


@pytest.mark.parametrize("mode", ["conflicting", "negative", "wrong-sequence"])
async def test_view_stream_never_invents_counts_for_invalid_or_unmatched_records(tmp_path, mode):
    client = Client(Session(42, "synthetic"), data_dir=tmp_path)

    async def rpc(method, request, **kwargs):
        response = contract(method).response()
        item = response.containers.add()
        item.mId.CopyFrom(request.mids[0])
        item.views.value = -1 if mode == "negative" else 3
        if mode == "conflicting":
            response.containers.add().CopyFrom(item)
            response.containers[-1].views.value = 4
        if mode == "wrong-sequence":
            item.mId.seq += 1
        return response

    client._rpc = rpc
    try:
        iterator = client.iter_views(PEER, [MessageRef(PEER, 1, 2, 7)])
        if mode == "wrong-sequence":
            assert (await anext(iterator)).count is None
            await iterator.aclose()
        else:
            with pytest.raises(ProtocolError):
                await anext(iterator)
    finally:
        await client.close()


async def test_view_stream_bounded_consumption_and_validation_before_each_batch(tmp_path):
    client = Client(Session(42, "synthetic"), data_dir=tmp_path)
    consumed = 0
    calls = []

    def source():
        nonlocal consumed
        for i in itertools.count(1):
            consumed += 1
            yield MessageRef(PEER, i, i + 10)

    async def rpc(method, request, **kwargs):
        calls.append(len(request.mids))
        return contract(method).response()

    client._rpc = rpc
    try:
        iterator = client.iter_views(PEER, source(), batch_size=7)
        assert (await anext(iterator)).count is None
        await iterator.aclose()
        assert consumed == 7 and calls == [7]
        for invalid in (
            MessageRef(PEER, 0, 1),
            MessageRef(PEER, 1, 0),
            MessageRef(PEER, 1, 1, -1),
            MessageRef(Peer(PeerKind.USER, 44), 1, 2),
        ):
            with pytest.raises(ValueError):
                await anext(client.iter_views(PEER, [invalid]))
        assert calls == [7]
        for size in (0, 101):
            with pytest.raises(ValueError):
                await anext(client.iter_views(PEER, [], batch_size=size))
        assert calls == [7]
    finally:
        await client.close()
