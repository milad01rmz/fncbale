import pytest

from fncbale import Client, Peer, PeerKind, Session, contract
from fncbale.errors import ProtocolError, RpcError, TransportError
from fncbale.proto import struct_pb2 as s

PEER = Peer(PeerKind.CHANNEL, 44, 99)


def test_dedicated_count_primary_wire_and_scalar_zero_presence():
    request = contract("GetGroupMembersCount").request()
    request.group.groupId, request.group.accessHash = 44, 99
    assert request.SerializeToString() == bytes.fromhex("0a04082c1063")
    response = contract("GetGroupMembersCount").response(membersCount=6)
    assert response.SerializeToString() == bytes.fromhex("0806")
    assert type(response)(membersCount=0).SerializeToString() == b""
    with pytest.raises(ValueError):
        response.HasField("membersCount")
    raw = response.SerializeToString() + bytes.fromhex("980609")
    assert type(response).FromString(raw).SerializeToString() == raw
    assert contract("GetGroupMembersCount").readonly


async def count_fixture(tmp_path, value=6, error=None):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    calls = []
    full = s.WebFullGroup(id=44)
    full.membersCount.value = 8

    async def rpc(method, request, **kwargs):
        calls.append(method)
        assert request.group.groupId == 44 and request.group.accessHash == 99
        if error is not None:
            raise error
        return contract(method).response(membersCount=value)

    async def get_full(peer):
        assert peer == PEER
        calls.append("GetFullGroup")
        return full

    client._rpc, client.get_full_group = rpc, get_full
    return client, calls, full


async def test_positive_count_does_not_load_full_metadata(tmp_path):
    client, calls, _ = await count_fixture(tmp_path)
    try:
        assert await client.member_count(PEER) == 6
        assert calls == ["GetGroupMembersCount"]
    finally:
        await client.close()


async def test_scalar_zero_uses_full_presence_and_current_count(tmp_path):
    client, calls, full = await count_fixture(tmp_path, value=0)
    try:
        assert await client.member_count(PEER) == 8  # Do not publish an ambiguous zero.
        full.membersCount.value = 0
        assert await client.member_count(PEER) == 0
        full.ClearField("membersCount")
        with pytest.raises(ProtocolError):
            await client.member_count(PEER)
        assert calls == ["GetGroupMembersCount", "GetFullGroup"] * 3
    finally:
        await client.close()


async def test_unimplemented_alone_uses_same_peer_full_fallback(tmp_path):
    client, calls, _ = await count_fixture(tmp_path, error=RpcError(12, "GetGroupMembersCount"))
    try:
        assert await client.member_count(PEER) == 8
        assert calls == ["GetGroupMembersCount", "GetFullGroup"]
    finally:
        await client.close()


@pytest.mark.parametrize("code", [3, 5, 7, 8, 13, 14, 16])
async def test_other_rpc_errors_never_switch_methods(tmp_path, code):
    client, calls, _ = await count_fixture(tmp_path, error=RpcError(code, "GetGroupMembersCount"))
    try:
        with pytest.raises(RpcError) as caught:
            await client.member_count(PEER)
        assert caught.value.code == code and calls == ["GetGroupMembersCount"]
    finally:
        await client.close()


async def test_negative_count_rejected_without_method_switch(tmp_path):
    client, calls, _ = await count_fixture(tmp_path, value=-1)
    try:
        with pytest.raises(ProtocolError):
            await client.member_count(PEER)
        assert calls == ["GetGroupMembersCount"]
    finally:
        await client.close()


async def test_explicit_full_source_bypasses_dedicated_method_and_validates_inputs(tmp_path):
    client, calls, _ = await count_fixture(tmp_path)
    try:
        assert await client.member_count(PEER, source="full") == 8
        assert calls == ["GetFullGroup"]
        with pytest.raises(ValueError):
            await client.member_count(PEER, source="anything")
        with pytest.raises(ValueError):
            await client.member_count(Peer(PeerKind.USER, 7))
        assert calls == ["GetFullGroup"]
    finally:
        await client.close()


@pytest.mark.parametrize("exhausted", [False, True])
async def test_transport_read_budget_has_fixed_payload_and_no_extra_full_attempt(tmp_path, exhausted):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    calls = []

    async def call(method, payload, route):
        calls.append((method, payload, route))
        if len(calls) <= 2 or exhausted:
            raise TransportError("modeled read failure", possibly_sent=True)
        return contract(method).response(membersCount=12).SerializeToString()

    client._call_bytes = call
    try:
        if exhausted:
            with pytest.raises(TransportError):
                await client.member_count(PEER)
        else:
            assert await client.member_count(PEER) == 12
        assert [call[2] for call in calls] == ["websocket", "websocket", "http"]
        assert len({(call[0], call[1]) for call in calls}) == 1
        assert all(call[0] == "GetGroupMembersCount" for call in calls)
    finally:
        await client.close()


@pytest.mark.parametrize("group_id", [None, 0, 45])
@pytest.mark.parametrize("fallback", [False, True])
async def test_full_group_identity_is_checked_before_count_or_cache_adoption(tmp_path, group_id, fallback):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    client._cache_peer(Peer(PeerKind.CHANNEL, 44, 99, username="expected"))
    calls = []

    async def call(method, payload, route):
        calls.append(method)
        response = contract(method).response()
        if method == "GetFullGroup" and group_id is not None:
            response.fullGroup.id = group_id
            response.fullGroup.membersCount.value = 2
        return response.SerializeToString()

    client._call_bytes = call
    try:
        with pytest.raises(ProtocolError):
            if fallback:
                await client.member_count(PEER)
            else:
                await client.get_full_group(PEER)
        assert calls == (["GetGroupMembersCount", "GetFullGroup"] if fallback else ["GetFullGroup"])
        assert not client._peer_cache
    finally:
        await client.close()
