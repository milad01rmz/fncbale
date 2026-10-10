"""One-way independent-send channel mirror with durable mappings and operation IDs."""

import argparse
import asyncio
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import time

from fncbale import Client, MessageRef, OperationHandle, contract, __version__
from fncbale.proto import struct_pb2 as s


class ChannelMirror:
    def __init__(self, client, source, target, *, name="channel-mirror", report=None):
        if source.key == target.key:
            raise ValueError("Source and target must differ")
        self.client, self.source, self.target = client, source, target
        self.account = client.account
        self.prefix = f"mirror:{name}:{source.key}:{target.key}:"
        self.report = report or (lambda **values: None)
        self.lock = asyncio.Lock()

    def check(self):
        self.client._ensure_operation_account(self.account)

    async def get(self, key):
        self.check()
        result = await self.client.fsm.get(self.prefix + key)
        self.check()
        return result

    async def put(self, key, value):
        self.check()
        await self.client.fsm.set(self.prefix + key, value)
        self.check()

    async def mapping(self, rid):
        return await self.get(f"rid:{rid}")

    @staticmethod
    def content(wire):
        content = s.WebMessage()
        content.CopyFrom(wire.message)
        if not content.HasField("textMessage") and not content.HasField("documentMessage"):
            if wire.HasField("quotedMessage"):
                content.CopyFrom(wire.quotedMessage.quotedMessageContent)
        if content.HasField("documentMessage"):
            content.documentMessage.ClearField("groupedId")
        return content

    @classmethod
    def content_hash(cls, wire):
        return hashlib.sha256(cls.content(wire).SerializeToString(deterministic=True)).hexdigest()

    async def history(self, *, limit=100, before=-1):
        return [
            s.WebHistory.FromString(m.raw)
            async for m in self.client.iter_history(self.source, limit=limit, before=before)
        ]

    async def reply(self, wire):
        if not wire.HasField("quotedMessage"):
            return None
        quote = wire.quotedMessage
        if quote.quotedPeer.id != self.source.id:
            self.report(kind="reply-unmapped", source_rid=wire.rid)
            return None
        mapping = await self.mapping(quote.messageId.value)
        if not mapping or mapping.get("deleted"):
            self.report(kind="reply-unmapped", source_rid=wire.rid)
            return None
        return MessageRef(self.target, **mapping["target"])

    async def deliver(self, snapshots):
        if not snapshots:
            return
        self.check()
        grouped = len(snapshots) > 1
        key = f"album:{snapshots[0].groupedId.value}" if grouped else f"message:{snapshots[0].rid}"
        state = await self.get(key)
        if state is None:
            reply = await self.reply(snapshots[0])
            state = {
                "snapshots": [wire.SerializeToString().hex() for wire in snapshots],
                "reply": {"rid": reply.rid, "date": reply.date, "seq": reply.seq} if reply else None,
            }
            await self.put(key, state)
        frozen = [s.WebHistory.FromString(bytes.fromhex(value)) for value in state["snapshots"]]
        if state.get("complete"):
            if {wire.rid for wire in snapshots} - {wire.rid for wire in frozen}:
                self.report(kind="album-gap", source_rids=[wire.rid for wire in snapshots])
                raise ValueError(
                    "Source album expanded beyond its committed mirror; explicit repair required"
                )
            return
        if state.get("operation_id"):
            handle = OperationHandle(self.client, state["operation_id"], account=self.account)
        else:
            reply = MessageRef(self.target, **state["reply"]) if state["reply"] else None
            handle = await self.client._enqueue_copy_snapshots(
                self.target,
                frozen,
                reply_to=reply,
                idempotency_key=self.prefix + key + state.get("repair_key", ""),
            )
            state["operation_id"] = handle.operation_id
            await self.put(key, state)
        try:
            result = await handle.wait()
        except Exception:
            # Reconcile the same durable operation; never produce new RIDs or switch to forward.
            operation = await handle.status()
            if operation.status == "uncertain":
                await self.client.reconcile_operation(handle.operation_id)
                result = await handle.wait()
            else:
                raise
        messages = list(result.messages) if grouped else [result]
        for wire, message in zip(frozen, messages, strict=True):
            await self.put(
                f"rid:{wire.rid}",
                {
                    "target": {"rid": message.rid, "date": message.ref.date, "seq": message.ref.seq},
                    "grouped_id": message.grouped_id,
                    "content_hash": self.content_hash(wire),
                    "deleted": False,
                },
            )
        state["complete"] = True
        await self.put(key, state)
        self.report(
            kind="copy",
            items=len(messages),
            operation_id=handle.operation_id,
            source_rids=[wire.rid for wire in frozen],
            target_rids=[m.rid for m in messages],
        )

    async def backfill(self):
        async with self.lock:
            history = sorted(await self.history(limit=None), key=lambda wire: (wire.date, wire.seq.value))
            groups = {}
            for wire in history:
                if wire.groupedId.value:
                    groups.setdefault(wire.groupedId.value, []).append(wire)
            processed = set()
            for wire in history:
                if wire.rid in processed:
                    continue
                items = groups.get(wire.groupedId.value, [wire])
                processed.update(item.rid for item in items)
                if not all(
                    self.content(item).HasField("textMessage")
                    or self.content(item).HasField("documentMessage")
                    for item in items
                ):
                    self.report(kind="unsupported-content", source_rids=[item.rid for item in items])
                    continue
                await self.deliver(items)
            self.report(kind="backfill-complete", history_items=len(history), processed=len(processed))

    async def edit(self, event, wire, mapping):
        digest = self.content_hash(wire)
        if digest == mapping["content_hash"] or mapping.get("deleted"):
            return
        key = "edit:" + event.event_id
        saved = await self.get(key)
        if saved is None:
            saved = {"content": self.content(wire).SerializeToString().hex(), "hash": digest}
            await self.put(key, saved)
        ref = MessageRef(self.target, **mapping["target"])
        if saved.get("operation_id"):
            handle = OperationHandle(self.client, saved["operation_id"], account=self.account)
        else:
            request = contract("UpdateMessage").request(rid=ref.rid)
            request.peer.type, request.peer.id, request.peer.accessHash = (
                self.target.wire_type,
                self.target.id,
                self.target.access_hash,
            )
            request.updatedMessage.ParseFromString(bytes.fromhex(saved["content"]))
            handle = await self.client._enqueue(
                self.target,
                "UpdateMessage",
                request,
                {
                    "kind": "edit",
                    "peer": asdict(self.target),
                    "rids": [ref.rid],
                    "date": ref.date,
                    "seq": ref.seq,
                    "grouped_id": mapping.get("grouped_id"),
                },
                idempotency_key=self.prefix + key,
                intent={"ref": asdict(ref), "content": saved["content"]},
            )
            saved["operation_id"] = handle.operation_id
            await self.put(key, saved)
        try:
            await handle.wait()
        except Exception:
            if (await handle.status()).status != "uncertain":
                raise
            await self.client.reconcile_operation(handle.operation_id)
            await handle.wait()
        mapping["content_hash"] = saved["hash"]
        await self.put(f"rid:{wire.rid}", mapping)
        self.report(kind="edit", source_rid=wire.rid, target_rid=ref.rid)

    async def on_event(self, event):
        if event.peer is None or event.peer.key != self.source.key:
            return
        if event.kind not in ("new", "sent", "edit", "delete"):
            return
        async with self.lock:
            if event.kind == "sent" and await self.mapping(event.message.rid):
                # ACKs carry identity only; later content changes have their own edit events.
                return
            if event.kind == "delete":
                mappings = [(rid, await self.mapping(rid)) for rid in event.rids]
                active = [(rid, value) for rid, value in mappings if value and not value.get("deleted")]
                if active:
                    await self.client.delete_messages(
                        [MessageRef(self.target, **value["target"]) for _, value in active],
                        idempotency_key=self.prefix + "delete:" + event.event_id,
                    )
                    for rid, value in active:
                        value["deleted"] = True
                        await self.put(f"rid:{rid}", value)
                    self.report(kind="delete", source_rids=[rid for rid, _ in active])
                return
            date = event.message.ref.date
            # An ACK/update date can identify one album item or the batch boundary.
            # Read the current window first so later siblings are not clipped off.
            history = await self.history()
            wire = next((item for item in history if item.rid == event.message.rid), None)
            if wire is None and event.kind == "sent":
                # Bale can report an album ACK using groupedId in the RID slot.
                album = sorted(
                    (item for item in history if item.groupedId.value == event.message.rid),
                    key=lambda item: (item.date, item.seq.value),
                )
                if album:
                    await self.deliver(album)
                    return
            if wire is None and date:
                history = await self.history(before=date + 1)
                wire = next((item for item in history if item.rid == event.message.rid), None)
            if wire is None:
                mapping = await self.mapping(event.message.rid)
                if mapping and mapping.get("deleted"):
                    return
                # An unresolved gap remains in quarantine rather than being silently ACKed.
                self.report(kind="source-unavailable", source_rid=event.message.rid)
                raise ValueError("Source snapshot unavailable; retained event requires replay")
            mapping = await self.mapping(wire.rid)
            if mapping:
                await self.edit(event, wire, mapping)
                return
            items = [wire]
            if wire.groupedId.value:
                items = sorted(
                    (item for item in history if item.groupedId.value == wire.groupedId.value),
                    key=lambda item: (item.date, item.seq.value),
                )
            await self.deliver(items)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("session", type=Path)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--source", default="@codextest1")
    parser.add_argument("--target", default="@codextest2")
    parser.add_argument("--stop-file", type=Path)
    parser.add_argument("--replay-failed", action="store_true")
    args = parser.parse_args()
    args.data_dir.mkdir(parents=True, exist_ok=True)
    log = args.data_dir / "activity.jsonl"

    def report(**values):
        values["time"] = time.time()
        with log.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(values) + "\n")

    client = Client(args.session, data_dir=args.data_dir / "client")
    original_call = client._call_bytes

    async def trace(method, payload, route):
        started = time.perf_counter()
        try:
            return await original_call(method, payload, route)
        finally:
            report(
                kind="rpc",
                method=method,
                route=route,
                elapsed_ms=round((time.perf_counter() - started) * 1000, 2),
            )

    client._call_bytes = trace
    try:
        await client.connect()
        source, target = await client.resolve_peer(args.source), await client.resolve_peer(args.target)
        mirror = ChannelMirror(client, source, target, report=report)
        client.router.on()(mirror.on_event)
        await mirror.backfill()
        client.start_handlers()
        if args.replay_failed:
            failures = [event async for event in client.iter_failed_events(limit=100)]
            for event in failures:
                if event.peer and event.peer.key == source.key:
                    await client.replay_event(event.event_id)
        (args.data_dir / "ready.json").write_text(
            json.dumps(
                {
                    "pid": os.getpid(),
                    "source": source.id,
                    "target": target.id,
                    "ready": True,
                    "version": __version__,
                }
            )
        )
        while args.stop_file is None or not args.stop_file.exists():
            await asyncio.sleep(1)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
