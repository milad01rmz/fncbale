"""Single-threaded SQLite writer with bounded group commit and durable journals."""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
import contextlib
import hashlib
import json
import re
import sqlite3
import time
import uuid
from pathlib import Path

from .errors import IdempotencyConflict, StorageError

SCHEMA = """
CREATE TABLE IF NOT EXISTS operations (
 id TEXT PRIMARY KEY, account TEXT NOT NULL, peer TEXT NOT NULL, method TEXT NOT NULL,
 payload BLOB NOT NULL, digest TEXT NOT NULL, idem TEXT, context TEXT NOT NULL DEFAULT '{}',
 status TEXT NOT NULL DEFAULT 'queued', attempts INTEGER NOT NULL DEFAULT 0,
 cycle_attempts INTEGER NOT NULL DEFAULT 0, not_before REAL NOT NULL DEFAULT 0,
 in_flight INTEGER NOT NULL DEFAULT 0, ambiguous INTEGER NOT NULL DEFAULT 0,
 response BLOB, error TEXT, created REAL NOT NULL, updated REAL NOT NULL,
 UNIQUE(account,idem));
CREATE INDEX IF NOT EXISTS op_dispatch ON operations(account,status,created);
CREATE INDEX IF NOT EXISTS op_inspect ON operations(account,created,id);
DROP INDEX IF EXISTS op_peer_order;
CREATE INDEX IF NOT EXISTS op_peer_pending ON operations(account,peer,created)
 WHERE status IN ('queued','waiting','running','uncertain');
CREATE TABLE IF NOT EXISTS journal (
 id INTEGER PRIMARY KEY, account TEXT NOT NULL, raw BLOB NOT NULL, created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS inbox (
 id TEXT PRIMARY KEY, account TEXT NOT NULL, peer TEXT NOT NULL, kind TEXT NOT NULL,
 raw BLOB NOT NULL, dedupe TEXT, journal_id INTEGER, status TEXT NOT NULL DEFAULT 'pending',
 attempts INTEGER NOT NULL DEFAULT 0, created REAL NOT NULL, updated REAL NOT NULL,
 UNIQUE(account,dedupe));
DROP INDEX IF EXISTS inbox_pending;
CREATE INDEX IF NOT EXISTS inbox_delivery ON inbox(account,status);
CREATE TABLE IF NOT EXISTS routes (
 account TEXT NOT NULL, route TEXT NOT NULL, state BLOB NOT NULL, seq INTEGER NOT NULL,
 PRIMARY KEY(account,route));
CREATE TABLE IF NOT EXISTS fsm (
 account TEXT NOT NULL, key TEXT NOT NULL, data TEXT NOT NULL, PRIMARY KEY(account,key));
CREATE TABLE IF NOT EXISTS album_items (
 account TEXT NOT NULL, peer TEXT NOT NULL, grouped INTEGER NOT NULL, rid INTEGER NOT NULL,
 date INTEGER NOT NULL, raw BLOB NOT NULL, deleted INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY(account,peer,rid));
CREATE TABLE IF NOT EXISTS album_pending (
 account TEXT NOT NULL, peer TEXT NOT NULL, rid INTEGER NOT NULL,
 edit BLOB, deleted INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(account,peer,rid));
CREATE TABLE IF NOT EXISTS account_limits (
 account TEXT PRIMARY KEY, not_before REAL NOT NULL);
"""


def _remember_album_mutation(db, account, peer, rid, *, edit=None, deleted=0):
    db.execute(
        "INSERT INTO album_pending(account,peer,rid,edit,deleted) VALUES(?,?,?,?,?) "
        "ON CONFLICT(account,peer,rid) DO UPDATE SET "
        "edit=CASE WHEN excluded.edit IS NULL THEN album_pending.edit ELSE excluded.edit END, "
        "deleted=max(album_pending.deleted,excluded.deleted)",
        (account, peer, rid, edit, deleted),
    )


def _migrate_album_mutations(db):
    from .proto.struct_pb2 import WebUpdate

    # Recover only missing snapshots from the retained journal/inbox order. Do not
    # replay old retained edits over existing snapshots whose newer edits may have expired.
    for row in db.execute(
        "SELECT account,peer,kind,raw FROM inbox WHERE kind IN ('edit','delete') ORDER BY rowid"
    ):
        value = WebUpdate.FromString(row["raw"])
        rids = (value.messageContentChanged.rid,) if row["kind"] == "edit" else value.messageDelete.rids
        for rid in rids:
            if db.execute(
                "SELECT 1 FROM album_items WHERE account=? AND peer=? AND rid=?",
                (row["account"], row["peer"], rid),
            ).fetchone():
                continue
            _remember_album_mutation(
                db,
                row["account"],
                row["peer"],
                rid,
                edit=row["raw"] if row["kind"] == "edit" else None,
                deleted=int(row["kind"] == "delete"),
            )


def _apply_album_edit(snapshot, edit_raw):
    from .proto.struct_pb2 import WebUpdate

    edited = WebUpdate.FromString(edit_raw).messageContentChanged
    content = (
        snapshot.messages.messageContainers[0].message
        if snapshot.HasField("messages")
        else snapshot.message.message
    )
    content.CopyFrom(
        edited.updatedContentTypeMessage if edited.HasField("updatedContentTypeMessage") else edited.message
    )


class _ClaimProbe:
    """Internal marker for a dispatch selection inside the writer transaction."""

    def __init__(self, account, callback):
        self.account, self.callback = account, callback
        self.empty_cacheable = False

    def __call__(self, db):
        return self.callback(db)


class Store:
    def __init__(self, path: str | Path, *, queue_size=256, commit_window=0.003):
        self.path = Path(path)
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="fncbale-db")
        self._queue = asyncio.Queue(queue_size)
        self._window = commit_window
        self._task = None
        self._start_task = None
        self._db = None
        self._closed = False
        self._closing = False
        self._last_purge = 0.0
        self._maintenance_lock = asyncio.Lock()
        self._admission_lock = asyncio.Lock()
        self._close_task = None
        self._spool_roots = {}
        self._rates = {}
        self._inbox_watchers = {}

    def _watch_inbox(self, account, wake):
        self._inbox_watchers.setdefault(account, set()).add(wake)

    def _unwatch_inbox(self, account, wake):
        watchers = self._inbox_watchers.get(account)
        if watchers is not None:
            watchers.discard(wake)
            if not watchers:
                self._inbox_watchers.pop(account, None)

    def _notify_inbox(self, account):
        for wake in self._inbox_watchers.get(account, ()):
            wake.set()

    def register_spool(self, path, in_use):
        self._spool_roots.setdefault(Path(path).resolve(), []).append(in_use)

    async def start(self):
        if self._closed or self._closing:
            raise StorageError("Store is closing or closed")
        if self._start_task is None:
            self._start_task = asyncio.create_task(self._initialize())
        await asyncio.shield(self._start_task)

    async def _initialize(self):
        if self._task:
            return

        def open_db():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._db = sqlite3.connect(self.path, isolation_level=None, timeout=30)
            self._db.row_factory = sqlite3.Row
            self._db.execute("PRAGMA journal_mode=WAL")
            self._db.execute("PRAGMA synchronous=FULL")
            self._db.execute("PRAGMA busy_timeout=30000")
            version = self._db.execute("PRAGMA user_version").fetchone()[0]
            if version > 3:
                self._db.close()
                self._db = None
                raise StorageError("Database schema is newer than this client")
            try:
                self._db.executescript("BEGIN IMMEDIATE;\n" + SCHEMA)
                columns = {row[1] for row in self._db.execute("PRAGMA table_info(operations)")}
                for name, definition in (
                    ("cycle_attempts", "INTEGER NOT NULL DEFAULT 0"),
                    ("not_before", "REAL NOT NULL DEFAULT 0"),
                    ("in_flight", "INTEGER NOT NULL DEFAULT 0"),
                    ("ambiguous", "INTEGER NOT NULL DEFAULT 0"),
                ):
                    if name not in columns:
                        self._db.execute(f"ALTER TABLE operations ADD COLUMN {name} {definition}")
                if version == 1:
                    self._db.execute(
                        "UPDATE operations SET cycle_attempts=min(attempts,3), "
                        "in_flight=CASE WHEN status='running' AND attempts>0 THEN 1 ELSE 0 END, "
                        "ambiguous=CASE WHEN status='uncertain' THEN 1 ELSE 0 END"
                    )
                if 0 < version < 3:
                    _migrate_album_mutations(self._db)
                self._db.execute("PRAGMA user_version=3")
                self._db.execute("COMMIT")
                self._rates = dict(self._db.execute("SELECT account,not_before FROM account_limits"))
            except BaseException:
                with contextlib.suppress(Exception):
                    self._db.execute("ROLLBACK")
                self._db.close()
                self._db = None
                raise

        await asyncio.get_running_loop().run_in_executor(self._executor, open_db)
        self._task = asyncio.create_task(self._writer(), name="fncbale-store")

    async def run(self, callback, *, write=True, _committed=None):
        if self._closed or self._closing:
            raise StorageError("Store is closed")
        await self.start()
        future = asyncio.get_running_loop().create_future()
        async with self._admission_lock:
            if self._closing:
                raise StorageError("Store is closing")
            await self._queue.put((callback, write, future, _committed))
        # Retrieve abandoned exceptions without changing results for active waiters.
        future.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
        # Cancellation of a waiter cannot retract an accepted transaction.
        return await asyncio.shield(future)

    async def _writer(self):
        while True:
            first = await self._queue.get()
            if first is None:
                break
            batch = [first]
            if self._window:
                await asyncio.sleep(self._window)
            while len(batch) < 128:
                try:
                    item = self._queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
                if item is None:
                    await self._queue.put(None)
                    break
                batch.append(item)

            def execute(batch=tuple(batch)):
                results = []
                empty_claims = set()
                self._db.execute("BEGIN IMMEDIATE" if any(x[1] for x in batch) else "BEGIN")
                try:
                    for index, (callback, write, _, _) in enumerate(batch):
                        probe = isinstance(callback, _ClaimProbe)
                        if probe and callback.account in empty_claims:
                            results.append((True, None))
                            continue
                        if write and not probe:
                            # Any mutation can change readiness/FIFO/rate gates.
                            # Hints never survive writes or this transaction.
                            empty_claims.clear()
                        self._db.execute(f"SAVEPOINT item_{index}")
                        try:
                            result = callback(self._db)
                            results.append((True, result))
                            if probe and result is None and callback.empty_cacheable:
                                empty_claims.add(callback.account)
                        except Exception as error:
                            self._db.execute(f"ROLLBACK TO item_{index}")
                            results.append((False, error))
                        finally:
                            self._db.execute(f"RELEASE item_{index}")
                    self._db.execute("COMMIT")
                except Exception:
                    with contextlib.suppress(Exception):
                        self._db.execute("ROLLBACK")
                    raise
                return results

            try:
                results = await asyncio.get_running_loop().run_in_executor(self._executor, execute)
            except Exception as exc:
                results = [(False, StorageError(f"SQLite commit failed: {type(exc).__name__}"))] * len(batch)
            for (_, _, future, committed), (ok, result) in zip(batch, results, strict=True):
                if ok and committed:
                    committed()
                if not future.done():
                    future.set_result(result) if ok else future.set_exception(result)
                self._queue.task_done()

    async def enqueue(self, account, peer, method, payload, context, idem=None, limit=4096, digest=None):
        digest = digest or hashlib.sha256(method.encode() + payload).hexdigest()
        now, operation_id = time.time(), uuid.uuid4().hex

        def insert(db):
            if idem is not None:
                old = db.execute(
                    "SELECT id,digest FROM operations WHERE account=? AND idem=?", (account, idem)
                ).fetchone()
                if old:
                    if old["digest"] != digest:
                        raise IdempotencyConflict("Idempotency key already belongs to another payload")
                    return old["id"]
            count = db.execute(
                "SELECT count(*) FROM operations WHERE account=? AND status IN "
                "('queued','waiting','running','uncertain')",
                (account,),
            ).fetchone()[0]
            if count >= limit:
                raise StorageError("Durable outbox is full")
            db.execute(
                "INSERT INTO operations(id,account,peer,method,payload,digest,idem,context,created,updated) "
                "VALUES(?,?,?,?,?,?,?,?,?,?)",
                (operation_id, account, peer, method, payload, digest, idem, context, now, now),
            )
            return operation_id

        return await self.run(insert)

    async def operation(self, account, operation_id):
        def load(db):
            row = db.execute(
                "SELECT * FROM operations WHERE id=? AND account=?", (operation_id, account)
            ).fetchone()
            if row is None:
                raise KeyError(operation_id)
            return dict(row)

        return await self.run(load, write=False)

    async def operation_page(self, account, *, statuses=None, after=None, limit=100):
        if not 1 <= limit <= 1000:
            raise ValueError("Invalid operation page size")

        def load(db):
            where, parameters = ["account=?"], [account]
            if statuses is not None:
                if not statuses:
                    return []
                where.append("status IN (" + ",".join("?" for _ in statuses) + ")")
                parameters.extend(statuses)
            if after is not None:
                where.append("(created,id)>(?,?)")
                parameters.extend(after)
            parameters.append(limit)
            # Payload, response, peer/access hash and message context stay private.
            query = (
                "SELECT id,status,method,attempts,error,not_before,cycle_attempts,created,"
                "json_object('_rpc_confirmed',json_extract(context,'$._rpc_confirmed'),"
                "'_history_verified',json_extract(context,'$._history_verified')) AS context "
                "FROM operations WHERE " + " AND ".join(where) + " ORDER BY created,id LIMIT ?"
            )
            return [dict(row) for row in db.execute(query, parameters)]

        return await self.run(load, write=False)

    async def commit_media_upload(self, account, operation_id, index, *, sha256, file_id, access_hash):
        """Merge a completed upload into its immutable item without replacing sibling commits."""

        def commit(db):
            row = db.execute(
                "SELECT context FROM operations WHERE id=? AND account=? AND status='running' AND in_flight=0",
                (operation_id, account),
            ).fetchone()
            if row is None:
                raise StorageError("Media operation is no longer preparing")
            context = json.loads(row["context"])
            item = context["media"][index]
            if item["sha256"] != sha256 or not file_id or not access_hash:
                raise StorageError("Uploaded file does not match the immutable item")
            if item.get("file_id") and (item["file_id"], item["access_hash"]) != (file_id, access_hash):
                raise StorageError("Uploaded item identity already committed")
            item.update(file_id=file_id, access_hash=access_hash)
            db.execute(
                "UPDATE operations SET context=?,updated=? WHERE id=? AND account=?",
                (json.dumps(context, ensure_ascii=False), time.time(), operation_id, account),
            )

        await self.run(commit)

    async def commit_media_payload(self, account, operation_id, payload, context):
        def commit(db):
            row = db.execute(
                "SELECT payload FROM operations WHERE id=? AND account=? AND status='running' AND in_flight=0",
                (operation_id, account),
            ).fetchone()
            if row is None or (row["payload"] and row["payload"] != payload):
                raise StorageError("Media operation is no longer preparing this payload")
            db.execute(
                "UPDATE operations SET payload=?,context=?,updated=? WHERE id=? AND account=?",
                (payload, context, time.time(), operation_id, account),
            )

        await self.run(commit)

    async def recover_operations(self, account):
        # A running operation might have reached the server before the process died.
        return await self.run(
            lambda db: (
                db.execute(
                    "UPDATE operations SET status=CASE WHEN in_flight=1 OR ambiguous=1 THEN 'uncertain' "
                    "WHEN not_before>? THEN 'waiting' ELSE 'queued' END, "
                    "error='process interrupted',updated=? "
                    "WHERE account=? AND status='running'",
                    (time.time(), time.time(), account),
                ).rowcount
            )
        )

    async def claim(self, account):
        def claim(db):
            row = db.execute(
                "SELECT o.* FROM operations o WHERE account=? AND status IN ('queued','waiting') "
                "AND not_before<=? AND NOT EXISTS (SELECT 1 FROM account_limits l "
                "WHERE l.account=o.account AND l.not_before>?) "
                "AND NOT EXISTS (SELECT 1 FROM operations p WHERE p.account=o.account AND p.peer=o.peer "
                "AND p.status IN ('queued','waiting','running','uncertain') "
                "AND (p.created<o.created OR (p.created=o.created AND p.rowid<o.rowid))) "
                "ORDER BY created,rowid LIMIT 1",
                (account, time.time(), time.time()),
            ).fetchone()
            if row is None:
                # Pending timed/rate/peer-blocked work must be reevaluated by
                # later probes. Only a physically empty dispatch queue is stable
                # until a mutation, even when wall-clock gates expire mid-batch.
                probe.empty_cacheable = (
                    db.execute(
                        "SELECT 1 FROM operations WHERE account=? AND status IN ('queued','waiting') LIMIT 1",
                        (account,),
                    ).fetchone()
                    is None
                )
                return None
            db.execute(
                "UPDATE operations SET status='running',updated=? WHERE id=?", (time.time(), row["id"])
            )
            return dict(row)

        probe = _ClaimProbe(account, claim)
        return await self.run(probe)

    async def attempted(self, account, operation_id):
        def attempt(db):
            cursor = db.execute(
                "UPDATE operations SET attempts=attempts+1,cycle_attempts=cycle_attempts+1,"
                "in_flight=1,updated=? WHERE id=? AND account=? "
                "AND status='running' AND cycle_attempts<3",
                (time.time(), operation_id, account),
            )
            if not cursor.rowcount:
                raise StorageError("Operation is no longer dispatchable")
            return db.execute("SELECT cycle_attempts FROM operations WHERE id=?", (operation_id,)).fetchone()[
                0
            ]

        return await self.run(attempt)

    async def reschedule(
        self, account, operation_id, *, delay=0, ambiguous=False, account_wait=False, error=None
    ):
        deadline = time.time() + max(0, delay)

        def schedule(db):
            if account_wait:
                db.execute(
                    "INSERT INTO account_limits VALUES(?,?) ON CONFLICT(account) DO UPDATE "
                    "SET not_before=max(not_before,excluded.not_before)",
                    (account, deadline),
                )
            db.execute(
                "UPDATE operations SET in_flight=0,ambiguous=max(ambiguous,?),not_before=?,"
                "status=CASE WHEN cycle_attempts>=3 THEN CASE WHEN ambiguous=1 OR ?=1 "
                "THEN 'uncertain' ELSE 'failed' END ELSE 'waiting' END,error=?,updated=? "
                "WHERE id=? AND account=? AND status='running'",
                (int(ambiguous), deadline, int(ambiguous), error, time.time(), operation_id, account),
            )
            return db.execute(
                "SELECT status FROM operations WHERE id=? AND account=?", (operation_id, account)
            ).fetchone()[0]

        return await self.run(
            schedule, _committed=lambda: self._remember_rate(account, deadline) if account_wait else None
        )

    def _remember_rate(self, account, deadline):
        self._rates[account] = max(self._rates.get(account, 0), deadline)

    def rate_deadline(self, account):
        return self._rates.get(account, 0)

    async def limit_account(self, account, delay):
        deadline = time.time() + max(0, delay)
        await self.run(
            lambda db: (
                db.execute(
                    "INSERT INTO account_limits VALUES(?,?) ON CONFLICT(account) DO UPDATE "
                    "SET not_before=max(not_before,excluded.not_before)",
                    (account, deadline),
                ).rowcount
            ),
            _committed=lambda: self._remember_rate(account, deadline),
        )

    async def retry(self, account, operation_id, *, allow_uncertain=False):
        return bool(
            await self.run(
                lambda db: (
                    db.execute(
                        "UPDATE operations SET ambiguous=CASE WHEN status='uncertain' THEN 1 ELSE ambiguous END,"
                        "status='queued',cycle_attempts=0,in_flight=0,not_before=0,error=NULL,"
                        "updated=? WHERE id=? AND account=? AND (status='failed' OR (status='uncertain' AND ?))",
                        (time.time(), operation_id, account, int(allow_uncertain)),
                    ).rowcount
                )
            )
        )

    async def finish(
        self, account, operation_id, status, *, response=None, error=None, basis="rpc", context_patch=None
    ):
        def finish(db):
            row = db.execute(
                "SELECT context,status FROM operations WHERE id=? AND account=?", (operation_id, account)
            ).fetchone()
            if row is None or row["status"] == "confirmed":
                return 0
            context = json.loads(row["context"])
            if context_patch:
                context.update(context_patch)
            if status == "confirmed":
                context["_rpc_confirmed"] = basis == "rpc"
                context["_history_verified"] = basis == "history"
            return db.execute(
                "UPDATE operations SET status=?,response=?,error=?,context=?,in_flight=0,updated=? "
                "WHERE id=? AND account=? AND status!='confirmed'",
                (
                    status,
                    response,
                    error,
                    json.dumps(context, ensure_ascii=False),
                    time.time(),
                    operation_id,
                    account,
                ),
            ).rowcount

        await self.run(finish)

    async def save_message_refs(self, account, operation_id, references):
        def save(db):
            row = db.execute(
                "SELECT context FROM operations WHERE id=? AND account=? AND status='confirmed'",
                (operation_id, account),
            ).fetchone()
            if row is None:
                raise StorageError("Message references require a confirmed operation")
            context = json.loads(row["context"])
            context["_message_refs"] = references
            context["_history_verified"] = True
            db.execute(
                "UPDATE operations SET context=?,updated=? WHERE id=? AND account=?",
                (json.dumps(context, ensure_ascii=False), time.time(), operation_id, account),
            )

        await self.run(save)

    async def cancel_unsent(self, account, operation_id):
        return bool(
            await self.run(
                lambda db: (
                    db.execute(
                        "UPDATE operations SET status='cancelled',updated=? "
                        "WHERE id=? AND account=? AND status IN ('queued','waiting') "
                        "AND in_flight=0 AND ambiguous=0",
                        (time.time(), operation_id, account),
                    ).rowcount
                )
            )
        )

    async def record(self, account, raw, events, states=()):
        now = time.time()

        def record(db):
            jid = db.execute(
                "INSERT INTO journal(account,raw,created) VALUES(?,?,?)", (account, raw, now)
            ).lastrowid
            ids = []
            for peer, kind, event_raw, dedupe in events:
                eid = uuid.uuid4().hex
                cursor = db.execute(
                    "INSERT OR IGNORE INTO inbox(id,account,peer,kind,raw,dedupe,journal_id,created,updated) "
                    "VALUES(?,?,?,?,?,?,?,?,?)",
                    (eid, account, peer, kind, event_raw, dedupe, jid, now, now),
                )
                if cursor.rowcount:
                    ids.append(eid)
                if kind in ("new", "edit", "delete"):
                    from .proto.struct_pb2 import WebUpdate

                    value = WebUpdate.FromString(event_raw)
                    if kind == "new":
                        item = (
                            value.messages.messageContainers[0]
                            if value.HasField("messages")
                            else value.message
                        )
                        if not item.groupedId.value:
                            continue
                        pending = db.execute(
                            "SELECT edit,deleted FROM album_pending WHERE account=? AND peer=? AND rid=?",
                            (account, peer, item.rid),
                        ).fetchone()
                        snapshot_raw = event_raw
                        if pending and pending["edit"]:
                            _apply_album_edit(value, pending["edit"])
                            snapshot_raw = value.SerializeToString()
                        inserted = db.execute(
                            "INSERT OR IGNORE INTO album_items(account,peer,grouped,rid,date,raw,deleted) "
                            "VALUES(?,?,?,?,?,?,?)",
                            (
                                account,
                                peer,
                                item.groupedId.value,
                                item.rid,
                                item.date,
                                snapshot_raw,
                                pending["deleted"] if pending else 0,
                            ),
                        )
                        if inserted.rowcount and pending:
                            db.execute(
                                "DELETE FROM album_pending WHERE account=? AND peer=? AND rid=?",
                                (account, peer, item.rid),
                            )
                        if not inserted.rowcount and value.HasField("messages"):
                            old = db.execute(
                                "SELECT raw,grouped,date FROM album_items WHERE account=? AND peer=? AND rid=?",
                                (account, peer, item.rid),
                            ).fetchone()
                            prior = WebUpdate.FromString(old[0]) if old else None
                            if (
                                prior is not None
                                and prior.HasField("message")
                                and old[1] == item.groupedId.value
                                and old[2] == item.date
                            ):
                                # Enrich a legacy compact snapshot with immutable full metadata,
                                # preserving later caption/content edits and deletion tombstones.
                                enriched = WebUpdate()
                                enriched.CopyFrom(value)
                                target = enriched.messages.messageContainers[0]
                                target.message.CopyFrom(prior.message.message)
                                if prior.message.HasField("quotedMessage"):
                                    target.quotedMessage.CopyFrom(prior.message.quotedMessage)
                                db.execute(
                                    "UPDATE album_items SET raw=? WHERE account=? AND peer=? AND rid=?",
                                    (enriched.SerializeToString(), account, peer, item.rid),
                                )
                    elif kind == "edit":
                        edited = value.messageContentChanged
                        old = db.execute(
                            "SELECT raw FROM album_items WHERE account=? AND peer=? AND rid=?",
                            (account, peer, edited.rid),
                        ).fetchone()
                        if old:
                            item = WebUpdate.FromString(old[0])
                            _apply_album_edit(item, event_raw)
                            db.execute(
                                "UPDATE album_items SET raw=? WHERE account=? AND peer=? AND rid=?",
                                (item.SerializeToString(), account, peer, edited.rid),
                            )
                        else:
                            _remember_album_mutation(db, account, peer, edited.rid, edit=event_raw)
                    elif kind == "delete":
                        for rid in value.messageDelete.rids:
                            changed = db.execute(
                                "UPDATE album_items SET deleted=1 WHERE account=? AND peer=? AND rid=?",
                                (account, peer, rid),
                            ).rowcount
                            if not changed:
                                _remember_album_mutation(db, account, peer, rid, deleted=1)
            for route, state, seq in states:
                db.execute(
                    "INSERT INTO routes(account,route,state,seq) VALUES(?,?,?,?) "
                    "ON CONFLICT(account,route) DO UPDATE SET state=excluded.state,seq=excluded.seq "
                    "WHERE excluded.seq>=routes.seq",
                    (account, route, state, seq),
                )
            return ids

        return await self.run(record, _committed=lambda: self._notify_inbox(account))

    async def routes(self, account):
        return await self.run(
            lambda db: [dict(r) for r in db.execute("SELECT * FROM routes WHERE account=?", (account,))],
            write=False,
        )

    async def pending_events(self, account, limit=100, exclude=()):
        def get(db):
            rows = db.execute(
                "SELECT * FROM inbox WHERE account=? AND status='pending' ORDER BY rowid", (account,)
            )
            result = []
            for row in rows:
                if row["id"] not in exclude:
                    result.append(dict(row))
                if len(result) >= limit:
                    break
            return result

        return await self.run(get, write=False)

    async def ack(self, account, event_id):
        await self.run(
            lambda db: (
                db.execute(
                    "UPDATE inbox SET status='acked',updated=? WHERE id=? AND account=?",
                    (time.time(), event_id, account),
                ).rowcount
            )
        )

    async def failed_event_page(self, account, *, after=0, limit=100):
        if not 1 <= limit <= 1000:
            raise ValueError("Invalid event page size")
        return await self.run(
            lambda db: [
                dict(row)
                for row in db.execute(
                    "SELECT rowid AS position,* FROM inbox "
                    "WHERE account=? AND status='quarantine' AND rowid>? ORDER BY rowid LIMIT ?",
                    (account, after, limit),
                )
            ],
            write=False,
        )

    async def fail_event(self, account, event_id, max_attempts, *, expected_attempts=None):
        def fail(db):
            # A retry after committed-but-unobserved completion must not count
            # another application failure or resurrect an acknowledged event.
            db.execute(
                "UPDATE inbox SET attempts=CASE WHEN attempts<? THEN attempts+1 ELSE attempts END,updated=?, "
                "status=CASE WHEN attempts+1>=? THEN 'quarantine' ELSE 'pending' END "
                "WHERE id=? AND account=? AND status='pending' "
                "AND (? IS NULL OR attempts=?)",
                (
                    max_attempts,
                    time.time(),
                    max_attempts,
                    event_id,
                    account,
                    expected_attempts,
                    expected_attempts,
                ),
            )
            row = db.execute(
                "SELECT status,attempts FROM inbox WHERE id=? AND account=?", (event_id, account)
            ).fetchone()
            return dict(row) if row else None

        return await self.run(fail)

    async def replay_event(self, account, event_id):
        return await self.run(
            lambda db: (
                db.execute(
                    "UPDATE inbox SET status='pending',attempts=0 "
                    "WHERE id=? AND account=? AND status='quarantine'",
                    (event_id, account),
                ).rowcount
            ),
            _committed=lambda: self._notify_inbox(account),
        )

    async def purge(self, retention_days):
        cutoff = time.time() - retention_days * 86400

        def purge(db):
            paths = []
            for row in db.execute(
                "SELECT context FROM operations WHERE updated<? "
                "AND status IN ('confirmed','failed','cancelled')",
                (cutoff,),
            ):
                paths.extend(item["path"] for item in json.loads(row[0]).get("media", []))
            db.execute(
                "DELETE FROM operations WHERE updated<? AND status IN ('confirmed','failed','cancelled')",
                (cutoff,),
            )
            db.execute("DELETE FROM inbox WHERE updated<? AND status='acked'", (cutoff,))
            db.execute(
                "DELETE FROM journal WHERE created<? AND NOT EXISTS "
                "(SELECT 1 FROM inbox WHERE journal_id=journal.id)",
                (cutoff,),
            )
            referenced = {
                str(Path(item["path"]).resolve())
                for row in db.execute("SELECT context FROM operations")
                for item in json.loads(row[0]).get("media", [])
            }
            return paths, referenced

        paths, referenced = await self.run(purge)
        protected = {
            str(path.resolve())
            for owners in self._spool_roots.values()
            for values in owners
            for path in values
        }
        roots = tuple(self._spool_roots)

        def cleanup():
            root = self.path.parent.resolve()
            removed = 0
            for name in paths:
                path = Path(name).resolve()
                if (
                    str(path) not in referenced | protected
                    and path.is_relative_to(root)
                    and path.parent.name == "spool"
                    and path.suffix == ".media"
                ):
                    path.unlink(missing_ok=True)
                    removed += 1
            for spool in roots:
                if not spool.is_dir():
                    continue
                for path in spool.glob("*.media"):
                    if (
                        not re.fullmatch(r"[0-9a-f]{32}\.media", path.name)
                        or path.is_symlink()
                        or not path.is_file()
                        or path.resolve().parent != spool
                    ):
                        continue
                    if str(path.resolve()) in referenced | protected or path.stat().st_mtime >= cutoff:
                        continue
                    path.unlink(missing_ok=True)
                    removed += 1
            return removed

        return await asyncio.to_thread(cleanup)

    async def maintain(self, retention_days):
        if time.monotonic() - self._last_purge < 3600:
            return
        # A pool shares one store: concurrent account supervisors must not each
        # scan every account's journal/spool during the same hourly pass.
        async with self._maintenance_lock:
            if time.monotonic() - self._last_purge >= 3600:
                await self.purge(retention_days)
                self._last_purge = time.monotonic()

    async def close(self):
        if self._close_task is None:
            self._closing = True
            self._close_task = asyncio.create_task(self._close_once(), name="fncbale-store-close")
            self._close_task.add_done_callback(
                lambda task: task.exception() if not task.cancelled() else None
            )
        await asyncio.shield(self._close_task)

    async def _close_once(self):
        async with self._admission_lock:
            if self._closed:
                return
            self._closing = True
        if self._start_task:
            with contextlib.suppress(Exception):
                await asyncio.shield(self._start_task)
        if self._task:
            await self._queue.put(None)
            await self._task
            await asyncio.get_running_loop().run_in_executor(self._executor, self._db.close)
        self._closed = True
        for watchers in self._inbox_watchers.values():
            for wake in watchers:
                wake.set()
        self._inbox_watchers.clear()
        self._executor.shutdown(wait=True)
