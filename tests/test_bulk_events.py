from fncbale.events import normalize, journal_events
from fncbale.proto import struct_pb2 as s
from fncbale.storage import Store


async def test_bulk_album_receive_edit_delete_and_snapshot(tmp_path):
    update = s.WebUpdate()
    update.messages.peer.type, update.messages.peer.id = 3, 10
    for rid in [2, 1]:
        item = update.messages.messageContainers.add(rid=rid, date=4, senderUid=8)
        item.groupedId.value = 99
        item.seq.value = 2**55 + rid
        item.authorSign.value = "" if rid == 1 else "model author"
        item.message.documentMessage.fileId = rid + 100
        item.message.documentMessage.caption.text = f"photo-{rid}"
        item.message.documentMessage.ext.documentExPhoto.w = 640
        item.message.documentMessage.ext.documentExPhoto.h = 480
        item.ParseFromString(item.SerializeToString() + b"\xfa\x3e\x02hi")
    events = normalize(update)
    assert [e.kind for e in events] == ["new", "new"]
    assert [e.message.rid for e in events] == [1, 2]
    assert all(e.message.grouped_id == 99 for e in events)
    assert [e.message.ref.seq for e in events] == [2**55 + 1, 2**55 + 2]
    assert [e.message.author_signature for e in events] == ["", "model author"]
    store = Store(tmp_path / "db")
    try:
        await store.record("a", update.SerializeToString(), journal_events(update))
        edit = s.WebUpdate()
        edit.messageContentChanged.peer.type, edit.messageContentChanged.peer.id = 2, 10
        edit.messageContentChanged.rid = 1
        edit.messageContentChanged.message.documentMessage.caption.text = "changed"
        await store.record("a", edit.SerializeToString(), journal_events(edit))
        delete = s.WebUpdate()
        delete.messageDelete.peer.type, delete.messageDelete.peer.id = 2, 10
        delete.messageDelete.rids.append(2)
        await store.record("a", delete.SerializeToString(), journal_events(delete))
        rows = await store.run(
            lambda db: [dict(row) for row in db.execute("SELECT * FROM album_items ORDER BY rid")],
            write=False,
        )
        assert len(rows) == 2 and rows[1]["deleted"] == 1
        assert normalize(s.WebUpdate.FromString(rows[0]["raw"]))[0].message.text == "changed"
        from google.protobuf.unknown_fields import UnknownFieldSet
        from fncbale import Client, Peer, PeerKind, Session

        retained = s.WebUpdate.FromString(rows[0]["raw"]).messages.messageContainers[0]
        assert retained.HasField("authorSign") and list(UnknownFieldSet(retained))
        client = Client(Session(1, "synthetic"), data_dir=tmp_path, _store=store)
        client.account = "a"
        try:
            album = await client.get_album(Peer(PeerKind.CHANNEL, 10), 99, include_deleted=True)
            assert [m.ref.seq for m in album.messages] == [2**55 + 1, 2**55 + 2]
            assert album.messages[0].text == "changed" and album.messages[0].author_signature == ""
        finally:
            await client.close()
    finally:
        await store.close()


async def test_full_duplicate_enriches_legacy_album_without_undoing_edits_or_delete(tmp_path):
    store = Store(tmp_path / "db")
    legacy = s.WebUpdate()
    legacy.message.peer.type, legacy.message.peer.id = 2, 10
    legacy.message.rid, legacy.message.date = 1, 4
    legacy.message.groupedId.value = 99
    legacy.message.message.documentMessage.caption.text = "original"
    try:
        await store.record("a", legacy.SerializeToString(), journal_events(legacy))
        edit = s.WebUpdate()
        edit.messageContentChanged.peer.CopyFrom(legacy.message.peer)
        edit.messageContentChanged.rid = 1
        edit.messageContentChanged.message.documentMessage.caption.text = "later edit"
        await store.record("a", edit.SerializeToString(), journal_events(edit))
        delete = s.WebUpdate()
        delete.messageDelete.peer.CopyFrom(legacy.message.peer)
        delete.messageDelete.rids.append(1)
        await store.record("a", delete.SerializeToString(), journal_events(delete))
        full = s.WebUpdate()
        full.messages.peer.type, full.messages.peer.id = 3, 10
        item = full.messages.messageContainers.add(rid=1, date=4)
        item.groupedId.value, item.seq.value = 99, 2**55
        item.authorSign.value = "signature"
        item.message.CopyFrom(legacy.message.message)
        await store.record("a", full.SerializeToString(), journal_events(full))
        row = await store.run(
            lambda db: dict(db.execute("SELECT * FROM album_items").fetchone()), write=False
        )
        assert row["deleted"] == 1
        message = normalize(s.WebUpdate.FromString(row["raw"]))[0].message
        assert (
            message.text == "later edit"
            and message.ref.seq == 2**55
            and message.author_signature == "signature"
        )
        assert (
            len(await store.pending_events("a")) == 3
        )  # The full duplicate adds metadata, no extra new event.
    finally:
        await store.close()
