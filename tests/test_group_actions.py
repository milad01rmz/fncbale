import asyncio
from dataclasses import replace

import pytest

from fncbale import Client, Config, Peer, PeerKind, Session, contract
from fncbale.errors import DeliveryUncertain, IdempotencyConflict, TransportError


async def action_client(tmp_path, calls):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path, config=Config(outbox_workers=1))
    client.account, client._active = "a", True

    async def call(method, payload, route):
        calls.append((method, payload, route))
        response = contract(method).response()
        if method in ("CreateGroup", "JoinGroup"):
            response.group.id, response.group.accessHash = 10, 99
            response.group.title, response.group.groupType = "created", 1
        return response.SerializeToString()

    client._call_bytes = call
    client._tasks.append(asyncio.create_task(client._outbox_worker()))
    return client


async def test_action_nonce_is_frozen_caller_unchanged_and_idem_replay(tmp_path):
    calls = []
    client = await action_client(tmp_path, calls)
    request = contract("EditGroupTitle").request(title="new")
    request.groupPeer.groupId = 10
    try:
        one = await client.enqueue_account_action("EditGroupTitle", request, idempotency_key="one")
        await one.wait()
        two = await client.enqueue_account_action("EditGroupTitle", request, idempotency_key="one")
        await two.wait()
        assert one.operation_id == two.operation_id and request.rid == 0 and len(calls) == 1
        frozen = contract("EditGroupTitle").request.FromString(calls[0][1])
        assert frozen.rid > 0
        request.title = "changed"
        with pytest.raises(IdempotencyConflict):
            await client.enqueue_account_action("EditGroupTitle", request, idempotency_key="one")
    finally:
        await client.close()


async def test_group_builders_validate_targets_use_hashes_and_clear_cache(tmp_path):
    calls = []
    client = await action_client(tmp_path, calls)
    try:
        created = await client.create_channel("new", username="@initial")
        created = client._cache_peer(replace(created, username="initial"))
        create = contract("CreateGroup").request.FromString(calls[-1][1])
        assert create.groupType == 1 and create.rid > 0 and create.nick.value == "initial"
        assert create.restriction == 1
        await client.edit_group_title(created, "changed")
        await client.edit_group_about(created, "")
        about = contract("EditGroupAbout").request.FromString(calls[-1][1])
        assert about.HasField("about") and about.about.value == ""
        assert about.groupPeer.accessHash == 99 and about.rid > 0
        updated = await client.edit_channel_username(created, "@updated")
        nick = contract("EditChannelNick").request.FromString(calls[-1][1])
        assert nick.randomId > 0 and updated.username == "updated"
        assert "@initial" not in client._peer_cache
        user = Peer(PeerKind.USER, 7, 123)
        await client.invite_user(created, user)
        invite = contract("InviteUser").request.FromString(calls[-1][1])
        assert invite.user.uid == 7 and invite.user.accessHash == 123 and invite.rid > 0
        await client.kick_user(created, user)
        await client.leave_group(created, make_orphan=True)
        leave = contract("LeaveGroup").request.FromString(calls[-1][1])
        assert leave.rid > 0 and leave.makeOrphan.value and created.key not in client._peer_cache
        before = len(calls)
        with pytest.raises(ValueError):
            await client.create_group("new", members=[created])
        with pytest.raises(ValueError):
            await client.edit_group_title(user, "invalid")
        with pytest.raises(ValueError):
            await client.invite_user(created, created)
        assert len(calls) == before
    finally:
        await client.close()


async def test_partial_group_creation_exposes_created_peer_without_recreating(tmp_path):
    from fncbale import GroupCreationIncomplete

    calls = []
    client = await action_client(tmp_path, calls)

    async def partial(method, payload, route):
        calls.append(payload)
        response = contract(method).response()
        response.group.id, response.group.accessHash = 10, 99
        response.notAddedUserPeers.add(uid=7)
        return response.SerializeToString()

    client._call_bytes = partial
    try:
        for _ in range(2):
            with pytest.raises(GroupCreationIncomplete) as caught:
                await client.create_group("new", members=[Peer(PeerKind.USER, 7)], idempotency_key="create")
            assert caught.value.peer.id == 10 and caught.value.rejected_user_ids == (7,)
        assert len(calls) == 1
    finally:
        await client.close()


async def test_uncertain_admin_write_is_not_reissued_with_a_fresh_nonce(tmp_path):
    calls = []
    client = await action_client(tmp_path, calls)

    async def lost(method, payload, route):
        calls.append(payload)
        raise TransportError("model ACK loss", possibly_sent=True)

    client._call_bytes = lost
    try:
        with pytest.raises(DeliveryUncertain):
            await client.edit_group_title(Peer(PeerKind.CHANNEL, 10), "one")
        assert len(calls) == 1
        assert contract("EditGroupTitle").request.FromString(calls[0]).rid > 0
    finally:
        await client.close()


def test_visibility_wire_matches_primary_tags_and_wrapper_presence():
    request = contract("SetRestriction").request(restriction=1)
    request.groupOutPeer.groupId, request.groupOutPeer.accessHash = 10, 99
    request.nick.value = "qa123"
    assert request.SerializeToString() == bytes.fromhex("0a04080a106310011a070a057161313233")
    private = contract("SetRestriction").request()
    private.groupOutPeer.CopyFrom(request.groupOutPeer)
    private.nick.SetInParent()
    assert private.SerializeToString() == bytes.fromhex("0a04080a10631a00")
    unknown = private.SerializeToString() + b"\x20\x09"
    assert type(private).FromString(unknown).SerializeToString() == unknown


async def test_explicit_visibility_is_durable_group_scoped_and_preserves_nonce_absence(tmp_path):
    calls = []
    client = await action_client(tmp_path, calls)
    peer = Peer(PeerKind.CHANNEL, 10, 99, username="old")
    client._cache_peer(peer)
    try:
        updated = await client.set_group_visibility(
            peer, public=True, username="@qa123", idempotency_key="public"
        )
        assert updated.username == "qa123" and "@old" not in client._peer_cache
        request = contract("SetRestriction").request.FromString(calls[-1][1])
        assert (
            request.restriction == 1
            and request.nick.value == "qa123"
            and request.groupOutPeer.accessHash == 99
        )
        assert (
            "rid" not in request.DESCRIPTOR.fields_by_name
            and "randomId" not in request.DESCRIPTOR.fields_by_name
        )
        rows = await client.store.run(
            lambda db: db.execute(
                "SELECT peer FROM operations WHERE account=?", (client.account,)
            ).fetchall(),
            write=False,
        )
        assert len(rows) == 1 and rows[0]["peer"] == peer.key
        replay = await client.set_group_visibility(
            peer, public=True, username="@qa123", idempotency_key="public"
        )
        assert replay.id == peer.id and len(calls) == 1
        private = await client.set_group_visibility(updated, public=False)
        request = contract("SetRestriction").request.FromString(calls[-1][1])
        assert request.restriction == 0 and request.HasField("nick") and not request.nick.value
        assert private.username is None and "@qa123" not in client._peer_cache
    finally:
        await client.close()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"public": 1},
        {"public": True},
        {"public": True, "username": "a b"},
        {"public": False, "username": "x"},
    ],
)
async def test_visibility_rejects_ambiguous_or_invalid_intent_before_rpc(tmp_path, kwargs):
    calls = []
    client = await action_client(tmp_path, calls)
    try:
        with pytest.raises((TypeError, ValueError)):
            await client.set_group_visibility(Peer(PeerKind.CHANNEL, 10), **kwargs)
        assert not calls
    finally:
        await client.close()


async def test_visibility_without_server_nonce_stays_uncertain_after_lost_ack(tmp_path):
    calls = []
    client = await action_client(tmp_path, calls)

    async def lost(method, payload, route):
        calls.append(payload)
        raise TransportError("ACK lost", possibly_sent=True)

    client._call_bytes = lost
    try:
        with pytest.raises(DeliveryUncertain):
            await client.set_group_visibility(Peer(PeerKind.CHANNEL, 10, 99), public=True, username="qa123")
        assert len(calls) == 1
    finally:
        await client.close()


async def test_profile_actions_keep_presence_durable_replay_and_self_order(tmp_path):
    calls = []
    client = await action_client(tmp_path, calls)
    own = client._cache_peer(Peer(PeerKind.USER, 1, username="old"))
    other = client._cache_peer(Peer(PeerKind.USER, 7, username="other"))
    try:
        name = await client.enqueue_edit_profile_name("نام فارسی 🧪", idempotency_key="name")
        assert own.key not in client._peer_cache and "@old" not in client._peer_cache
        assert other.key in client._peer_cache
        await name.wait()
        replay = await client.enqueue_edit_profile_name("نام فارسی 🧪", idempotency_key="name")
        await replay.wait()
        assert replay.operation_id == name.operation_id and len(calls) == 1
        row = await client.store.operation(client.account, name.operation_id)
        assert (
            row["peer"] == own.key and not contract("EditName").request.FromString(row["payload"]).name == ""
        )
        with pytest.raises(IdempotencyConflict):
            await client.enqueue_edit_profile_name("different", idempotency_key="name")
        await client.edit_profile_about("")
        assert contract("EditAbout").request.FromString(calls[-1][1]).HasField("about")
        await client.edit_profile_about(None)
        assert not contract("EditAbout").request.FromString(calls[-1][1]).HasField("about")
        await client.edit_profile_username("@new")
        assert contract("EditNickName").request.FromString(calls[-1][1]).nickname.value == "new"
        await client.edit_profile_username(None)
        assert not contract("EditNickName").request.FromString(calls[-1][1]).HasField("nickname")
        before = len(calls)
        for invalid in (None, "", "   "):
            with pytest.raises(ValueError):
                await client.edit_profile_name(invalid)
        with pytest.raises(TypeError):
            await client.edit_profile_about(123)
        with pytest.raises(ValueError):
            await client.edit_profile_username("@two names")
        assert len(calls) == before
    finally:
        await client.close()


async def test_profile_ack_loss_stays_inspectable_without_retransmission(tmp_path):
    calls = []
    client = await action_client(tmp_path, calls)

    async def lost(method, payload, route):
        calls.append((method, payload))
        raise TransportError("model ACK loss", possibly_sent=True)

    client._call_bytes = lost
    try:
        handle = await client.enqueue_edit_profile_about("new about", idempotency_key="lost")
        with pytest.raises(DeliveryUncertain):
            await handle.wait()
        again = await client.enqueue_edit_profile_about("new about", idempotency_key="lost")
        assert again.operation_id == handle.operation_id
        assert (await client.get_operation(handle.operation_id)).status == "uncertain"
        assert len(calls) == 1
    finally:
        await client.close()


@pytest.mark.parametrize("builder", [True, False])
async def test_cancelled_committed_profile_admission_invalidates_stale_self(tmp_path, builder):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    client.account, client._active = "a", True
    own = client._cache_peer(Peer(PeerKind.USER, 1, username="old"))
    other = client._cache_peer(Peer(PeerKind.USER, 7, username="other"))
    committed = asyncio.Event()
    original, operation_ids = client.store.enqueue, []

    async def enqueue(*args, **kwargs):
        operation_ids.append(await original(*args, **kwargs))
        committed.set()
        await asyncio.Event().wait()

    client.store.enqueue = enqueue
    request = contract("EditNickName").request()
    request.nickname.value = "new"
    task = asyncio.create_task(
        client.enqueue_edit_profile_username("@new", idempotency_key="cancel-admission")
        if builder
        else client.enqueue_account_action("EditNickName", request, idempotency_key="cancel-admission")
    )
    try:
        await asyncio.wait_for(committed.wait(), 3)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert own.key not in client._peer_cache and "@old" not in client._peer_cache
        assert other.key in client._peer_cache and "@other" in client._peer_cache
        operation = await client.get_operation(operation_ids[0])
        assert operation.status == "queued"
        client.store.enqueue = original
        replay = await client.enqueue_edit_profile_username("@new", idempotency_key="cancel-admission")
        assert replay.operation_id == operation.operation_id
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        await client.close()


async def test_rejected_profile_intent_keeps_cache_and_accepted_operation(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    client.account, client._active = "a", True
    try:
        handle = await client.enqueue_edit_profile_name("original", idempotency_key="fixed")
        peer = client._cache_peer(Peer(PeerKind.USER, 1, username="cached"))
        with pytest.raises(IdempotencyConflict):
            await client.enqueue_edit_profile_name("different", idempotency_key="fixed")
        assert peer.key in client._peer_cache and "@cached" in client._peer_cache
        assert (await client.get_operation(handle.operation_id)).status == "queued"
    finally:
        await client.close()
