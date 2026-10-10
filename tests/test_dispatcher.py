import asyncio
import pytest


from fncbale.dispatcher import FSM, Router
from fncbale.events import Event
from fncbale.models import Peer, PeerKind
from fncbale.storage import Store


async def test_router_filters_and_middleware():
    router, calls = Router(), []

    @router.middleware
    async def middleware(event, next_handler):
        calls.append("before")
        await next_handler(event)
        calls.append("after")

    @router.on("new", predicate=lambda e: e.peer.id == 10)
    async def handle(event):
        calls.append("handler")

    await router.dispatch(Event("id", "edit", Peer(PeerKind.USER, 10), b""))
    assert not calls
    await router.dispatch(Event("id", "new", Peer(PeerKind.USER, 10), b""))
    assert calls == ["before", "handler", "after"]


async def test_fsm_atomic_concurrent_updates(tmp_path):
    store = Store(tmp_path / "db")
    fsm = FSM(store, "a")
    try:
        await fsm.set("counter", 0)
        await asyncio.gather(*[fsm.update("counter", lambda old: old + 1) for _ in range(100)])
        assert await fsm.get("counter") == 100
        assert await FSM(store, "another-account").get("counter") is None
    finally:
        await store.close()


async def test_event_iterator_bound_and_restart_redelivery(tmp_path):
    from fncbale import Client, Config, Session
    from fncbale.events import journal_events
    from fncbale.proto.struct_pb2 import WebUpdate

    client = Client(Session(15, "fake"), data_dir=tmp_path, config=Config(queue_size=2))
    client.account, client._active = "a", True
    try:
        for rid in range(3):
            update = WebUpdate()
            update.message.peer.type, update.message.peer.id = 1, 10
            update.message.rid, update.message.date = rid, 1
            await client.store.record("a", update.SerializeToString(), journal_events(update))
        iterator = client.events()
        first, second = await anext(iterator), await anext(iterator)
        assert len(client._leased_events) == 2
        blocked = asyncio.create_task(anext(iterator))
        await asyncio.sleep(0.1)
        assert not blocked.done()
        await first.ack()
        third = await asyncio.wait_for(blocked, 1)
        assert third.message.rid == 2
        await iterator.aclose()
        again = client.events()
        repeated = await anext(again)
        assert repeated.event_id == second.event_id
        await again.aclose()
    finally:
        await client.close()


async def test_closed_full_conversation_releases_dispatch_and_acks(tmp_path):
    from fncbale import Client, Config, Session, ConversationClosed
    from fncbale.events import journal_events
    from fncbale.proto.struct_pb2 import WebUpdate

    client = Client(Session(15, "synthetic"), data_dir=tmp_path, config=Config(queue_size=1))
    client.account, client._active = "a", True
    handled = []

    @client.router.on("new")
    async def handle(event):
        handled.append(event.message.rid)

    try:
        async with client.conversation(Peer(PeerKind.USER, 10)) as scope:
            for rid in range(3):
                update = WebUpdate()
                update.message.peer.type, update.message.peer.id = 1, 10
                update.message.rid, update.message.date = rid, 1
                await client.store.record("a", update.SerializeToString(), journal_events(update))
            async with asyncio.timeout(3):
                while not (handled == [0] and len(client._leased_events) == 1):
                    await asyncio.sleep(0.01)
            assert scope._queue.full()
        async with asyncio.timeout(3):
            while handled != [0, 1, 2] or client._leased_events:
                await asyncio.sleep(0.01)
        assert not client._conversations
        with pytest.raises(ConversationClosed):
            await scope.receive()
        with pytest.raises(ConversationClosed):
            await scope.send("after closure")
        assert not await client.store.pending_events("a", limit=5)
    finally:
        await client.close()


async def test_conversation_timeout_cancellation_and_disconnect(tmp_path):
    from fncbale import Client, Config, Session, ConversationClosed

    client = Client(Session(15, "synthetic"), data_dir=tmp_path, config=Config(queue_size=1))
    client.account, client._active = "a", True
    try:
        async with client.conversation(Peer(PeerKind.USER, 10), timeout=0.05) as scope:
            with pytest.raises(TimeoutError):
                await scope.receive()
            cancelled = asyncio.create_task(scope.receive())
            await asyncio.sleep(0)
            cancelled.cancel()
            with pytest.raises(asyncio.CancelledError):
                await cancelled
            marker = Event("marker", "new", scope.peer, b"")
            await scope._deliver(marker)
            assert await scope.receive() is marker  # No leaked getter stole this event.
            waiting = asyncio.create_task(scope.receive())
            await asyncio.sleep(0)
            await client.disconnect()
            with pytest.raises(ConversationClosed):
                await waiting
        assert not client._conversations
    finally:
        await client.close()


async def test_failed_conversation_registration_leaves_no_scope(tmp_path):
    from fncbale import Client, Session, BaleError

    client = Client(Session(15, "synthetic"), data_dir=tmp_path)
    client.account, client._active, client._event_consumer = "a", True, True
    try:
        with pytest.raises(BaleError):
            async with client.conversation(Peer(PeerKind.USER, 10)):
                pytest.fail("An explicit iterator already owns delivery")
        assert not client._conversations
    finally:
        await client.close()
