import asyncio

import pytest

from fncbale import Client, Config, Session
from fncbale.errors import BaleError, ClientClosed
from fncbale.events import journal_events
from fncbale.proto.struct_pb2 import WebUpdate


async def setup_client(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path, config=Config(queue_size=2))
    client.account, client._active = "a", True
    update = WebUpdate()
    update.message.peer.type, update.message.peer.id = 1, 10
    update.message.rid, update.message.date = 1, 1
    ids = await client.store.record("a", update.SerializeToString(), journal_events(update))
    return client, ids[0]


async def test_handler_reserves_consumer_before_task_first_runs(tmp_path):
    client, event_id = await setup_client(tmp_path)
    handled = asyncio.Event()

    @client.router.on("new")
    async def handler(event):
        assert event.event_id == event_id
        handled.set()

    iterator = client.events()
    try:
        task = client.start_handlers()
        assert client.start_handlers() is task
        with pytest.raises(BaleError):
            await anext(iterator)
        await asyncio.wait_for(handled.wait(), 2)
        assert not task.done()
    finally:
        await iterator.aclose()
        await client.close()


async def test_cancel_before_first_handler_step_releases_reservation(tmp_path):
    client, event_id = await setup_client(tmp_path)
    iterator = None
    try:
        task = client.start_handlers()
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        assert not client._event_consumer
        iterator = client.events()
        event = await asyncio.wait_for(anext(iterator), 2)
        assert event.event_id == event_id
        await event.ack()
    finally:
        if iterator is not None:
            await iterator.aclose()
        await client.close()


async def test_closed_client_cannot_start_untracked_handler_task(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    await client.close()
    with pytest.raises(ClientClosed):
        client.start_handlers()


async def test_old_iterator_finally_cannot_release_new_consumer_after_disconnect(tmp_path):
    client, event_id = await setup_client(tmp_path)
    old, new = client.events(), None
    try:
        assert (await anext(old)).event_id == event_id
        await client.disconnect()
        client._active = True  # Model a successful reconnect without network.
        new = client.events()
        delivered = await asyncio.wait_for(anext(new), 2)
        assert delivered.event_id == event_id
        await old.aclose()
        assert client._event_consumer and event_id in client._leased_events
        await delivered.ack()
    finally:
        await old.aclose()
        if new is not None:
            await new.aclose()
        await client.close()


async def test_ack_is_bound_to_inbox_account_when_client_identity_changes(tmp_path):
    client, event_id = await setup_client(tmp_path)
    iterator = client.events()
    try:
        event = await anext(iterator)
        client.account = "b"  # Exercise the post-authentication account detach boundary.
        await event.ack()
        rows = await client.store.run(
            lambda db: [dict(row) for row in db.execute("SELECT account,id,status FROM inbox")],
            write=False,
        )
        assert rows == [{"account": "a", "id": event_id, "status": "acked"}]
    finally:
        await iterator.aclose()
        await client.close()


async def test_old_stream_cannot_yield_cached_batch_from_another_account(tmp_path):
    client, _ = await setup_client(tmp_path)
    update = WebUpdate()
    update.message.peer.type, update.message.peer.id = 1, 10
    update.message.rid, update.message.date = 2, 2
    await client.store.record("a", update.SerializeToString(), journal_events(update))
    iterator = client.events()
    try:
        assert (await anext(iterator)).message.rid == 1
        client.account = "b"
        with pytest.raises(StopAsyncIteration):
            await anext(iterator)
        assert not client._leased_events and not client._event_consumer
    finally:
        await iterator.aclose()
        await client.close()


async def test_handler_retains_ownership_until_worker_cleanup_finishes(tmp_path):
    client, event_id = await setup_client(tmp_path)
    entered, cleaning, finish = asyncio.Event(), asyncio.Event(), asyncio.Event()

    @client.router.on("new")
    async def handler(event):
        entered.set()
        try:
            await asyncio.Event().wait()
        finally:
            cleaning.set()
            await finish.wait()

    iterator, replay = client.events(), None
    task = client.start_handlers()
    try:
        await asyncio.wait_for(entered.wait(), 2)
        task.cancel()
        await asyncio.wait_for(cleaning.wait(), 2)
        with pytest.raises(BaleError):
            await anext(iterator)
        finish.set()
        await asyncio.gather(task, return_exceptions=True)
        replay = client.events()
        event = await asyncio.wait_for(anext(replay), 2)
        assert event.event_id == event_id
        await event.ack()
    finally:
        finish.set()
        await asyncio.gather(task, return_exceptions=True)
        await iterator.aclose()
        if replay is not None:
            await replay.aclose()
        await client.close()


async def test_failed_task_creation_closes_coroutine_and_releases_owner(tmp_path, monkeypatch):
    client, _ = await setup_client(tmp_path)
    attempted = []

    def reject(coroutine, **kwargs):
        attempted.append(coroutine)
        raise RuntimeError("modeled task creation failure")

    try:
        with monkeypatch.context() as patch:
            patch.setattr(asyncio, "create_task", reject)
            with pytest.raises(RuntimeError):
                client.start_handlers()
        assert len(attempted) == 1 and attempted[0].cr_frame is None
        assert not client._event_consumer and not client._tasks
    finally:
        for coroutine in attempted:
            coroutine.close()
        await client.close()


@pytest.mark.parametrize("stop", ["disconnect", "close"])
async def test_direct_run_handlers_shutdown_waits_for_worker_cleanup(tmp_path, stop):
    client, event_id = await setup_client(tmp_path)
    entered, cleaning, finish = asyncio.Event(), asyncio.Event(), asyncio.Event()

    @client.router.on("new")
    async def handler(event):
        entered.set()
        try:
            await asyncio.Event().wait()
        finally:
            cleaning.set()
            await finish.wait()

    caller = asyncio.create_task(client.run_handlers())
    disconnected, replay = None, None
    try:
        await asyncio.wait_for(entered.wait(), 2)
        disconnected = asyncio.create_task(getattr(client, stop)())
        await asyncio.wait_for(cleaning.wait(), 2)
        assert not disconnected.done(), "shutdown returned before direct handler cleanup"
        assert client._event_consumer
        finish.set()
        await asyncio.wait_for(disconnected, 2)
        await asyncio.gather(caller, return_exceptions=True)
        assert not client._event_consumer
        if stop == "close":
            client = Client(Session(1, "synthetic"), data_dir=tmp_path)
            client.account = "a"
        client._active = True
        replay = client.events()
        assert (await asyncio.wait_for(anext(replay), 2)).event_id == event_id
    finally:
        finish.set()
        caller.cancel()
        await asyncio.gather(caller, return_exceptions=True)
        if disconnected is not None:
            await asyncio.gather(disconnected, return_exceptions=True)
        if replay is not None:
            await replay.aclose()
        await client.close()


async def test_cancelling_direct_caller_waits_for_tracked_child_cleanup(tmp_path):
    client, event_id = await setup_client(tmp_path)
    entered, cleaning, finish = asyncio.Event(), asyncio.Event(), asyncio.Event()

    @client.router.on("new")
    async def handler(event):
        entered.set()
        try:
            await asyncio.Event().wait()
        finally:
            cleaning.set()
            await finish.wait()

    caller = asyncio.create_task(client.run_handlers())
    replay = None
    try:
        await asyncio.wait_for(entered.wait(), 2)
        child = client._handler_task
        assert child is not caller and child in client._tasks
        caller.cancel()
        await asyncio.wait_for(cleaning.wait(), 2)
        assert not caller.done() and client._event_consumer
        finish.set()
        with pytest.raises(asyncio.CancelledError):
            await caller
        assert child.done() and not client._event_consumer
        replay = client.events()
        assert (await asyncio.wait_for(anext(replay), 2)).event_id == event_id
    finally:
        finish.set()
        caller.cancel()
        await asyncio.gather(caller, return_exceptions=True)
        if replay is not None:
            await replay.aclose()
        await client.close()


async def test_direct_handler_failure_reports_to_caller_and_releases_owner(tmp_path, monkeypatch):
    client, _ = await setup_client(tmp_path)
    failure = RuntimeError("modeled internal dispatcher failure")

    async def failed(owner):
        raise failure

    monkeypatch.setattr(client, "_run_handlers", failed)
    try:
        with pytest.raises(RuntimeError) as caught:
            await client.run_handlers()
        assert caught.value is failure and not client._event_consumer
        assert client._handler_task.done()
    finally:
        await client.close()
