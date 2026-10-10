import sqlite3

import pytest

from fncbale import Client, Peer, PeerKind, Session
from fncbale.events import journal_events
from fncbale.proto import struct_pb2 as s
from fncbale.storage import Store


def mutation(kind, rid=1, peer_id=10):
    update = s.WebUpdate()
    value = update.messageContentChanged if kind == "edit" else update.messageDelete
    value.peer.type, value.peer.id = 2, peer_id
    if kind == "edit":
        value.rid = rid
        value.updatedContentTypeMessage.documentMessage.fileId = rid + 100
        value.updatedContentTypeMessage.documentMessage.caption.text = "edited before metadata"
    else:
        value.rids.append(rid)
    return update


def album():
    update = s.WebUpdate()
    update.messages.peer.type, update.messages.peer.id = 3, 10
    for rid in (2, 1):
        item = update.messages.messageContainers.add(rid=rid, date=100)
        item.groupedId.value, item.seq.value = 99, 2**55 + rid
        item.authorSign.value = "signature"
        item.message.documentMessage.fileId = rid + 100
        item.message.documentMessage.caption.text = "original"
        item.ParseFromString(item.SerializeToString() + b"\xfa\x3e\x02hi")
    return update


async def record(store, update, *, account="a", state=()):
    return await store.record(account, update.SerializeToString(), journal_events(update), state)


@pytest.mark.parametrize("restart", [False, True])
async def test_mutations_before_album_metadata_survive_ack_and_restart(tmp_path, restart):
    store = Store(tmp_path / "db")
    try:
        for value in (mutation("edit"), mutation("delete", rid=2)):
            for event_id in await record(store, value):
                await store.ack("a", event_id)
        if restart:
            await store.close()
            store = Store(tmp_path / "db")
        await record(store, album())
        client = Client(Session(1, "synthetic"), data_dir=tmp_path, _store=store)
        client.account = "a"
        try:
            snapshot = await client.get_album(Peer(PeerKind.CHANNEL, 10), 99)
            assert [item.rid for item in snapshot.messages] == [1]
            assert snapshot.messages[0].text == "edited before metadata"
            assert snapshot.messages[0].ref.seq == 2**55 + 1
            assert snapshot.messages[0].author_signature == "signature"
            from google.protobuf.unknown_fields import UnknownFieldSet

            assert list(UnknownFieldSet(s.WebHistory.FromString(snapshot.messages[0].raw)))
            all_items = await client.get_album(Peer(PeerKind.CHANNEL, 10), 99, include_deleted=True)
            assert [item.rid for item in all_items.messages] == [1, 2]
            pending = await store.pending_events("a")
            # Original raw new events are kept intact; snapshot repair must not rewrite history.
            assert len(pending) == 2
            assert all(
                s.WebUpdate.FromString(row["raw"])
                .messages.messageContainers[0]
                .message.documentMessage.caption.text
                == "original"
                for row in pending
            )
        finally:
            await client.close()
    finally:
        await store.close()


async def test_delete_then_edit_then_stale_bulk_never_resurrects_album_item(tmp_path):
    store = Store(tmp_path / "db")
    try:
        await record(store, mutation("delete"))
        await record(store, mutation("edit"))
        await record(store, album())
        rows = await store.run(
            lambda db: [dict(row) for row in db.execute("SELECT * FROM album_items ORDER BY rid")],
            write=False,
        )
        assert rows[0]["deleted"] == 1
        assert (
            s.WebUpdate.FromString(rows[0]["raw"])
            .messages.messageContainers[0]
            .message.documentMessage.caption.text
            == "edited before metadata"
        )
        await record(store, album())
        assert (
            await store.run(
                lambda db: db.execute("SELECT deleted FROM album_items WHERE rid=1").fetchone()[0],
                write=False,
            )
            == 1
        )
    finally:
        await store.close()


async def test_composed_bulk_and_mutations_keep_account_peer_and_raw_event_identity(tmp_path):
    store = Store(tmp_path / "db")
    try:
        composed = album()
        composed.messageContentChanged.CopyFrom(mutation("edit").messageContentChanged)
        composed.messageDelete.CopyFrom(mutation("delete", 2).messageDelete)
        ids = await record(store, composed)
        await record(store, album(), account="other")
        elsewhere = mutation("delete", 1, peer_id=20)
        await record(store, elsewhere)
        rows = await store.run(
            lambda db: [
                dict(row)
                for row in db.execute("SELECT account,rid,deleted,raw FROM album_items ORDER BY account,rid")
            ],
            write=False,
        )
        assert [row["deleted"] for row in rows] == [0, 1, 0, 0]
        assert (
            s.WebUpdate.FromString(rows[0]["raw"])
            .messages.messageContainers[0]
            .message.documentMessage.caption.text
            == "edited before metadata"
        )
        assert len(ids) == 4 and len(await store.pending_events("a")) == 5
        assert (
            await store.run(
                lambda db: db.execute("SELECT count(*) FROM album_pending").fetchone()[0], write=False
            )
            == 1
        )
    finally:
        await store.close()


async def test_pending_mutations_survive_retention_and_snapshot_checkpoint_rollback(tmp_path):
    store = Store(tmp_path / "db")
    try:
        ids = []
        for value in (mutation("edit"), mutation("delete", 2)):
            ids.extend(await record(store, value))
        for event_id in ids:
            await store.ack("a", event_id)
        await store.run(
            lambda db: (db.execute("UPDATE inbox SET updated=0"), db.execute("UPDATE journal SET created=0"))
        )
        await store.purge(7)
        assert not await store.pending_events("a")
        assert (
            await store.run(lambda db: db.execute("SELECT count(*) FROM journal").fetchone()[0], write=False)
            == 0
        )
        await store.run(
            lambda db: db.execute("""
            CREATE TRIGGER fail_checkpoint BEFORE INSERT ON routes
            BEGIN SELECT RAISE(ABORT, 'synthetic checkpoint failure'); END
        """)
        )
        with pytest.raises(sqlite3.Error):
            await record(store, album(), state=[("route", b"state", 10)])
        assert not await store.routes("a") and not await store.pending_events("a")
        assert (
            await store.run(
                lambda db: db.execute("SELECT count(*) FROM album_items").fetchone()[0], write=False
            )
            == 0
        )
        assert (
            await store.run(
                lambda db: db.execute("SELECT count(*) FROM album_pending").fetchone()[0], write=False
            )
            == 2
        )
        await store.run(lambda db: db.execute("DROP TRIGGER fail_checkpoint"))
        await record(store, album(), state=[("route", b"state", 10)])
        assert (await store.routes("a"))[0]["seq"] == 10
        assert (
            await store.run(
                lambda db: db.execute("SELECT count(*) FROM album_pending").fetchone()[0], write=False
            )
            == 0
        )
        assert (
            await store.run(
                lambda db: db.execute("SELECT deleted FROM album_items WHERE rid=2").fetchone()[0],
                write=False,
            )
            == 1
        )
    finally:
        await store.close()


async def test_schema_two_backfill_uses_retained_mutations_without_rewriting_known_snapshot(tmp_path):
    database = tmp_path / "db"
    store = Store(database)
    try:
        for value in (mutation("edit"), mutation("delete", 2)):
            for event_id in await record(store, value):
                await store.ack("a", event_id)
        known = album()
        known.messages.messageContainers[1].message.documentMessage.caption.text = "newer stored content"
        await record(store, known, account="known")
        old = mutation("edit")
        await store.run(
            lambda db: db.execute(
                "INSERT INTO inbox(id,account,peer,kind,raw,created,updated) VALUES('old','known','2:10','edit',?,0,0)",
                (old.SerializeToString(),),
            )
        )
        await store.close()
        # Make a genuine v2 shape: retained inbox/snapshot, no pending mutation table.
        with sqlite3.connect(database) as db:
            db.execute("DROP TABLE album_pending")
            db.execute("PRAGMA user_version=2")
        store = Store(database)
        await store.start()
        assert await store.run(lambda db: db.execute("PRAGMA user_version").fetchone()[0], write=False) == 3
        assert (
            await store.run(
                lambda db: db.execute("SELECT count(*) FROM album_pending").fetchone()[0], write=False
            )
            == 2
        )
        await record(store, album())
        rows = await store.run(
            lambda db: [
                dict(row)
                for row in db.execute("SELECT account,rid,raw,deleted FROM album_items ORDER BY account,rid")
            ],
            write=False,
        )
        first = s.WebUpdate.FromString(rows[0]["raw"]).messages.messageContainers[0]
        known_first = s.WebUpdate.FromString(rows[2]["raw"]).messages.messageContainers[0]
        assert (
            first.message.documentMessage.caption.text == "edited before metadata" and rows[1]["deleted"] == 1
        )
        assert known_first.message.documentMessage.caption.text == "newer stored content"
    finally:
        await store.close()
