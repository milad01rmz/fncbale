"""Concurrent typed pool/outbox/inbox/stream/restart QA; modeled transports, real SQLite/files."""

import argparse
import asyncio
from collections import defaultdict, deque
import gc
import hashlib
import io
import json
from pathlib import Path
import platform
import random
import tempfile
import time
import uuid
from unittest.mock import patch

import httpx
from PIL import Image

from fncbale import (
    AccountPool,
    Config,
    Media,
    MediaKind,
    Peer,
    PeerKind,
    ProtocolProfile,
    Session,
    __version__,
    contract,
)
from fncbale.errors import RpcError, TransportError
from fncbale.proto import struct_pb2 as s
from fncbale.transports import WebSocketTransport

try:
    from .cache_memory_qa import memory
    from .qa_model import ModelServer
except ImportError:
    from cache_memory_qa import memory
    from qa_model import ModelServer


class MixedServer(ModelServer):
    def __init__(self, uids, controlled_overlap=False):
        super().__init__()
        self.uids = uids
        self.controlled_overlap = controlled_overlap
        self.overlap_put_entered, self.overlap_get_entered = asyncio.Event(), asyncio.Event()
        self.first_get_gated = False
        self.lost_ack.add(uids[0])
        self.limited.add(uids[1])
        self.drop_live.update(uids[::3])
        self.owners, self.content_pool = {}, {}
        self.accepted, self.reissued = set(), 0
        self.rpc_active, self.rpc_peak = 0, 0
        self.rpc_account_active, self.rpc_account_peak = defaultdict(int), defaultdict(int)
        self.transfer_active = {"PUT": 0, "GET": 0}
        self.transfer_peak = {"PUT": 0, "GET": 0}
        self.transfer_account_active, self.transfer_account_peak = defaultdict(int), defaultdict(int)
        self.overlap = {"rpc_and_transfer": False, "put_and_get": False}
        self.faults = defaultdict(int)
        self.transferred = {"PUT": 0, "GET": 0}
        self.ws_batch_failures, self.batch_http_calls = 0, 0

    def overlap_check(self):
        self.overlap["rpc_and_transfer"] |= bool(self.rpc_active and sum(self.transfer_active.values()))
        self.overlap["put_and_get"] |= bool(self.transfer_active["PUT"] and self.transfer_active["GET"])

    def transfer_enter(self, method, uid):
        self.transfer_active[method] += 1
        self.transfer_peak[method] = max(self.transfer_peak[method], self.transfer_active[method])
        key = (method, uid)
        self.transfer_account_active[key] += 1
        self.transfer_account_peak[key] = max(
            self.transfer_account_peak[key], self.transfer_account_active[key]
        )
        self.overlap_check()

    def transfer_leave(self, method, uid):
        self.transfer_active[method] -= 1
        self.transfer_account_active[method, uid] -= 1

    async def rpc(self, uid, method, payload):
        self.rpc_active += 1
        self.rpc_peak = max(self.rpc_peak, self.rpc_active)
        self.rpc_account_active[uid] += 1
        self.rpc_account_peak[uid] = max(self.rpc_account_peak[uid], self.rpc_account_active[uid])
        self.overlap_check()
        request = contract(method).request.FromString(payload)
        ids = []
        if method == "SendMessage":
            ids = [request.rid]
        elif method == "SendMultiMediaMessage":
            ids = [item.randomId for item in request.multiMedia]
        try:
            if method == "GetNasimFileUrls":
                self.calls[uid, method] += 1
                await asyncio.sleep(0.003)
                response = contract(method).response()
                for item in reversed(request.files):
                    response.fileUrls.add(fileId=item.fileId, url=f"https://files.invalid/{item.fileId}")
                return response.SerializeToString()
            try:
                result = await super().rpc(uid, method, payload)
            except TransportError as error:
                if error.possibly_sent:
                    self.faults["lost_ack"] += 1
                    self.accept_writes(uid, ids)
                raise
            except RpcError as error:
                if error.code == 8:
                    self.faults["rate_limit"] += 1
                raise
            self.accept_writes(uid, ids)
            if method == "GetNasimFileUploadUrl":
                allocation = contract(method).response.FromString(result)
                self.owners[allocation.fileId] = uid
            return result
        finally:
            self.rpc_active -= 1
            self.rpc_account_active[uid] -= 1

    def accept_writes(self, uid, ids):
        for rid in ids:
            self.reissued += (uid, rid) in self.accepted
            self.accepted.add((uid, rid))

    async def websocket_rpc(self, transport, service, method, payload):
        uid = int(transport._token.split("synthetic-")[1])
        if uid == self.uids[4] and method == "GetNasimFileUrls" and self.ws_batch_failures < 2:
            self.ws_batch_failures += 1
            raise TransportError("modeled pre-dispatch read failure")
        return await self.rpc(uid, method, payload)

    async def http_rpc(self, request):
        if request.url.path.rsplit("/", 1)[1] == "GetNasimFileUrls":
            self.batch_http_calls += 1
        return await super().http_rpc(request)


class FileStream(httpx.AsyncByteStream):
    def __init__(self, server, file_id):
        self.server, self.file_id = server, file_id

    async def __aiter__(self):
        server, uid = self.server, self.server.owners[self.file_id]
        server.transfer_enter("GET", uid)
        try:
            if server.controlled_overlap and not server.first_get_gated:
                server.first_get_gated = True
                server.overlap_get_entered.set()
                await server.overlap_put_entered.wait()
            content = server.files[self.file_id]
            for offset in range(0, len(content), 16384):
                await asyncio.sleep(0.002)
                chunk = content[offset : offset + 16384]
                server.transferred["GET"] += len(chunk)
                yield chunk
                if uid == server.uids[2] and not server.faults["get_interruption"]:
                    server.faults["get_interruption"] += 1
                    raise httpx.ReadError("modeled streamed GET interruption")
        finally:
            server.transfer_leave("GET", uid)


class FileTransport(httpx.AsyncBaseTransport):
    def __init__(self, server):
        self.server = server

    async def handle_async_request(self, request):
        server = self.server
        file_id = int(request.url.path.strip("/"))
        uid = server.owners[file_id]
        if request.method == "PUT":
            server.transfer_enter("PUT", uid)
            try:
                if (
                    server.controlled_overlap
                    and uid == server.uids[5]
                    and not server.overlap_put_entered.is_set()
                ):
                    server.overlap_put_entered.set()
                    await server.overlap_get_entered.wait()
                chunks = []
                async for chunk in request.stream:
                    await asyncio.sleep(0.002)
                    server.transferred["PUT"] += len(chunk)
                    if uid == server.uids[0] and not server.faults["put_interruption"]:
                        server.faults["put_interruption"] += 1
                        raise httpx.WriteError("modeled streamed PUT interruption")
                    chunks.append(chunk)
                content = b"".join(chunks)
                digest = hashlib.sha256(content).digest()
                server.files[file_id] = server.content_pool.setdefault(digest, content)
                return httpx.Response(200)
            finally:
                server.transfer_leave("PUT", uid)
        if uid == server.uids[5] and not server.faults["expired_url"]:
            server.faults["expired_url"] += 1
            return httpx.Response(403)
        return httpx.Response(200, stream=FileStream(server, file_id))


def photo(seed, size=(192, 128)):
    output = io.BytesIO()
    image = Image.frombytes("RGB", size, random.Random(seed).randbytes(size[0] * size[1] * 3))
    image.save(output, format="PNG")
    return output.getvalue()


async def scenario(
    accounts=6,
    rounds=1,
    *,
    seconds=None,
    audit=None,
    controlled_overlap=False,
    measure_memory=False,
    photo_size=(192, 128),
    stream_chunk_size=16384,
):
    audit = {} if audit is None else audit
    if accounts < 6 or rounds < 1 or (seconds is not None and seconds <= 0):
        raise ValueError("At least six model accounts and positive rounds/duration required")
    if len(photo_size) != 2 or any(not 1 <= edge <= 2048 for edge in photo_size):
        raise ValueError("Photo fixture dimensions must be1..2048")
    uids = list(range(99500001, 99500001 + accounts))
    server = MixedServer(uids, controlled_overlap)
    config = Config(
        profile=ProtocolProfile(grpc_url=f"https://mixed-{uuid.uuid4().hex}.invalid"),
        global_rpc_limit=8,
        rpc_limit=3,
        global_upload_limit=4,
        upload_limit=2,
        global_download_limit=4,
        download_limit=2,
        metadata_workers=2,
        queue_size=32,
        outbox_workers=3,
        recovery_interval=0.15,
        stream_chunk_size=stream_chunk_size,
    )
    contents = [photo(1, photo_size), photo(2, photo_size)]
    hashes = [hashlib.sha256(value).hexdigest() for value in contents]
    completed = defaultdict(lambda: {"text": 0, "album": 0, "hashes": 0})
    peaks = {"store_queue": 0, "raw_per_account": 0, "leased_per_account": 0, "waiters_per_account": 0}
    lag_samples = deque(maxlen=10000)
    stop, start = asyncio.Event(), asyncio.Event()
    pool = None
    wall_started, cpu_started = time.perf_counter(), time.process_time()
    memory_samples = deque(maxlen=512)
    memory_stages = {}
    memory_sample_count, sampled_rss_peak = 0, 0

    def memory_snapshot():
        # Whole-process OS readings include this driver and retained server fixtures.
        # Deduplicated byte counts describe fixture content, not SDK allocations.
        file_objects = {id(content): content for content in server.files.values()}
        return {
            "elapsed_seconds": time.perf_counter() - wall_started,
            **memory(),
            "model_log_frames": sum(len(values) for values in server.logs.values()),
            "model_log_bytes": sum(len(frame) for values in server.logs.values() for frame in values),
            "model_message_objects": sum(len(values) for values in server.messages.values()),
            "model_file_references": len(server.files),
            "model_unique_file_bytes": sum(len(content) for content in file_objects.values()),
            "sdk_retained_peer_keys": sum(len(client._peer_cache) for client in pool.clients.values())
            if pool is not None
            else 0,
        }

    if measure_memory:
        memory_stages["before_pool"] = memory_snapshot()

    async def observe():
        nonlocal memory_sample_count, sampled_rss_peak
        expected = asyncio.get_running_loop().time() + 0.02
        next_memory = expected
        while True:
            await asyncio.sleep(0.02)
            now = asyncio.get_running_loop().time()
            lag_samples.append(max(0, now - expected))
            expected = now + 0.02
            if pool is not None:
                peaks["store_queue"] = max(peaks["store_queue"], pool.store._queue.qsize())
                for client in pool.clients.values():
                    peaks["raw_per_account"] = max(peaks["raw_per_account"], client._ws.updates.qsize())
                    peaks["leased_per_account"] = max(peaks["leased_per_account"], len(client._leased_events))
                    peaks["waiters_per_account"] = max(
                        peaks["waiters_per_account"], len(client._operation_waiters)
                    )
            if measure_memory and now >= next_memory:
                sample = memory_snapshot()
                memory_samples.append(sample)
                memory_sample_count += 1
                sampled_rss_peak = max(sampled_rss_peak, sample["rss_bytes"])
                next_memory = now + 1

    async def wire_connect(transport):
        await server.connect(transport)

    async def wire_request(transport, service, method, payload):
        return await server.websocket_rpc(transport, service, method, payload)

    with tempfile.TemporaryDirectory(prefix="fncbale-mixed-") as directory:
        root = Path(directory).resolve()
        assert root.parent == Path(tempfile.gettempdir()).resolve() and root.name.startswith("fncbale-mixed-")

        async def make_pool():
            current = AccountPool(data_dir=root, config=config)
            try:
                await current.resources.http.aclose()
                current.resources.http = httpx.AsyncClient(transport=FileTransport(server))
                await current.store.start()
                await current.store.run(
                    lambda db: [
                        db.execute(statement)
                        for statement in (
                            "CREATE TABLE IF NOT EXISTS qa_deliveries(account TEXT,id TEXT,deliveries INTEGER,PRIMARY KEY(account,id))",
                            "CREATE TABLE IF NOT EXISTS qa_order(account TEXT,peer TEXT,last INTEGER,PRIMARY KEY(account,peer))",
                            "CREATE TABLE IF NOT EXISTS qa_attempts(account TEXT,id TEXT,attempts INTEGER,PRIMARY KEY(account,id))",
                        )
                    ]
                )
                for uid in uids:
                    client = current.add(str(uid), Session(uid, f"synthetic-{uid}"))
                    await client._grpc.http.aclose()
                    client._grpc.http = httpx.AsyncClient(transport=httpx.MockTransport(server.http_rpc))

                    @client.router.on()
                    async def consume(event, client=client):
                        if (
                            client.session.user_id == uids[0]
                            and event.message
                            and event.message.text == "retry-handler"
                        ):

                            def attempted(db):
                                value = db.execute(
                                    "SELECT attempts FROM qa_attempts WHERE account=? AND id=?",
                                    (client.account, event.event_id),
                                ).fetchone()
                                count = (value[0] if value else 0) + 1
                                db.execute(
                                    "INSERT INTO qa_attempts VALUES(?,?,?) ON CONFLICT(account,id) DO UPDATE SET attempts=excluded.attempts",
                                    (client.account, event.event_id, count),
                                )
                                return count

                            if await client.store.run(attempted) <= 2:
                                server.faults["handler_failure"] += 1
                                raise RuntimeError("modeled application failure")
                        if client.session.user_id % 5 == 0:
                            await asyncio.sleep(0.003)

                        def delivered(db):
                            rowid = db.execute(
                                "SELECT rowid FROM inbox WHERE account=? AND id=?",
                                (client.account, event.event_id),
                            ).fetchone()[0]
                            peer = event.peer.key if event.peer else "unknown"
                            last = db.execute(
                                "SELECT last FROM qa_order WHERE account=? AND peer=?", (client.account, peer)
                            ).fetchone()
                            assert last is None or rowid >= last[0], (
                                "Registered per-peer delivery order regressed"
                            )
                            db.execute(
                                "INSERT INTO qa_order VALUES(?,?,?) ON CONFLICT(account,peer) DO UPDATE SET last=excluded.last",
                                (client.account, peer, rowid),
                            )
                            db.execute(
                                "INSERT INTO qa_deliveries VALUES(?,?,1) ON CONFLICT(account,id) DO UPDATE SET deliveries=deliveries+1",
                                (client.account, event.event_id),
                            )

                        await client.store.run(delivered)

                    await client.resolve_peer(Peer(PeerKind.CHANNEL, 101))
                    await client.resolve_peer(Peer(PeerKind.CHANNEL, 102))
                await asyncio.gather(*(client.connect() for client in current.clients.values()))
                return current
            except BaseException:
                await current.close()
                raise

        async def text_lane(client):
            await start.wait()
            uid, number = client.session.user_id, 0
            while (seconds is not None and not stop.is_set()) or (seconds is None and number < rounds):
                text = "retry-handler" if uid == uids[0] and number == 0 else f"text-{number}"
                message = await client.send_message(
                    Peer(PeerKind.CHANNEL, 102), text, idempotency_key=f"text-{number}"
                )
                replay = await client.send_message(
                    Peer(PeerKind.CHANNEL, 102), text, idempotency_key=f"text-{number}"
                )
                assert replay.rid == message.rid
                await client.edit_message(message, f"edit-{number}")
                await client.delete_message(message)
                completed[uid]["text"] += 1
                number += 1

        async def media_lane(client):
            await start.wait()
            uid, number = client.session.user_id, 0
            while (seconds is not None and not stop.is_set()) or (seconds is None and number < rounds):
                album = await client.send_album(
                    Peer(PeerKind.CHANNEL, 101),
                    [
                        Media(value, MediaKind.PHOTO, f"caption-{index}")
                        for index, value in enumerate(contents)
                    ],
                    idempotency_key=f"album-{number}",
                )
                targets = root / f"downloads-{uid}"
                if uid == uids[3] and number == 0:
                    entered = asyncio.Event()
                    targets.mkdir(exist_ok=True)
                    previous = targets / f"01-{album.messages[0].rid}.png"
                    # Use explicit jobs so the cancelled target name is unambiguous.
                    previous.write_bytes(b"previous")

                    async def pause(index, done, total, entered=entered):
                        if index == 0:
                            entered.set()
                            await asyncio.Event().wait()

                    task = asyncio.create_task(
                        client.download_many(
                            [(album.messages[0], previous), (album.messages[1], targets / "other.png")],
                            expected_sha256=hashes,
                            progress=pause,
                        )
                    )
                    try:
                        await asyncio.wait_for(entered.wait(), 30)
                        task.cancel()
                        await asyncio.gather(task, return_exceptions=True)
                        assert task.cancelled() and previous.read_bytes() == b"previous"
                        assert not list(targets.glob("*.part"))
                        server.faults["download_cancel"] += 1
                    finally:
                        if not task.done():
                            task.cancel()
                            await asyncio.gather(task, return_exceptions=True)
                paths = await client.download_album(album, targets, expected_sha256=hashes)
                actual = await asyncio.to_thread(
                    lambda paths=paths: [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]
                )
                assert actual == hashes
                await client.edit_caption(album.messages[0], f"changed-{number}")
                await client.delete_messages(album.messages)
                completed[uid]["album"] += 1
                completed[uid]["hashes"] += 2
                number += 1

        with (
            patch.object(WebSocketTransport, "connect", wire_connect),
            patch.object(WebSocketTransport, "request", wire_request),
        ):
            observer = asyncio.create_task(observe())
            try:
                audit["phase"] = "connecting-initial-pool"
                pool = await make_pool()
                audit["phase"] = "concurrent-traffic"
                tasks = [
                    asyncio.create_task(lane(client))
                    for client in pool.clients.values()
                    for lane in (text_lane, media_lane)
                ]
                start.set()
                traffic_started = time.perf_counter()
                try:
                    if seconds is not None:
                        await asyncio.sleep(seconds)
                        stop.set()
                    async with asyncio.timeout(max(90, accounts * rounds * 2)):
                        await asyncio.gather(*tasks)
                finally:
                    for task in tasks:
                        if not task.done():
                            task.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
                traffic_seconds = time.perf_counter() - traffic_started
                if measure_memory:
                    memory_stages["traffic_drained"] = memory_snapshot()
                audit.update(
                    phase="traffic-drained",
                    traffic_seconds=traffic_seconds,
                    completed_cycles=sum(value["text"] + value["album"] for value in completed.values()),
                    queue_peaks=peaks,
                    faults=dict(server.faults),
                )
                await asyncio.gather(*(client.recover() for client in pool.clients.values()))
                # Freeze outbox workers only in the QA harness to establish the
                # exact accepted-unsent crash boundary before closing the pool.
                workers = [
                    task
                    for client in pool.clients.values()
                    for task in client._tasks
                    if task.get_name().startswith("fncbale-outbox-")
                ]
                for task in workers:
                    task.cancel()
                await asyncio.gather(*workers, return_exceptions=True)
                queued = {}
                for client in pool.clients.values():
                    handle = await client.enqueue_message(
                        Peer(PeerKind.CHANNEL, 102), "accepted-before-restart", idempotency_key="restart"
                    )
                    row = await client.store.operation(client.account, handle.operation_id)
                    assert row["status"] == "queued" and not row["in_flight"]
                    queued[client.session.user_id] = (
                        handle.operation_id,
                        contract("SendMessage").request.FromString(row["payload"]).rid,
                    )
                await pool.close()
                pool = None
                audit["phase"] = "offline-mutations"
                for uid in uids:
                    for peer_id in (101, 102):
                        request = contract("SendMessage").request(rid=2**60 + peer_id)
                        request.peer.type, request.peer.id = 2, peer_id
                        request.message.textMessage.text = "offline"
                        await server.rpc(uid, "SendMessage", request.SerializeToString())
                        edit = contract("UpdateMessage").request(rid=request.rid)
                        edit.peer.CopyFrom(request.peer)
                        edit.updatedMessage.textMessage.text = "offline-edit"
                        await server.rpc(uid, "UpdateMessage", edit.SerializeToString())
                        delete = contract("DeleteMessage").request(rids=[request.rid])
                        delete.peer.CopyFrom(request.peer)
                        delete.dates.dates.append(server.messages[uid, peer_id][request.rid].date)
                        await server.rpc(uid, "DeleteMessage", delete.SerializeToString())
                audit["phase"] = "connecting-restarted-pool"
                pool = await make_pool()
                if measure_memory:
                    memory_stages["reconnected"] = memory_snapshot()
                audit["phase"] = "waiting-accepted-restart-operations"
                audit["restart_operation_states"] = await pool.store.run(
                    lambda db: [
                        list(row)
                        for row in db.execute("SELECT status,count(*) FROM operations GROUP BY status")
                    ],
                    write=False,
                )
                for client in pool.clients.values():
                    operation_id, rid = queued[client.session.user_id]
                    message = await asyncio.wait_for(client.wait_operation(operation_id), 60)
                    assert message.rid == rid
                await asyncio.gather(*(client.recover() for client in pool.clients.values()))
                audit["phase"] = "draining-inbox"
                async with asyncio.timeout(max(90, accounts * 2)):
                    while True:
                        pending, quarantine = await pool.store.run(
                            lambda db: (
                                db.execute("SELECT count(*) FROM inbox WHERE status!='acked'").fetchone()[0],
                                db.execute("SELECT count(*) FROM inbox WHERE status='quarantine'").fetchone()[
                                    0
                                ],
                            ),
                            write=False,
                        )
                        assert quarantine == 0
                        if not pending:
                            break
                        await asyncio.sleep(0.05)
                for client in pool.clients.values():
                    for row in await pool.store.routes(client.account):
                        peer_id = 0 if row["route"] == "global" else int(row["route"])
                        assert row["seq"] == len(server.logs[client.session.user_id, peer_id])
                    rows = await pool.store.run(
                        lambda db, account=client.account: db.execute(
                            "SELECT kind,raw FROM inbox WHERE account=?", (account,)
                        ).fetchall(),
                        write=False,
                    )
                    for peer_id in (101, 102):
                        rid = 2**60 + peer_id
                        kinds = set()
                        for kind, raw in rows:
                            update = s.WebUpdate.FromString(raw)
                            if (
                                (kind == "new" and update.message.rid == rid)
                                or (kind == "edit" and update.messageContentChanged.rid == rid)
                                or (kind == "delete" and rid in update.messageDelete.rids)
                            ):
                                kinds.add(kind)
                        assert kinds == {"new", "edit", "delete"}
                totals = await pool.store.run(
                    lambda db: {
                        "operations": db.execute("SELECT count(*) FROM operations").fetchone()[0],
                        "confirmed": db.execute(
                            "SELECT count(*) FROM operations WHERE status='confirmed'"
                        ).fetchone()[0],
                        "inbox": db.execute("SELECT count(*) FROM inbox").fetchone()[0],
                        "acked": db.execute("SELECT count(*) FROM inbox WHERE status='acked'").fetchone()[0],
                        "delivered_unique": db.execute("SELECT count(*) FROM qa_deliveries").fetchone()[0],
                        "redeliveries": db.execute(
                            "SELECT coalesce(sum(deliveries-1),0) FROM qa_deliveries"
                        ).fetchone()[0],
                    },
                    write=False,
                )
                expected_ops = (
                    sum((value["text"] + value["album"]) * 3 for value in completed.values()) + accounts
                )
                assert totals["operations"] == totals["confirmed"] == expected_ops
                audit.update(
                    phase="verifying-limits",
                    totals=totals,
                    transfer_peaks=server.transfer_peak,
                    overlap=server.overlap,
                )
                assert totals["inbox"] == totals["acked"] == totals["delivered_unique"]
                assert len(completed) == accounts and all(
                    value["text"] and value["album"] for value in completed.values()
                )
                assert server.faults == {
                    "lost_ack": 1,
                    "rate_limit": 1,
                    "put_interruption": 1,
                    "get_interruption": 1,
                    "expired_url": 1,
                    "handler_failure": 2,
                    "download_cancel": 1,
                }
                assert server.ws_batch_failures == 2 and server.batch_http_calls >= 1 and server.reissued == 0
                assert (
                    server.rpc_peak <= config.global_rpc_limit
                    and max(server.rpc_account_peak.values()) <= config.rpc_limit
                )
                assert (
                    server.transfer_peak["PUT"] <= config.global_upload_limit
                    and server.transfer_peak["GET"] <= config.global_download_limit
                )
                assert (
                    max(
                        value
                        for (method, _), value in server.transfer_account_peak.items()
                        if method == "PUT"
                    )
                    <= config.upload_limit
                )
                assert (
                    max(
                        value
                        for (method, _), value in server.transfer_account_peak.items()
                        if method == "GET"
                    )
                    <= config.download_limit
                )
                assert server.overlap["rpc_and_transfer"] and not server.errors, (
                    server.overlap,
                    server.errors,
                )
                assert all(
                    value <= config.queue_size for key, value in peaks.items() if key != "waiters_per_account"
                )
            finally:
                if pool is not None:
                    await pool.close()
                observer.cancel()
                await asyncio.gather(observer, return_exceptions=True)
        assert not server.rpc_active and not any(server.transfer_active.values())
        assert all(
            not client._operation_waiters and not client._leased_events for client in pool.clients.values()
        )
        if measure_memory:
            gc.collect()
            memory_stages["closed_model_retained"] = memory_snapshot()
    ordered = sorted(lag_samples)

    def percentile(value):
        return ordered[min(len(ordered) - 1, int((len(ordered) - 1) * value))] if ordered else 0

    return {
        "pass": True,
        "version": __version__,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "accounts": accounts,
        "requested_seconds": seconds,
        "rounds_if_fixed": rounds if seconds is None else None,
        "input_photo_dimensions": list(photo_size),
        "input_file_sizes": [len(content) for content in contents],
        "sdk_stream_chunk_size": config.stream_chunk_size,
        "wall_seconds": time.perf_counter() - wall_started,
        "cpu_seconds": time.process_time() - cpu_started,
        "traffic_seconds_including_drain": traffic_seconds,
        **totals,
        "text_cycles": sum(value["text"] for value in completed.values()),
        "album_cycles": sum(value["album"] for value in completed.values()),
        "independent_file_hashes": sum(value["hashes"] for value in completed.values()),
        "rpc_peak": server.rpc_peak,
        "rpc_account_peak": max(server.rpc_account_peak.values()),
        "transfer_peaks": server.transfer_peak,
        "transferred_bytes_including_retries": server.transferred,
        "actual_overlap": server.overlap,
        "controlled_overlap_fixture": controlled_overlap,
        "faults": dict(server.faults),
        "ws_read_failures": server.ws_batch_failures,
        "http_read_fallbacks": server.batch_http_calls,
        "accepted_write_reissues": server.reissued,
        "restart_accepted_operations": accounts,
        "offline_all_route_mutations_verified": True,
        "queue_peaks": peaks,
        "loop_lag_p50": percentile(0.5),
        "loop_lag_p95": percentile(0.95),
        "loop_lag_p99": percentile(0.99),
        "loop_lag_max": max(ordered, default=0),
        "loop_samples": len(ordered),
        "process_memory": {
            "enabled": measure_memory,
            "sample_count": memory_sample_count,
            "sampled_rss_peak_bytes": sampled_rss_peak if measure_memory else None,
            "stages": memory_stages,
            "samples": list(memory_samples),
            "scope": "Whole-process OS RSS/HWM (and Windows private commit), sampled at most once/second; bounded512 retained samples. Driver, synthetic server history/files, imports, allocator and measurement work included. Model byte counts are not total fixture heap or SDK memory attribution. HWM includes setup/restart; close retains server fixture and Python arenas. Not100 real accounts or real-service performance.",
        },
        "scope": "Real typed SDK/SQLite FULL WAL/spool/stream/hash/handlers and same-process pool restart; modeled WS request adapter and streamed HTTP transport with artificial per-chunk delays. No fresh auth, process-kill, real-server throughput, or wire correlation claim. Driver/model work included in CPU/loop timing; queues sampled every20ms, not exact all-time peaks. Optional OS process RAM includes fixtures and is reported separately.",
    }


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--accounts", type=int, default=6)
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--seconds", type=float)
    parser.add_argument("--measure-memory", action="store_true")
    parser.add_argument("--photo-width", type=int, default=192)
    parser.add_argument("--photo-height", type=int, default=128)
    parser.add_argument("--stream-chunk-size", type=int, default=16384)
    parser.add_argument("--output", type=Path, default=Path("docs/qa/mixed-pool-0113.json"))
    args = parser.parse_args()
    audit = {}
    try:
        result = await scenario(
            args.accounts,
            args.rounds,
            seconds=args.seconds,
            audit=audit,
            measure_memory=args.measure_memory,
            photo_size=(args.photo_width, args.photo_height),
            stream_chunk_size=args.stream_chunk_size,
        )
    except Exception as exc:
        args.output.with_suffix(".failed.json").write_text(
            json.dumps(
                {
                    "pass": False,
                    "version": __version__,
                    "error": type(exc).__name__,
                    "accounts": args.accounts,
                    "seconds": args.seconds,
                    **audit,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        raise
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
