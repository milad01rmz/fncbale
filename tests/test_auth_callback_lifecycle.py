import asyncio

import pytest

from fncbale import Client, Session
from fncbale.errors import AuthenticationError, ClientClosed
from test_auth_flow import auth_server


@pytest.mark.parametrize("phase", ["code", "password"])
async def test_close_finishes_while_application_auth_input_is_pending(tmp_path, phase):
    client = Client(Session(42, "synthetic-old"), data_dir=tmp_path)
    await client.session_file.save(client.session)
    before = client.session_file.path.read_bytes()
    calls = auth_server(client)
    entered, release = asyncio.Event(), asyncio.Event()

    async def waiting(value):
        entered.set()
        await release.wait()
        return value

    async def code(_):
        return await waiting("code") if phase == "code" else "needs-password"

    async def password():
        return await waiting(" synthetic password ")

    login = asyncio.create_task(client.login("09000000000", code, password_callback=password))
    closing = None
    try:
        await asyncio.wait_for(entered.wait(), 1)
        closing = asyncio.create_task(client.close())
        await asyncio.wait_for(asyncio.shield(closing), 0.5)
        assert client._closed and not login.done()
        release.set()
        with pytest.raises(ClientClosed):
            await login
        expected = ["StartPhoneAuth"] + (["ValidateCode"] if phase == "password" else [])
        assert [name for name, _ in calls] == expected
        assert client.session_file.path.read_bytes() == before
    finally:
        release.set()
        await asyncio.gather(login, *([closing] if closing else []), return_exceptions=True)
        await client.close()


@pytest.mark.parametrize("phase", ["code", "password"])
async def test_application_auth_callback_can_close_its_client(tmp_path, phase):
    client = Client(data_dir=tmp_path)
    calls = auth_server(client)

    async def code(_):
        if phase == "code":
            await client.close()
            return "code"
        return "needs-password"

    async def password():
        await client.close()
        return " synthetic password "

    try:
        with pytest.raises(ClientClosed):
            await asyncio.wait_for(client.login("09000000000", code, password_callback=password), 0.5)
        assert client._closed and not client.session_file.path.exists()
        assert [name for name, _ in calls] == ["StartPhoneAuth"] + (
            ["ValidateCode"] if phase == "password" else []
        )
    finally:
        await client.close()


async def test_late_callback_cannot_replace_a_newer_completed_login(tmp_path):
    client = Client(data_dir=tmp_path)
    calls = auth_server(client)
    entered, release = asyncio.Event(), asyncio.Event()

    async def code(_):
        entered.set()
        await release.wait()
        return "code"

    login = asyncio.create_task(client.login("09000000000", code))
    try:
        await asyncio.wait_for(entered.wait(), 1)
        newer = await asyncio.wait_for(client.start_login("09000000000"), 0.5)
        session = await client.complete_login(newer, "code")
        before = client.session_file.path.read_bytes()
        release.set()
        with pytest.raises(AuthenticationError):
            await login
        assert client.session is session and client.session_file.path.read_bytes() == before
        assert [name for name, _ in calls] == ["StartPhoneAuth", "StartPhoneAuth", "ValidateCode"]
    finally:
        release.set()
        await asyncio.gather(login, return_exceptions=True)
        await client.close()
