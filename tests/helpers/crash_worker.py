"""Synthetic subprocess killed by crash QA; never reads a real session."""

import asyncio
import json
import os
from pathlib import Path
import sys
import time

from fncbale.storage import Store
from fncbale.events import journal_events
from fncbale.proto.struct_pb2 import WebUpdate


def ready(path, data):
    temporary = Path(path).with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(data, stream)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


async def main():
    database, stage, signal = sys.argv[1:]
    store = Store(database)
    media = stage in ("media", "media-transaction")
    context = (
        json.dumps({"media": [{"sha256": "first"}, {"sha256": "second"}], "rids": [11, 12], "grouped_id": 13})
        if media
        else "{}"
    )
    operation = await store.enqueue(
        "a",
        "p",
        "SendMultiMediaMessage" if media else "SendMessage",
        b"" if media else b"immutable",
        context,
        "fixed",
    )
    data = {"operation": operation}
    if stage.startswith("album-"):
        edit = WebUpdate()
        edit.messageContentChanged.peer.type, edit.messageContentChanged.peer.id = 2, 10
        edit.messageContentChanged.rid = 11
        edit.messageContentChanged.message.documentMessage.caption.text = "committed edit"
        delete = WebUpdate()
        delete.messageDelete.peer.CopyFrom(edit.messageContentChanged.peer)
        delete.messageDelete.rids.append(12)
        for update in (edit, delete):
            for event_id in await store.record("a", update.SerializeToString(), journal_events(update)):
                await store.ack("a", event_id)
        if stage == "album-materialize":

            def boundary():
                ready(signal, data)
                time.sleep(300)
                return 0

            await store.run(lambda db: db.create_function("qa_boundary", 0, boundary))
            await store.run(
                lambda db: db.execute(
                    "CREATE TRIGGER qa_materialize AFTER DELETE ON album_pending "
                    "BEGIN SELECT qa_boundary(); END"
                )
            )
            update = WebUpdate()
            update.messages.peer.type, update.messages.peer.id = 3, 10
            for rid in (12, 11):
                item = update.messages.messageContainers.add(rid=rid, date=100)
                item.groupedId.value = 13
                item.message.documentMessage.caption.text = "old base"
            await store.record(
                "a", update.SerializeToString(), journal_events(update), [("route", b"state", 10)]
            )
    if stage in ("claimed", "inflight", "waiting", "confirmed", "media", "media-transaction"):
        await store.claim("a")
    if media:
        await store.commit_media_upload("a", operation, 0, sha256="first", file_id=100, access_hash=200)
    if stage == "media-transaction":

        def interrupted_media(db):
            value = json.loads(
                db.execute("SELECT context FROM operations WHERE id=?", (operation,)).fetchone()[0]
            )
            value["media"][1].update(file_id=101, access_hash=200)
            db.execute("UPDATE operations SET context=? WHERE id=?", (json.dumps(value), operation))
            ready(signal, data)
            time.sleep(300)

        await store.run(interrupted_media)
    if stage in ("inflight", "waiting", "confirmed"):
        await store.attempted("a", operation)
    if stage == "waiting":
        await store.reschedule("a", operation, delay=60, account_wait=True, error="rate limited")
    if stage == "confirmed":
        await store.finish("a", operation, "confirmed", response=b"ack")
    if stage in ("inbox", "acked"):
        data["event"] = (
            await store.record(
                "a", b"frame", [("p", "unknown", b"event", "identity")], [("global", b"checkpoint", 42)]
            )
        )[0]
        if stage == "acked":
            await store.ack("a", data["event"])
    if stage == "transaction":

        def interrupted(db):
            db.execute("INSERT INTO journal(account,raw,created) VALUES('a',?,0)", (b"uncommitted",))
            db.execute("INSERT INTO routes VALUES('a','global',?,99)", (b"uncommitted",))
            db.execute(
                "INSERT INTO inbox(id,account,peer,kind,raw,created,updated) "
                "VALUES('partial','a','p','unknown',?,0,0)",
                (b"uncommitted",),
            )
            ready(signal, data)
            time.sleep(300)

        await store.run(interrupted)
    ready(signal, data)
    await asyncio.sleep(300)


asyncio.run(main())
