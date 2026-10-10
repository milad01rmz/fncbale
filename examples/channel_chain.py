"""Read-only upstream channel feeding two independently sent test-channel mirrors."""

import argparse
import asyncio
import json
import os
from pathlib import Path
import time

from fncbale import Client, contract, __version__
from fncbale.errors import RpcError
from fncbale.events import Event

if __package__:
    from .channel_mirror import ChannelMirror
else:
    from channel_mirror import ChannelMirror


class DestinationFence:
    """Reject every mutation except message writes to explicitly allowed destinations."""

    def __init__(self, destination_ids):
        self.destinations = frozenset(destination_ids)

    def check(self, method, payload):
        definition = contract(method)
        if definition.readonly:
            return None
        if method not in {"SendMessage", "SendMultiMediaMessage", "UpdateMessage", "DeleteMessage"}:
            raise RpcError(7, method, reason="Chain permits only read RPCs and destination message mutations")
        request = definition.request.FromString(payload)
        expected_type = 3 if method == "SendMultiMediaMessage" else 2
        if request.peer.type != expected_type or request.peer.id not in self.destinations:
            raise RpcError(7, method, reason="Chain mutation destination is outside the test channels")
        return request.peer.id


async def seed_recent(mirror, posts):
    """Seed only recent logical posts, retaining complete album siblings in the window."""
    async with mirror.lock:
        await _seed_recent(mirror, posts)


async def _seed_recent(mirror, posts):
    if await mirror.get("chain-seeded"):
        return
    history = sorted(await mirror.history(), key=lambda item: (item.date, item.seq.value))
    groups = {}
    for wire in history:
        key = ("album", wire.groupedId.value) if wire.groupedId.value else ("message", wire.rid)
        groups.setdefault(key, []).append(wire)
    selected = list(groups.values())[-posts:] if posts else []
    for items in selected:
        await mirror.deliver(items)
    await mirror.put(
        "chain-seeded",
        {
            "posts": len(selected),
            "items": sum(map(len, selected)),
            "since": min(
                (item.date for group in selected for item in group),
                default=max((item.date for item in history), default=0),
            ),
        },
    )
    mirror.report(kind="seed-complete", posts=len(selected), items=sum(map(len, selected)))


async def poll_recent(mirror):
    """Read-only recovery probe for visible new/edited posts; never infer deletes from absence."""
    async with mirror.lock:
        state = await mirror.get("chain-seeded")
        if not state:
            return
        history = sorted(await mirror.history(), key=lambda item: (item.date, item.seq.value))
        groups = {}
        for wire in history:
            if wire.date < state["since"]:
                continue
            key = ("album", wire.groupedId.value) if wire.groupedId.value else ("message", wire.rid)
            groups.setdefault(key, []).append(wire)
        for items in groups.values():
            if not await mirror.mapping(items[0].rid):
                await mirror.deliver(items)
            else:
                for wire in items:
                    mapping = await mirror.mapping(wire.rid)
                    if mapping is None:
                        # A late sibling cannot disappear just because the first
                        # album item is already mapped. Deliver reports a durable
                        # explicit album-gap instead of silently ignoring it.
                        await mirror.deliver(items)
                        break
                    if mapping and mirror.content_hash(wire) != mapping["content_hash"]:
                        event = Event(
                            "poll:" + str(wire.rid) + ":" + mirror.content_hash(wire),
                            "edit",
                            mirror.source,
                            b"",
                        )
                        await mirror.edit(event, wire, mapping)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("session", type=Path)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--stop-file", type=Path, required=True)
    parser.add_argument("--upstream", default="@akhbarefori")
    parser.add_argument("--first", default="@codextest1")
    parser.add_argument("--second", default="@codextest2")
    parser.add_argument("--seed-posts", type=int, default=5)
    args = parser.parse_args()
    if not 0 <= args.seed_posts <= 10:
        parser.error("seed-posts must be between0 and10")
    args.data_dir.mkdir(parents=True, exist_ok=True)

    def report(**values):
        values["time"] = time.time()
        with (args.data_dir / "activity.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(values) + "\n")

    client = Client(args.session, data_dir=args.data_dir / "client")
    call = client._call_bytes
    # Resolve by exact username over read RPCs before permitting any writes.
    fence = DestinationFence(())

    async def guarded_call(method, payload, route):
        destination = fence.check(method, payload)
        if destination is not None:
            report(kind="chain-write", method=method, destination=destination)
        return await call(method, payload, route)

    client._call_bytes = guarded_call
    try:
        # Resolve destinations before starting outbox workers that can resume queued writes.
        client.session = await client.session_file.load()
        if client.session is None:
            raise ValueError("A native session is required")
        client._grpc._token = client.session.token
        news = await client.resolve_peer(args.upstream)
        first = await client.resolve_peer(args.first)
        second = await client.resolve_peer(args.second)
        if len({news.key, first.key, second.key}) != 3:
            raise ValueError("Chain requires three distinct channels")
        fence = DestinationFence((first.id, second.id))
        source_group = await client.get_full_group(news)
        source_member = source_group.isMember.value
        await client.connect()
        downstream = ChannelMirror(client, first, second, report=report)
        upstream = ChannelMirror(client, news, first, report=report)

        # Keep the previous first→second namespace and ledger: never duplicate its history.
        async def on_event(event):
            await downstream.on_event(event)
            await upstream.on_event(event)

        client.router.on()(on_event)
        await downstream.backfill()
        client.start_handlers()
        await seed_recent(upstream, args.seed_posts)
        ready = {
            "pid": os.getpid(),
            "version": __version__,
            "ready": True,
            "chain": [news.id, first.id, second.id],
            "readonly_source": news.id,
            "allowed_write_destinations": sorted(fence.destinations),
            "source_is_member": source_member,
            "history_poll_seconds": 10,
        }
        (args.data_dir / "ready.json").write_text(json.dumps(ready), encoding="utf-8")
        report(kind="chain-ready", **ready)
        next_poll = time.monotonic() + 10
        while not args.stop_file.exists():
            await asyncio.sleep(1)
            if time.monotonic() >= next_poll:
                try:
                    await poll_recent(upstream)
                except Exception as exc:
                    report(kind="upstream-poll-error", error=type(exc).__name__)
                next_poll = time.monotonic() + 10
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
