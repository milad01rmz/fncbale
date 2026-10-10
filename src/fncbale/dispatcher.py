from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import inspect
import json
from typing import TYPE_CHECKING

from .errors import BaleError, ConversationClosed
from .events import Event
from .models import Message, Peer

if TYPE_CHECKING:
    from .client import Client


class Router:
    def __init__(self):
        self.handlers = []
        self.middlewares = []

    def on(self, kind=None, *, predicate=None):
        def register(callback):
            self.handlers.append((kind, predicate, callback))
            return callback

        return register

    def middleware(self, callback):
        self.middlewares.append(callback)
        return callback

    async def dispatch(self, event):
        for kind, predicate, callback in self.handlers:
            if kind and kind != event.kind:
                continue
            if predicate:
                accepted = predicate(event)
                if inspect.isawaitable(accepted):
                    accepted = await accepted
                if not accepted:
                    continue

            async def endpoint(item, cb=callback):
                await cb(item)

            next_handler = endpoint
            for middleware in reversed(self.middlewares):
                previous = next_handler

                async def layer(item, mw=middleware, nxt=previous):
                    await mw(item, nxt)

                next_handler = layer
            await next_handler(event)


class FSM:
    def __init__(self, store, account):
        self.store, self.account = store, account

    async def get(self, key):
        def get(db):
            row = db.execute(
                "SELECT data FROM fsm WHERE account=? AND key=?", (self.account, str(key))
            ).fetchone()
            return json.loads(row[0]) if row else None

        return await self.store.run(get, write=False)

    async def set(self, key, value):
        data = json.dumps(value, ensure_ascii=False)
        await self.store.run(
            lambda db: (
                db.execute(
                    "INSERT INTO fsm(account,key,data) VALUES(?,?,?) "
                    "ON CONFLICT(account,key) DO UPDATE SET data=excluded.data",
                    (self.account, str(key), data),
                ).rowcount
            )
        )

    async def update(self, key, transform):
        """Atomic read-modify-write; transform must be synchronous."""

        def update(db):
            row = db.execute(
                "SELECT data FROM fsm WHERE account=? AND key=?", (self.account, str(key))
            ).fetchone()
            value = transform(json.loads(row[0]) if row else None)
            db.execute(
                "INSERT INTO fsm(account,key,data) VALUES(?,?,?) "
                "ON CONFLICT(account,key) DO UPDATE SET data=excluded.data",
                (self.account, str(key), json.dumps(value)),
            )
            return value

        return await self.store.run(update)


class Conversation:
    """A scoped queue; closure releases both blocked producers and receivers."""

    def __init__(self, client: Client, peer: Peer, timeout: float | None):
        self.client, self.peer, self.timeout = client, peer, timeout
        self._queue = asyncio.Queue(client.config.queue_size)
        self._closed = asyncio.Event()

    def close(self) -> None:
        self._closed.set()

    async def _wait(self, operation):
        # Construct queue operations only after checking closure, avoiding orphan coroutines.
        if self._closed.is_set():
            raise ConversationClosed("Conversation scope has ended")
        pending = asyncio.create_task(operation())
        closed = asyncio.create_task(self._closed.wait())
        try:
            await asyncio.wait((pending, closed), return_when=asyncio.FIRST_COMPLETED)
            if self._closed.is_set():
                raise ConversationClosed("Conversation scope has ended")
            return pending.result()
        finally:
            pending.cancel()
            closed.cancel()
            await asyncio.gather(pending, closed, return_exceptions=True)

    async def _deliver(self, event: Event) -> None:
        try:
            await self._wait(lambda: self._queue.put(event))
        except ConversationClosed:
            return

    async def send(self, text: str, **kwargs) -> Message:
        if self._closed.is_set():
            raise ConversationClosed("Conversation scope has ended")
        return await self.client.send_message(self.peer, text, **kwargs)

    async def receive(self) -> Event:
        return await asyncio.wait_for(self._wait(self._queue.get), self.timeout)


@asynccontextmanager
async def conversation(client, peer, *, timeout=30):
    client._ensure_open()
    if not client._active:
        raise BaleError("Connect before opening a conversation")
    peer = await client.resolve_peer(peer)
    scope = Conversation(client, peer, timeout)
    client._conversations.add(scope)
    try:
        client.start_handlers()
        yield scope
    finally:
        scope.close()
        client._conversations.discard(scope)
