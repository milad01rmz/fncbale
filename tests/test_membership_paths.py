import asyncio
import json

import pytest

from fncbale import Client, Peer, PeerKind, Session, contract
from fncbale.errors import DeliveryUncertain, TransportError


async def fixture_client(tmp_path, calls, *, wrong_identity=False, lost_ack=False):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    client.account, client._active = "membership", True

    async def call(method, payload, route):
        calls.append((method, payload, route))
        if lost_ack:
            raise TransportError("modeled lost acknowledgement", possibly_sent=True)
        response = contract(method).response()
        if method in ("JoinGroup", "JoinPublicGroup"):
            response.group.id = 11 if wrong_identity else 10
            response.group.accessHash, response.group.groupType = 99, 1
        else:
            response.url = "https://ble.ir/join/synthetic"
        return response.SerializeToString()

    client._call_bytes = call
    client._tasks.append(asyncio.create_task(client._outbox_worker()))
    return client


def test_public_join_and_invite_url_golden_primary_wire():
    request = contract("JoinPublicGroup").request()
    request.peer.type, request.peer.id = 2, 10
    assert request.SerializeToString() == bytes.fromhex("0a040802100a")
    assert "rid" not in request.DESCRIPTOR.fields_by_name
    assert "randomId" not in request.DESCRIPTOR.fields_by_name
    unknown = request.SerializeToString() + bytes.fromhex("980609")
    assert type(request).FromString(unknown).SerializeToString() == unknown
    invite = contract("GetGroupInviteURL").request()
    invite.groupPeer.groupId, invite.groupPeer.accessHash = 10, 99
    assert invite.SerializeToString() == bytes.fromhex("0a04080a1063")
    response = contract("GetGroupInviteURL").response(url="x")
    assert response.SerializeToString() == bytes.fromhex("0a0178")
    assert contract("GetGroupInviteURL").readonly
    assert not contract("JoinPublicGroup").readonly


async def test_public_join_uses_group_fifo_and_committed_local_replay(tmp_path):
    calls = []
    client = await fixture_client(tmp_path, calls)
    try:
        peer = Peer(PeerKind.CHANNEL, 10, 99)
        result = await client.join_public_group(peer, idempotency_key="join")
        replay = await client.join_public_group(peer, idempotency_key="join")
        assert result.id == replay.id == 10 and result.kind == PeerKind.CHANNEL
        assert len(calls) == 1
        rows = await client.store.run(
            lambda db: db.execute("SELECT peer,context FROM operations").fetchall(), write=False
        )
        assert len(rows) == 1 and rows[0]["peer"] == peer.key
        assert json.loads(rows[0]["context"])["rids"] == []
        url = await client.get_group_invite_url(peer)
        assert url == "https://ble.ir/join/synthetic"
        request = contract("GetGroupInviteURL").request.FromString(calls[-1][1])
        assert request.groupPeer.groupId == 10 and request.groupPeer.accessHash == 99
    finally:
        await client.close()


async def test_public_join_rejects_foreign_ack_identity(tmp_path):
    calls = []
    client = await fixture_client(tmp_path, calls, wrong_identity=True)
    try:
        with pytest.raises(DeliveryUncertain):
            await client.join_public_group(Peer(PeerKind.CHANNEL, 10, 99))
        assert len(calls) == 1 and "2:11" not in client._peer_cache
        row = await client.store.run(
            lambda db: dict(db.execute("SELECT * FROM operations").fetchone()), write=False
        )
        assert row["status"] == "uncertain" and row["attempts"] == 1
    finally:
        await client.close()


async def test_public_join_no_nonce_ack_loss_remains_durable_uncertain(tmp_path):
    calls = []
    client = await fixture_client(tmp_path, calls, lost_ack=True)
    try:
        for _ in range(2):
            with pytest.raises(DeliveryUncertain):
                await client.join_public_group(Peer(PeerKind.CHANNEL, 10), idempotency_key="lost")
        assert len(calls) == 1
        row = await client.store.run(
            lambda db: dict(db.execute("SELECT * FROM operations").fetchone()), write=False
        )
        assert row["status"] == "uncertain" and row["attempts"] == 1
        assert json.loads(row["context"])["rids"] == []
    finally:
        await client.close()


@pytest.mark.parametrize("value", ["", " ", "two tokens", 12, None])
async def test_private_token_invalid_input_does_not_commit_or_send(tmp_path, value):
    calls = []
    client = await fixture_client(tmp_path, calls)
    try:
        with pytest.raises((ValueError, TypeError)):
            await client.join_group(value)
        assert not calls
    finally:
        await client.close()


async def test_user_target_rejected_for_public_join_and_invite_link(tmp_path):
    calls = []
    client = await fixture_client(tmp_path, calls)
    try:
        for function in (client.join_public_group, client.get_group_invite_url):
            with pytest.raises(ValueError):
                await function(Peer(PeerKind.USER, 7, 11))
        assert not calls
    finally:
        await client.close()


@pytest.mark.parametrize("method", ["CreateGroup", "JoinGroup", "JoinPublicGroup"])
async def test_missing_group_ack_never_persists_false_confirmation(tmp_path, method):
    calls = []
    client = await fixture_client(tmp_path, calls)

    async def empty_ack(method, payload, route):
        calls.append((method, payload, route))
        return b""

    client._call_bytes = empty_ack
    try:
        for _ in range(2):
            with pytest.raises(DeliveryUncertain):
                if method == "CreateGroup":
                    await client.create_group("synthetic", idempotency_key="empty")
                elif method == "JoinGroup":
                    await client.join_group("synthetic", idempotency_key="empty")
                else:
                    await client.join_public_group(Peer(PeerKind.CHANNEL, 10), idempotency_key="empty")
        assert len(calls) == 1
        row = await client.store.run(
            lambda db: dict(db.execute("SELECT * FROM operations").fetchone()), write=False
        )
        assert row["status"] == "uncertain" and row["attempts"] == 1 and row["response"] is None
        original_id = row["id"]
        await client.close()
        client = await fixture_client(tmp_path, calls)
        with pytest.raises(DeliveryUncertain) as caught:
            if method == "CreateGroup":
                await client.create_group("synthetic", idempotency_key="empty")
            elif method == "JoinGroup":
                await client.join_group("synthetic", idempotency_key="empty")
            else:
                await client.join_public_group(Peer(PeerKind.CHANNEL, 10), idempotency_key="empty")
        assert caught.value.operation_id == original_id and len(calls) == 1
    finally:
        await client.close()
