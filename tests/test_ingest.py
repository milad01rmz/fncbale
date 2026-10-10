import asyncio

from fncbale import Client, Config, Session
from fncbale.events import UnknownEvent
from fncbale.proto import response_pb2 as r


class Transport:
    def __init__(self):
        self.updates = asyncio.Queue()
        self.disconnected = asyncio.Event()
        self.connected = True
        self.closes = 0

    async def close(self):
        self.closes += 1
        self.connected = False
        self.disconnected.set()

    async def connect(self):
        self.connected = True
        self.disconnected.clear()


async def test_malformed_frame_is_journaled_and_consumer_continues(tmp_path):
    client = Client(Session(11, "synthetic"), data_dir=tmp_path)
    client.account, client._active, client._ws = "a", True, Transport()
    value = r.Response()
    update = value.ws_update.update.composed_update.message
    update.peer.type, update.peer.id, update.rid, update.date = 1, 10, 20, 30
    update.message.textMessage.text = "valid after malformed"
    client._start_ingest()
    try:
        await client._ws.updates.put(b"\xff")
        await client._ws.updates.put(value.SerializeToString())
        await asyncio.wait_for(client._ws.updates.join(), 3)
        iterator = client.events()
        malformed, valid = await anext(iterator), await anext(iterator)
        assert isinstance(malformed, UnknownEvent) and malformed.raw == b"\xff"
        assert valid.message.text == "valid after malformed"
        await malformed.ack()
        await valid.ack()
        await iterator.aclose()
        assert not client._ingest_task.done()
    finally:
        await client.close()


async def test_supervisor_repairs_failed_ingest_even_on_healthy_socket(tmp_path):
    client = Client(Session(11, "synthetic"), data_dir=tmp_path, config=Config(recovery_interval=0.01))
    client.account, client._active, client._ws = "a", True, Transport()

    async def failure():
        raise RuntimeError("synthetic background failure")

    async def recover():
        pass

    client.recover = recover
    failed = asyncio.create_task(failure())
    client._ingest_task = failed
    client._tasks.append(failed)
    supervisor = asyncio.create_task(client._supervise())
    client._tasks.append(supervisor)
    try:
        async with asyncio.timeout(3):
            while client._ingest_task is failed:
                await asyncio.sleep(0.01)
        assert client._ws.closes == 1 and client._ws.connected
        assert not client._ingest_task.done() and failed not in client._tasks
    finally:
        await client.close()


async def test_supervisor_repairs_dispatcher_and_drains_failed_worker_group(tmp_path):
    from fncbale.events import journal_events
    from fncbale.proto.struct_pb2 import WebUpdate

    client = Client(Session(11, "synthetic"), data_dir=tmp_path, config=Config(recovery_interval=0.05))
    client.account, client._active, client._ws = "a", True, Transport()
    handled, failure = [], True

    @client.router.on("new")
    async def handler(event):
        handled.append(event.event_id)

    class BrokenConversation:
        peer = type("Peer", (), {"key": "1:10"})()

        async def _deliver(self, event):
            nonlocal failure
            if failure:
                failure = False
                raise RuntimeError("synthetic unexpected worker fault")

        def close(self):
            pass

    scope = BrokenConversation()
    client._conversations.add(scope)

    async def recover():
        pass

    client.recover = recover
    try:
        update = WebUpdate()
        update.message.peer.type, update.message.peer.id = 1, 10
        update.message.rid, update.message.date = 20, 30
        event_id = (await client.store.record("a", update.SerializeToString(), journal_events(update)))[0]
        failed = client.start_handlers()
        # A worker exception must cancel producer/siblings rather than hang a shard.
        import pytest

        with pytest.raises(ExceptionGroup):
            await asyncio.wait_for(asyncio.shield(failed), 3)
        assert not client._event_consumer and not client._leased_events
        assert handled == []
        supervisor = asyncio.create_task(client._supervise())
        client._tasks.append(supervisor)
        async with asyncio.timeout(3):
            while await client.store.pending_events("a"):
                await asyncio.sleep(0.01)
        assert handled == [event_id]
        assert client._handler_task is not failed and failed not in client._tasks
        assert not client._handler_task.done() and not client._leased_events
    finally:
        await client.close()
