from __future__ import annotations

import asyncio
from pathlib import Path

from .client import Client
from .config import Config
from .dispatcher import Router
from .errors import ClientClosed
from .resources import Resources
from .storage import Store
from .session import Session


class AccountPool:
    def __init__(self, *, data_dir: str | Path = ".fncbale", config: Config | None = None):
        self.config = config or Config()
        self.root = Path(data_dir).resolve()
        self.resources = Resources(self.config)
        self.store = Store(
            self.root / "pool.sqlite3",
            queue_size=self.config.queue_size,
            commit_window=self.config.commit_window,
        )
        self.clients: dict[str, Client] = {}
        self._names: set[str] = set()
        self._closing = False
        self._close_task: asyncio.Task | None = None

    def _ensure_open(self):
        if self._closing:
            raise ClientClosed("AccountPool.close() is permanent; create another pool")

    def add(self, name: str, session: Session | str | Path | None, *, router: Router | None = None) -> Client:
        self._ensure_open()
        reserved = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            *(f"COM{i}" for i in range(1, 10)),
            *(f"LPT{i}" for i in range(1, 10)),
        }
        if (
            not isinstance(name, str)
            or not name
            or name in (".", "..")
            or name.rstrip(" .") != name
            or name.casefold() in self._names
            or any(ch in '<>:"/\\|?*' or ord(ch) < 32 for ch in name)
            or name.split(".", 1)[0].upper() in reserved
            or Path(name).name != name
        ):
            raise ValueError("Account name must be a unique portable directory component")
        destination = (self.root / name).resolve()
        if destination.parent != self.root or destination != self.root / name:
            raise ValueError("Account directory resolves outside this pool")
        client = Client(
            session,
            data_dir=destination,
            config=self.config,
            router=router,
            _resources=self.resources,
            _store=self.store,
        )
        self.clients[name] = client
        self._names.add(name.casefold())
        return client

    async def __aenter__(self) -> AccountPool:
        self._ensure_open()
        await self.store.start()
        self._ensure_open()
        return self

    async def __aexit__(self, *_):
        await self.close()

    async def close(self) -> None:
        if self._close_task is None:
            self._closing = True
            self._close_task = asyncio.create_task(self._close_once(), name="fncbale-pool-close")
            self._close_task.add_done_callback(
                lambda task: task.exception() if not task.cancelled() else None
            )
        await asyncio.shield(self._close_task)

    async def _close_once(self):
        results = await asyncio.gather(
            *(client.close() for client in self.clients.values()), return_exceptions=True
        )
        results.extend(
            await asyncio.gather(self.store.close(), self.resources.close(), return_exceptions=True)
        )
        errors = [result for result in results if isinstance(result, BaseException)]
        if errors:
            raise BaseExceptionGroup("AccountPool cleanup failed", errors)
