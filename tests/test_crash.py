import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from fncbale.storage import Store


@pytest.mark.parametrize(
    "stage,expected",
    [
        ("accepted", "queued"),
        ("claimed", "queued"),
        ("inflight", "uncertain"),
        ("waiting", "waiting"),
        ("confirmed", "confirmed"),
        ("inbox", "queued"),
        ("acked", "queued"),
        ("transaction", "queued"),
        ("media", "queued"),
        ("media-transaction", "queued"),
        ("album-pending", "queued"),
        ("album-materialize", "queued"),
    ],
)
async def test_real_process_kill_preserves_committed_state(tmp_path, stage, expected):
    root = Path(__file__).resolve().parents[1]
    signal, database = tmp_path / "ready.json", tmp_path / "db"
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(root / "src")
    process = subprocess.Popen(
        [sys.executable, str(root / "tests/helpers/crash_worker.py"), str(database), stage, str(signal)],
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    try:
        deadline = time.monotonic() + 15
        while not signal.exists():
            assert process.poll() is None, process.stderr.read().decode(errors="replace")
            assert time.monotonic() < deadline, "Synthetic crash child did not reach its commit boundary"
            await asyncio.sleep(0.02)
        data = json.loads(signal.read_text(encoding="utf-8"))
        process.kill()
        await asyncio.to_thread(process.wait, 10)
    finally:
        if process.poll() is None:
            process.kill()
            await asyncio.to_thread(process.wait, 10)
        process.stderr.close()
    store = Store(database)
    try:
        await store.recover_operations("a")
        row = await store.operation("a", data["operation"])
        assert row["status"] == expected and row["payload"] == (
            b"" if stage.startswith("media") else b"immutable"
        )
        assert (
            await store.enqueue("a", "p", row["method"], row["payload"], row["context"], "fixed") == row["id"]
        )
        if stage.startswith("media"):
            context = json.loads(row["context"])
            assert context["media"][0]["file_id"] == 100 and "file_id" not in context["media"][1]
            assert context["rids"] == [11, 12] and context["grouped_id"] == 13 and row["attempts"] == 0
        if stage == "waiting":
            assert row["cycle_attempts"] == 1 and row["not_before"] > time.time()
            assert await store.claim("a") is None
        if stage == "confirmed":
            assert row["response"] == b"ack"
        if stage in ("inbox", "acked"):
            pending = await store.pending_events("a")
            assert [event["id"] for event in pending] == ([data["event"]] if stage == "inbox" else [])
            assert (await store.routes("a"))[0]["seq"] == 42
        if stage == "transaction":
            assert not await store.routes("a") and not await store.pending_events("a")
            assert (
                await store.run(
                    lambda db: db.execute("SELECT count(*) FROM journal").fetchone()[0], write=False
                )
                == 0
            )
        if stage.startswith("album-"):
            from fncbale.events import journal_events
            from fncbale.proto.struct_pb2 import WebUpdate

            assert not await store.pending_events("a") and not await store.routes("a")
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
            if stage == "album-materialize":
                await store.run(lambda db: db.execute("DROP TRIGGER qa_materialize"))
            update = WebUpdate()
            update.messages.peer.type, update.messages.peer.id = 3, 10
            for rid in (12, 11):
                item = update.messages.messageContainers.add(rid=rid, date=100)
                item.groupedId.value = 13
                item.message.documentMessage.caption.text = "old base"
            await store.record(
                "a", update.SerializeToString(), journal_events(update), [("route", b"state", 10)]
            )
            rows = await store.run(
                lambda db: [dict(row) for row in db.execute("SELECT * FROM album_items ORDER BY rid")],
                write=False,
            )
            assert (
                WebUpdate.FromString(rows[0]["raw"])
                .messages.messageContainers[0]
                .message.documentMessage.caption.text
                == "committed edit"
            )
            assert rows[1]["deleted"] == 1 and (await store.routes("a"))[0]["seq"] == 10
            assert (
                await store.run(
                    lambda db: db.execute("SELECT count(*) FROM album_pending").fetchone()[0], write=False
                )
                == 0
            )
    finally:
        await store.close()
