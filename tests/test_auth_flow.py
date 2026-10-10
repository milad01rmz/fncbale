import asyncio

import pytest

from fncbale import Client, Session
from fncbale.errors import AuthenticationError, RpcError
from fncbale.proto import request_pb2 as q, response_pb2 as r


def auth_server(client):
    calls = []

    async def request(service, method, raw):
        payload = getattr(q, method).FromString(raw)
        calls.append((method, payload))
        if method == "StartPhoneAuth":
            return r.StartPhoneAuth(
                transaction_hash="synthetic-private-transaction", sent_code_type=1
            ).SerializeToString()
        if method == "ValidateCode":
            if payload.code == "wrong":
                raise RpcError(3, method, reason="PHONE_CODE_INVALID")
            if payload.code == "needs-password":
                raise RpcError(7, method, reason="password needed for login")
            if payload.code == "denied":
                raise RpcError(7, method, reason="permission denied")
            if payload.code == "empty-auth":
                return r.Auth().SerializeToString()
        if method == "ValidatePassword":
            assert payload.password == " synthetic password "
        auth = r.Auth()
        auth.user.id, auth.jwt.value = 43, "synthetic-new"
        return auth.SerializeToString()

    client._grpc.request = request
    return calls


async def test_callback_password_rpc_challenge(tmp_path):
    client = Client(Session(42, "synthetic-old"), data_dir=tmp_path)
    calls = auth_server(client)

    async def code(challenge):
        # Application mutation of the protobuf must not alter the transaction used.
        challenge.transaction_hash = "application-mutated"
        return "needs-password"

    async def password():
        return " synthetic password "

    try:
        result = await client.login("09000000000", code, password_callback=password)
        assert result.user_id == 43 and await client.session_file.load() == result
        assert [name for name, _ in calls] == ["StartPhoneAuth", "ValidateCode", "ValidatePassword"]
        assert all(p.transaction_hash == "synthetic-private-transaction" for _, p in calls[1:])
        assert all(p.is_jwt.value for _, p in calls[1:])
    finally:
        await client.close()


async def test_staged_wrong_code_and_password_resume_without_new_otp(tmp_path):
    from fncbale import PasswordRequired

    client = Client(data_dir=tmp_path)
    calls = auth_server(client)
    try:
        challenge = await client.start_login("+98 (900) 000-0000")
        assert calls[0][1].phone_number == 989000000000
        assert "synthetic-private" not in repr(challenge)
        with pytest.raises(RpcError) as wrong:
            await client.complete_login(challenge, "wrong")
        assert wrong.value.code == 3
        with pytest.raises(PasswordRequired) as needed:
            await client.complete_login(challenge, "needs-password")
        assert needed.value.challenge is challenge and "synthetic-private" not in str(needed.value)
        count = len(calls)
        with pytest.raises(PasswordRequired):
            await client.complete_login(challenge, "ignored")
        assert len(calls) == count
        result = await client.complete_password_login(challenge, " synthetic password ")
        assert result.user_id == 43 and len(calls) == count + 1
        with pytest.raises(AuthenticationError):
            await client.complete_login(challenge, "replay")
        assert sum(name == "StartPhoneAuth" for name, _ in calls) == 1
    finally:
        await client.close()


@pytest.mark.parametrize("code,error", [("denied", RpcError), ("empty-auth", AuthenticationError)])
async def test_unrelated_error_or_empty_auth_does_not_prompt_password(tmp_path, code, error):
    client = Client(Session(42, "synthetic-old"), data_dir=tmp_path)
    calls = auth_server(client)

    async def callback(_):
        return code

    async def unexpected():
        pytest.fail("Only an explicit server discriminator permits password submission")

    try:
        with pytest.raises(error):
            await client.login("09000000000", callback, password_callback=unexpected)
        assert len(calls) == 2 and client.session.user_id == 42
    finally:
        await client.close()


async def test_challenge_owner_replacement_and_validation_before_rpc(tmp_path):
    client = Client(data_dir=tmp_path / "one")
    other = Client(data_dir=tmp_path / "two")
    calls, other_calls = auth_server(client), auth_server(other)
    try:
        for phone in ("", "letters09000000000", "+98++9000000000", "0", "9" * 16):
            with pytest.raises(ValueError):
                await client.start_login(phone)
        assert not calls
        challenge = await client.start_login("09000000000")
        with pytest.raises(AuthenticationError):
            await other.complete_login(challenge, "code")
        assert not other_calls
        with pytest.raises(ValueError):
            await client.complete_login(challenge, " ")
        with pytest.raises(AuthenticationError):
            await client.complete_password_login(challenge, "password")
        newer = await client.start_login("09000000000")
        with pytest.raises(AuthenticationError):
            await client.complete_login(challenge, "code")
        assert newer is not challenge and len(calls) == 2
        await client.complete_login(newer, " code ")
        assert calls[-1][1].code == "code"
    finally:
        await client.close()
        await other.close()


async def test_validated_auth_disk_retry_does_not_repeat_validation(tmp_path):
    client = Client(Session(42, "synthetic-old"), data_dir=tmp_path)
    calls = auth_server(client)
    original = client.session_file.save

    async def failed(_):
        raise OSError("synthetic disk failure")

    try:
        challenge = await client.start_login("09000000000")
        client.session_file.save = failed
        with pytest.raises(OSError):
            await client.complete_login(challenge, "code")
        assert client.session.user_id == 42 and len(calls) == 2
        client.session_file.save = original
        result = await client.complete_login(challenge, "code")
        assert result.user_id == 43 and len(calls) == 2
    finally:
        await client.close()


async def test_cancelled_code_wait_can_resume_same_challenge(tmp_path):
    client = Client(data_dir=tmp_path)
    calls = auth_server(client)
    entered = asyncio.Event()

    async def waiting(_):
        entered.set()
        await asyncio.Future()

    try:
        login = asyncio.create_task(client.login("09000000000", waiting))
        await entered.wait()
        login.cancel()
        with pytest.raises(asyncio.CancelledError):
            await login
        assert len(calls) == 1 and client._auth_candidate is None
        result = await client.complete_login(client.login_challenge, "code")
        assert result.user_id == 43 and len(calls) == 2
    finally:
        await client.close()


async def test_authentication_uses_shared_pool_rpc_budget(tmp_path):
    from fncbale import Config
    from fncbale.resources import Resources

    config = Config(global_rpc_limit=2)
    resources = Resources(config)
    clients = [Client(data_dir=tmp_path / str(i), config=config, _resources=resources) for i in range(9)]
    active = peak = 0

    async def request(service, method, payload):
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        try:
            await asyncio.sleep(0.01)
            return r.StartPhoneAuth(transaction_hash="synthetic").SerializeToString()
        finally:
            active -= 1

    try:
        for client in clients:
            client._grpc.request = request
        challenges = await asyncio.gather(*(client.start_login("09000000000") for client in clients))
        assert len(challenges) == 9 and peak == 2 and active == 0
    finally:
        await asyncio.gather(*(client.close() for client in clients))
        assert all(client.login_challenge is None for client in clients)
        await resources.close()
