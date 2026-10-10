"""Pool/typed RPC/album/recovery fault QA against a synthetic server model."""

import asyncio
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import time
import tracemalloc
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
    contract,
    __version__,
)
from fncbale.transports import WebSocketTransport
from fncbale.errors import DeliveryUncertain
from fncbale.proto import struct_pb2 as s

try:
    from .qa_model import ModelServer
except ImportError:
    from qa_model import ModelServer


async def scenario(accounts=20, rounds=5, *, observe_memory=False, audit=None):
    audit = audit if audit is not None else {}
    server = ModelServer()
    config = Config(
        profile=ProtocolProfile(grpc_url=f"https://model-{uuid.uuid4().hex}.invalid"),
        global_rpc_limit=8,
        rpc_limit=3,
        queue_size=32,
        recovery_interval=0.2,
    )
    uids = list(range(99000001, 99000001 + accounts))
    server.lost_ack.add(uids[0])
    server.limited.add(uids[1])
    server.drop_live.add(uids[-1])
    started = time.monotonic()
    snapshots = []
    peaks = {
        "raw_per_account": 0,
        "leased_per_account": 0,
        "waiters_per_account": 0,
        "background_per_account": 0,
        "store_queue": 0,
    }
    audit.update(memory_samples=snapshots, queue_and_task_peaks=peaks)
    active_pool = None

    async def observe():
        while True:
            current = active_pool
            if current:
                peaks["store_queue"] = max(peaks["store_queue"], current.store._queue.qsize())
                for client in current.clients.values():
                    for key, value in (
                        ("raw_per_account", client._ws.updates.qsize() if client._ws else 0),
                        ("leased_per_account", len(client._leased_events)),
                        ("waiters_per_account", len(client._operation_waiters)),
                        ("background_per_account", sum(not t.done() for t in client._tasks)),
                    ):
                        peaks[key] = max(peaks[key], value)
            del current
            await asyncio.sleep(0.1)

    async def snapshot(stage):
        if not observe_memory:
            return

        def measure():
            pattern = str(Path(__file__).resolve().parents[1] / "src" / "fncbale" / "*")
            snapshot = tracemalloc.take_snapshot().filter_traces((tracemalloc.Filter(True, pattern),))
            return sum(stat.size for stat in snapshot.statistics("filename"))

        snapshots.append({"stage": stage, "sdk_attributed_python_bytes": await asyncio.to_thread(measure)})
        print(json.dumps(snapshots[-1]), flush=True)

    async def wire_connect(transport):
        await server.connect(transport)

    async def wire_request(transport, service, method, payload):
        return await server.websocket_rpc(transport, service, method, payload)

    with tempfile.TemporaryDirectory(prefix="fncbale-multi-") as directory:
        root = Path(directory)
        image = root / "photo.png"
        Image.new("RGB", (32, 24), "red").save(image)

        async def make_pool():
            nonlocal active_pool
            pool = AccountPool(data_dir=root, config=config)
            await pool.resources.http.aclose()
            pool.resources.http = httpx.AsyncClient(transport=httpx.MockTransport(server.file_http))
            for uid in uids:
                client = pool.add(str(uid), Session(uid, f"synthetic-{uid}"))
                await client._grpc.http.aclose()
                client._grpc.http = httpx.AsyncClient(transport=httpx.MockTransport(server.http_rpc))

                @client.router.on()
                async def capture(event, current=client):
                    if event.peer and event.peer.id == 101:
                        await asyncio.sleep(0.002)
                    await current.fsm.update("received", lambda count: (count or 0) + 1)

            await asyncio.gather(*(client.connect() for client in pool.clients.values()))
            active_pool = pool
            return pool

        with (
            patch.object(WebSocketTransport, "connect", wire_connect),
            patch.object(WebSocketTransport, "request", wire_request),
        ):
            pool = await make_pool()
            observer = asyncio.create_task(observe())
            try:
                await snapshot("connected")

                async def exercise(client):
                    for number in range(rounds):
                        peer = Peer(PeerKind.CHANNEL, 101 + number % 2)
                        try:
                            message = await client.send_message(
                                peer, f"round-{number}", idempotency_key=f"round-{number}"
                            )
                        except DeliveryUncertain as error:
                            row = await client.store.operation(client.account, error.operation_id)
                            raise AssertionError(f"Synthetic operation uncertain: {row['error']}") from error
                        assert message.read is None
                        if client.session.user_id == uids[0] and number == 0:
                            assert message.history_verified and not message.rpc_confirmed
                        else:
                            assert message.rpc_confirmed and not message.history_verified
                        duplicate = await client.send_message(
                            peer, f"round-{number}", idempotency_key=f"round-{number}"
                        )
                        assert duplicate.rid == message.rid
                        await client.edit_message(message, f"edited-{number}")
                        await client.delete_message(message)
                    peer = Peer(PeerKind.CHANNEL, 101)
                    album_loses_ack = client.session.user_id % 2 == 0
                    if album_loses_ack:
                        server.lost_ack.add(client.session.user_id)
                    album = await client.send_album(
                        peer, [Media(image, MediaKind.PHOTO, str(n)) for n in range(2)]
                    )
                    assert all(
                        item.history_verified and item.rpc_confirmed != album_loses_ack
                        for item in album.messages
                    )
                    assert all(
                        item.ref.date == server.messages[client.session.user_id, peer.id][item.rid].date
                        for item in album.messages
                    )
                    for message in album.messages:
                        target = await client.download(
                            message,
                            root / f"{client.session.user_id}-{message.rid}.png",
                            expected_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),
                        )
                        assert target.read_bytes() == image.read_bytes()
                    return album.grouped_id

                albums = await asyncio.gather(*(exercise(client) for client in pool.clients.values()))
                await asyncio.gather(*(client.recover() for client in pool.clients.values()))
                await snapshot("after_mixed_work_and_diff")
                # Generate identical offline RIDs for distinct accounts. Namespace
                # isolation must preserve both and recover edit/delete on all routes.
                await asyncio.gather(*(client.disconnect() for client in pool.clients.values()))
                for uid in uids:
                    for peer_id in (101, 102):
                        rid = 2**60 + peer_id
                        request = contract("SendMessage").request(rid=rid)
                        request.peer.type, request.peer.id = 2, peer_id
                        request.message.textMessage.text = "offline"
                        await server.rpc(uid, "SendMessage", request.SerializeToString())
                        edit = contract("UpdateMessage").request(rid=rid)
                        edit.peer.CopyFrom(request.peer)
                        edit.updatedMessage.textMessage.text = "offline-edit"
                        await server.rpc(uid, "UpdateMessage", edit.SerializeToString())
                        delete = contract("DeleteMessage").request(rids=[rid])
                        delete.peer.CopyFrom(request.peer)
                        delete.dates.dates.append(server.messages[uid, peer_id][rid].date)
                        await server.rpc(uid, "DeleteMessage", delete.SerializeToString())
                    await server.publish(uid, 0, s.WebUpdate.FromString(b"\xfa\x3e\x02qa"))
            finally:
                await pool.close()
                active_pool = None
                observer.cancel()
                await asyncio.gather(observer, return_exceptions=True)
                if server.errors:
                    raise AssertionError(server.errors[0])
            pool = await make_pool()
            observer = asyncio.create_task(observe())
            try:
                await snapshot("restart_connected")
                drain_timeout = max(30, accounts * rounds * 0.05)
                previous, last_progress, last_print = None, time.monotonic(), time.monotonic()
                async with asyncio.timeout(drain_timeout):
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
                        audit.update(
                            drain_last_pending=pending,
                            drain_quarantine=quarantine,
                            drain_timeout_seconds=drain_timeout,
                        )
                        assert quarantine == 0, "Model handler failure quarantined an event"
                        if not pending:
                            break
                        now = time.monotonic()
                        if previous is None or pending < previous:
                            last_progress = now
                        previous = pending
                        if now - last_progress > max(30, drain_timeout / 4):
                            raise AssertionError("Inbox drain stopped making progress")
                        if observe_memory and now - last_print >= 15:
                            print(
                                json.dumps(
                                    {"stage": "draining", "pending": pending, "quarantine": quarantine}
                                ),
                                flush=True,
                            )
                            last_print = now
                        await asyncio.sleep(0.02)
                for client, grouped in zip(pool.clients.values(), albums, strict=True):
                    assert len((await client.get_album(Peer(PeerKind.CHANNEL, 101), grouped)).messages) == 2
                    routes = await pool.store.routes(client.account)
                    for row in routes:
                        peer_id = 0 if row["route"] == "global" else int(row["route"])
                        assert row["seq"] == len(server.logs[client.session.user_id, peer_id])
                    assert (await client.fsm.get("received")) > rounds * 3
                    evidence = await pool.store.run(
                        lambda db, account=client.account: [
                            (row[0], s.WebUpdate.FromString(row[1]))
                            for row in db.execute("SELECT kind,raw FROM inbox WHERE account=?", (account,))
                        ],
                        write=False,
                    )
                    for peer_id in (101, 102):
                        rid = 2**60 + peer_id
                        recovered = {
                            kind
                            for kind, update in evidence
                            if (kind == "new" and update.message.rid == rid)
                            or (kind == "edit" and update.messageContentChanged.rid == rid)
                            or (kind == "delete" and rid in update.messageDelete.rids)
                        }
                        assert recovered == {"new", "edit", "delete"}
                    assert any(kind == "unknown" for kind, _ in evidence)
                totals = await pool.store.run(
                    lambda db: {
                        "operations": db.execute("SELECT count(*) FROM operations").fetchone()[0],
                        "confirmed": db.execute(
                            "SELECT count(*) FROM operations WHERE status='confirmed'"
                        ).fetchone()[0],
                        "inbox": db.execute("SELECT count(*) FROM inbox").fetchone()[0],
                        "acked": db.execute("SELECT count(*) FROM inbox WHERE status='acked'").fetchone()[0],
                        "accounts": db.execute("SELECT count(DISTINCT account) FROM inbox").fetchone()[0],
                    },
                    write=False,
                )
                assert totals["operations"] == totals["confirmed"] == accounts * (rounds * 3 + 1)
                assert totals["accounts"] == accounts and totals["inbox"] == totals["acked"]
                assert server.peak <= config.global_rpc_limit
                assert server.calls[uids[0], "SendMessage"] == rounds + 2
                assert server.calls[uids[1], "SendMessage"] == rounds + 3
                assert all(server.calls[uid, "SendMultiMediaMessage"] == 1 for uid in uids)
                assert all(client._ws.pending_count == 0 for client in pool.clients.values())
                await snapshot("restarted_and_drained")
            finally:
                await pool.close()
                active_pool = None
                observer.cancel()
                await asyncio.gather(observer, return_exceptions=True)
            await snapshot("closed_pool_still_in_scope")
            assert peaks["raw_per_account"] <= config.queue_size
            assert peaks["leased_per_account"] <= config.queue_size
            assert peaks["store_queue"] <= config.queue_size
    return {
        "pass": True,
        "version": __version__,
        "seconds": time.monotonic() - started,
        **totals,
        "max_parallel_rpc": server.peak,
        "rpc_limit": config.global_rpc_limit,
        "lost_ack_reconciled": True,
        "rate_rejection_retried": True,
        "offline_new_edit_delete_all_routes": True,
        "same_rid_account_isolation": True,
        "albums_and_download_hashes": True,
        "distinct_album_item_reference_dates": True,
        "pending_leaks": 0,
        "queue_and_task_peaks": peaks,
        "memory_samples": snapshots,
        "memory_limitations": "Filtered tracemalloc Python allocations attributed to SDK sources; excludes model/driver and native allocations, not RSS. Closed pool remains in scope at last sample.",
        "limitations": "Synthetic WS request adapter and HTTP mock with real typed protocol/store/media; no real-account throughput claim.",
    }


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--accounts", type=int, default=20)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--memory", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("docs/qa/multiaccount-013.json"))
    args = parser.parse_args()
    if args.accounts < 2 or args.rounds < 1:
        parser.error("accounts must be at least two and rounds positive")
    if args.memory:
        tracemalloc.start()
    audit = {}
    try:
        result = await scenario(args.accounts, args.rounds, observe_memory=args.memory, audit=audit)
        if args.memory:
            result["total_python_trace_peak_bytes"] = tracemalloc.get_traced_memory()[1]
    except Exception as exc:
        failure = {
            "pass": False,
            "version": __version__,
            "accounts": args.accounts,
            "rounds": args.rounds,
            "error": type(exc).__name__,
            **audit,
        }
        args.output.with_suffix(".failed.json").write_text(
            json.dumps(failure, indent=2) + "\n", encoding="utf-8"
        )
        raise
    finally:
        if args.memory:
            tracemalloc.stop()
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
