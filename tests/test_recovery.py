from fncbale import Client, Session, contract
from fncbale.proto import struct_pb2 as s


async def test_all_route_recovery_does_not_replace_saved_cursors(tmp_path):
    client = Client(Session(11, "fake"), data_dir=tmp_path)
    client.account = "test"
    first, second = s.WebState(seq=1), s.WebState(seq=2)
    first.groupPeer.groupId, second.groupPeer.groupId = 10, 20
    await client.store.record(
        "test", b"initial", [], [("10", first.SerializeToString(), 1), ("20", second.SerializeToString(), 2)]
    )
    requested, calls = [], 0

    async def rpc(method, request, **kwargs):
        nonlocal calls
        if method == "GetRoutesStates":
            fresh = contract(method).response()
            for old in (first, second):
                value = fresh.seqs.add()
                value.CopyFrom(old)
                value.seq = 100  # Must not overwrite persisted pre-gap cursors.
            return fresh
        requested.append([(state.groupPeer.groupId, state.seq) for state in request.states])
        calls += 1
        response = contract("GetDiff").response()
        for state in request.states:
            batch = response.updates.add()
            batch.state.CopyFrom(state)
            batch.state.seq += 1
            batch.needMore = 1 if calls == 1 else 0
            item = batch.updates.add().messageDelete
            item.peer.type, item.peer.id = 2, state.groupPeer.groupId
            item.rids.append(calls)
        return response

    client._rpc = rpc
    try:
        await client.recover()
        assert requested == [[(10, 1), (20, 2)], [(10, 2), (20, 3)]]
        assert len(await client.store.pending_events("test")) == 4
        assert {r["route"]: r["seq"] for r in await client.store.routes("test")} == {"10": 3, "20": 4}
    finally:
        await client.close()


async def test_first_connection_overflow_recovers_from_pre_websocket_anchor(tmp_path, monkeypatch):
    import asyncio
    import uuid
    from fncbale import Config, ProtocolProfile
    from fncbale.proto import response_pb2 as r

    opened, log, requested = False, [], []

    class Wire:
        def __init__(self, *args):
            self.updates = asyncio.Queue(1)
            self.disconnected = asyncio.Event()
            self.connected = False

        async def connect(self):
            nonlocal opened
            self.connected = True
            self.disconnected.clear()
            if opened:
                return
            opened = True
            for rid in (101, 102):
                update = s.WebUpdate()
                update.message.peer.type, update.message.peer.id = 2, 10
                update.message.rid, update.message.date = rid, 100 + rid
                log.append(update)
                frame = r.Response()
                frame.ws_update.update.composed_update.CopyFrom(update)
                try:
                    self.updates.put_nowait(frame.SerializeToString())
                except asyncio.QueueFull:
                    self.connected = False
                    self.disconnected.set()  # Second live message was not queued.

        async def close(self):
            self.connected = False
            self.disconnected.set()

    monkeypatch.setattr("fncbale.client.WebSocketTransport", Wire)
    client = Client(
        Session(123, "synthetic"),
        data_dir=tmp_path,
        config=Config(profile=ProtocolProfile(grpc_url=f"https://boot-{uuid.uuid4().hex}.invalid")),
    )

    async def rpc(method, request, **kwargs):
        response = contract(method).response()
        if method == "GetRoutesStates":
            state = response.seqs.add(seq=5 + len(log))
            state.groupPeer.groupId = 10
        elif method == "GetDiff":
            requested.append(request.states[0].seq)
            batch = response.updates.add()
            batch.state.groupPeer.groupId, batch.state.seq = 10, 5 + len(log)
            for update in log[max(0, request.states[0].seq - 5) :]:
                batch.updates.add().CopyFrom(update)
        else:
            raise AssertionError(method)
        return response

    client._rpc = rpc
    try:
        await client.connect()
        assert requested[0] == 5  # Not the post-overflow latest state 7.
        async with asyncio.timeout(3):
            while len(await client.store.pending_events(client.account)) < 2:
                await asyncio.sleep(0.01)
        rows = await client.store.pending_events(client.account)
        assert {s.WebUpdate.FromString(row["raw"]).message.rid for row in rows} == {101, 102}
        assert (await client.store.routes(client.account))[0]["seq"] == 7
    finally:
        await client.close()


async def test_too_long_reports_gap(tmp_path):
    client = Client(Session(12, "fake"), data_dir=tmp_path)
    client.account = "test"
    state = s.WebState(seq=1)
    state.groupPeer.groupId = 10
    await client.store.record("test", b"initial", [], [("10", state.SerializeToString(), 1)])

    async def rpc(method, request, **kwargs):
        response = contract(method).response()
        if method == "GetRoutesStates":
            response.seqs.add().CopyFrom(state)
        else:
            batch = response.updates.add()
            batch.state.CopyFrom(state)
            batch.state.seq = 100
            batch.tooLong.value = True
        return response

    client._rpc = rpc
    try:
        await client.recover()
        assert (await client.store.pending_events("test"))[0]["kind"] == "gap"
    finally:
        await client.close()
