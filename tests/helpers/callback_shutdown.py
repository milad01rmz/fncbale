"""Isolated shutdown-cycle probe; watchdog only terminates this synthetic child."""

import argparse
import asyncio
import json
import os
from pathlib import Path
import threading

from fncbale import AccountPool, Client, Config, Session
from fncbale.events import journal_events
from fncbale.proto.struct_pb2 import WebUpdate

errors = []


def finish(passed, **details):
    print(json.dumps({"pass": passed, "loop_errors": list(errors), **details}), flush=True)
    # A reproduced cyclic cancellation graph cannot be safely joined by loop
    # shutdown. This process owns only the supplied synthetic fixture directory.
    os._exit(0)


async def probe(directory, method):
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(lambda _, context: errors.append(type(context.get("exception")).__name__))
    pooled = method == "pool-close"
    pool = AccountPool(data_dir=directory, config=Config(queue_size=2)) if pooled else None
    client = (
        pool.add("one", Session(1, "synthetic"))
        if pool
        else Client(Session(1, "synthetic"), data_dir=directory, config=Config(queue_size=2))
    )
    target, close_method = (pool, "close") if pooled else (client, method)
    operation_id = None
    if pool:
        other = pool.add("two", Session(2, "synthetic"))
        other.account, other._active = "b", True
        operation_id = await pool.store.enqueue("b", "p", "SendMessage", b"frozen", "{}")
    client.account, client._active = "a", True
    cleaned = asyncio.Event()
    update = WebUpdate()
    update.message.peer.type, update.message.peer.id = 1, 10
    update.message.rid, update.message.date = 1, 1
    event_id = (await client.store.record("a", update.SerializeToString(), journal_events(update)))[0]

    @client.router.on("new")
    async def shutdown(event):
        try:
            await getattr(target, close_method)()
        finally:
            await asyncio.sleep(0.05)
            cleaned.set()

    dispatcher = client.start_handlers()
    try:
        async with asyncio.timeout(5):
            await cleaned.wait()
            await getattr(target, close_method)()
            await asyncio.gather(dispatcher, return_exceptions=True)
            assert not client._event_consumer and not client._active and not errors
            await client.close()
            restarted = (
                AccountPool(data_dir=directory)
                if pool
                else Client(Session(1, "synthetic"), data_dir=directory)
            )
            try:
                rows = await restarted.store.pending_events("a")
                assert len(rows) == 1 and rows[0]["id"] == event_id
                if operation_id is not None:
                    row = await restarted.store.operation("b", operation_id)
                    assert row["status"] == "queued" and bytes(row["payload"]) == b"frozen"
            finally:
                await restarted.close()
    except BaseException as exc:
        finish(False, error=type(exc).__name__, method=method)
    finish(True, method=method, cleanup_joined=True, pending_id_preserved=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("method", choices=("disconnect", "close", "pool-close"))
    args = parser.parse_args()
    watchdog = threading.Timer(8, lambda: finish(False, error="WatchdogTimeout", method=args.method))
    watchdog.daemon = True
    watchdog.start()
    asyncio.run(probe(args.directory, args.method))
