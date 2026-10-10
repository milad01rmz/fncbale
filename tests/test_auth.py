from fncbale import Client, SessionFile
from fncbale.proto import response_pb2 as r, request_pb2 as q


async def test_native_login_and_private_session_roundtrip(tmp_path):
    client = Client(data_dir=tmp_path)
    seen = []

    async def request(service, method, payload):
        seen.append(method)
        if method == "StartPhoneAuth":
            decoded = q.StartPhoneAuth.FromString(payload)
            assert decoded.app_id == 4 and decoded.phone_number == 989000000000
            return r.StartPhoneAuth(transaction_hash="fake-challenge").SerializeToString()
        decoded = q.ValidateCode.FromString(payload)
        assert decoded.transaction_hash == "fake-challenge" and decoded.code == "fake-code"
        auth = r.Auth()
        auth.user.id = 42
        auth.jwt.value = "fake-test-session"
        return auth.SerializeToString()

    client._grpc.request = request

    async def code(challenge):
        assert challenge.transaction_hash == "fake-challenge"
        return "fake-code"

    try:
        session = await client.login("09000000000", code)
        assert session.user_id == 42
        assert (await SessionFile(tmp_path / "account.session").load()) == session
        assert seen == ["StartPhoneAuth", "ValidateCode"]
        assert "fake-test-session" not in repr(session)
    finally:
        await client.close()
