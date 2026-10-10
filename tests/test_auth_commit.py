import asyncio
import threading

import pytest

from fncbale import Client, Session, SessionFile
from fncbale.proto import response_pb2 as r


def auth_requests(client):
    async def request(service, method, payload):
        if method == "StartPhoneAuth":
            return r.StartPhoneAuth(transaction_hash="synthetic").SerializeToString()
        response = r.Auth()
        response.user.id, response.jwt.value = 43, "synthetic-new-session"
        return response.SerializeToString()

    client._grpc.request = request


async def code(challenge):
    return "synthetic-code"


async def test_failed_session_commit_preserves_client_identity(tmp_path):
    old = Session(42, "synthetic-old-session")
    client = Client(old, data_dir=tmp_path)
    auth_requests(client)

    async def failed(session):
        raise OSError("synthetic session disk failure")

    client.session_file.save = failed
    try:
        with pytest.raises(OSError):
            await client.login("09000000000", code)
        assert client.session == old and client._grpc._token == old.token
    finally:
        await client.close()


async def test_cancelled_login_waits_for_session_adoption_before_releasing_lifecycle(tmp_path):
    client = Client(Session(42, "synthetic-old-session"), data_dir=tmp_path)
    auth_requests(client)
    entered, release = asyncio.Event(), asyncio.Event()
    original = client.session_file.save

    async def save(session):
        entered.set()
        await release.wait()
        await original(session)

    client.session_file.save = save
    login = asyncio.create_task(client.login("09000000000", code))
    try:
        await entered.wait()
        login.cancel()
        await asyncio.sleep(0.02)
        assert not login.done()
        release.set()
        with pytest.raises(asyncio.CancelledError):
            await login
        saved = await client.session_file.load()
        assert client.session == saved and saved.user_id == 43 and client._grpc._token == saved.token
    finally:
        release.set()
        await client.close()


async def test_session_file_cancellation_drains_blocking_atomic_save(tmp_path, monkeypatch):
    import fncbale.session as module

    entered, release = threading.Event(), threading.Event()
    real_replace = module.os.replace

    def replace(source, destination):
        entered.set()
        assert release.wait(5)
        return real_replace(source, destination)

    monkeypatch.setattr(module.os, "replace", replace)
    file = SessionFile(tmp_path / "session")
    task = asyncio.create_task(file.save(Session(42, "synthetic")))
    try:
        assert await asyncio.to_thread(entered.wait, 5)
        task.cancel()
        await asyncio.sleep(0.02)
        assert not task.done()
        release.set()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert (await file.load()).user_id == 42
        assert not list(tmp_path.glob(".session-*"))
    finally:
        release.set()


async def test_session_replace_failure_preserves_previous_file(tmp_path, monkeypatch):
    import fncbale.session as module

    file = SessionFile(tmp_path / "session")
    old = Session(42, "synthetic-old")
    await file.save(old)

    def fail(*args):
        raise OSError("synthetic rename failure")

    monkeypatch.setattr(module.os, "replace", fail)
    with pytest.raises(OSError):
        await file.save(Session(43, "synthetic-new"))
    assert await file.load() == old and not list(tmp_path.glob(".session-*"))


async def test_changing_account_detaches_old_state_only_after_durable_save(tmp_path):
    import hashlib
    from fncbale import FSM

    client = Client(Session(42, "synthetic-old"), data_dir=tmp_path)
    key = hashlib.sha256(client.config.profile.grpc_url.encode()).hexdigest()[:12]
    old_account = client.account = f"{key}:42"
    old_fsm = client.fsm = FSM(client.store, old_account)
    operation = await client.store.enqueue(old_account, "1:7", "SendMessage", b"", "{}")
    client._progress[operation] = lambda *_: None
    auth_requests(client)
    original = client.session_file.save

    async def failure(_):
        raise OSError("synthetic disk failure")

    try:
        client.session_file.save = failure
        with pytest.raises(OSError):
            await client.login("09000000000", code)
        assert client.account == old_account and client.fsm is old_fsm and operation in client._progress
        client.session_file.save = original
        await client.complete_login(client.login_challenge, "unused validated code")
        assert client.account == f"{key}:43" and client.fsm is None and not client._progress
        assert not [item async for item in client.iter_operations()]
        assert (await client.store.operation(old_account, operation))["status"] == "queued"
    finally:
        await client.close()


async def test_same_account_session_refresh_preserves_operation_context(tmp_path):
    from fncbale import FSM

    client = Client(Session(42, "synthetic-old"), data_dir=tmp_path)
    client.account = "synthetic-account-42"
    fsm = client.fsm = FSM(client.store, client.account)
    callback = client._progress["pending-operation"] = lambda *_: None

    async def request(service, method, payload):
        if method == "StartPhoneAuth":
            return r.StartPhoneAuth(transaction_hash="synthetic").SerializeToString()
        auth = r.Auth()
        auth.user.id, auth.jwt.value = 42, "synthetic-refreshed"
        return auth.SerializeToString()

    client._grpc.request = request
    try:
        await client.login("09000000000", code)
        assert client.account == "synthetic-account-42" and client.fsm is fsm
        assert (
            client._progress["pending-operation"] is callback
            and client.session.token == "synthetic-refreshed"
        )
    finally:
        await client.close()
