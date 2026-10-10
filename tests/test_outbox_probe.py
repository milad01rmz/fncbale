import asyncio
import time
from types import SimpleNamespace

from fncbale.storage import Store
from fncbale import Client, Config, Peer, PeerKind, Session, contract


async def traced_store(tmp_path):
    store = Store(tmp_path / "state.sqlite3", commit_window=0.03)
    statements = []
    await store.run(lambda db: db.set_trace_callback(statements.append), write=False)
    return store, statements


def reads(statements):
    return sum(sql.startswith("SELECT o.* FROM operations") for sql in statements)


async def test_empty_outbox_workers_share_transaction_snapshot_without_duplicate_reads(tmp_path):
    store, statements = await traced_store(tmp_path)
    try:
        result = await asyncio.gather(*(store.claim("a") for _ in range(8)))
        assert result == [None] * 8
        assert reads(statements) == 1, "Eight empty workers repeated the same SQLite selection"
    finally:
        await store.close()


async def test_enqueue_in_same_batch_invalidates_empty_snapshot(tmp_path):
    store, statements = await traced_store(tmp_path)
    try:
        first, operation_id, claimed = await asyncio.gather(
            store.claim("a"),
            store.enqueue("a", "p", "SendMessage", b"frozen", "{}"),
            store.claim("a"),
        )
        assert first is None and claimed["id"] == operation_id
        assert reads(statements) == 2
        assert (await store.operation("a", operation_id))["status"] == "running"
    finally:
        await store.close()


async def test_claims_are_unique_and_uncertain_peer_does_not_block_other_account_or_peer(tmp_path):
    store, statements = await traced_store(tmp_path)
    try:
        one = await store.enqueue("a", "p", "SendMessage", b"first", "{}")
        two = await store.enqueue("a", "p", "SendMessage", b"second", "{}")
        other = await store.enqueue("a", "q", "SendMessage", b"other", "{}")
        remote = await store.enqueue("b", "p", "SendMessage", b"foreign", "{}")
        result = await asyncio.gather(*(store.claim("a") for _ in range(8)))
        ids = [row["id"] for row in result if row]
        assert ids == [one, other] and len(set(ids)) == 2
        await store.finish("a", one, "uncertain")
        assert await store.claim("a") is None
        assert (await store.claim("b"))["id"] == remote
        await store.finish("a", one, "confirmed", response=b"ack")
        assert (await store.claim("a"))["id"] == two
    finally:
        await store.close()


async def test_empty_hint_does_not_survive_next_transaction(tmp_path):
    store, statements = await traced_store(tmp_path)
    try:
        assert await store.claim("a") is None
        assert await store.claim("a") is None
        assert reads(statements) == 2
    finally:
        await store.close()


async def test_time_gate_expiry_between_probes_is_not_hidden_by_empty_hint(tmp_path, monkeypatch):
    store, statements = await traced_store(tmp_path)
    try:
        operation_id = await store.enqueue("a", "p", "SendMessage", b"frozen", "{}")
        assert (await store.claim("a"))["id"] == operation_id
        await store.reschedule("a", operation_id, delay=10)
        base, calls = time.time(), 0

        def now():
            nonlocal calls
            calls += 1
            return base if calls <= 2 else base + 20

        monkeypatch.setattr("fncbale.storage.time", SimpleNamespace(time=now, monotonic=time.monotonic))
        first, second = await asyncio.gather(store.claim("a"), store.claim("a"))
        assert first is None and second is not None and second["id"] == operation_id
    finally:
        await store.close()


async def test_enqueue_between_empty_claim_and_wait_does_not_lose_wake(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path, config=Config(outbox_workers=1))
    client.account, client._active = "a", True
    original = client.store.claim
    first = True
    transmitted = asyncio.Event()

    async def claim(account):
        nonlocal first
        row = await original(account)
        if first:
            first = False
            assert row is None
            await client.enqueue_message(Peer(PeerKind.USER, 10), "frozen", idempotency_key="race")
        return row

    async def send(method, payload, route):
        transmitted.set()
        return contract(method).response(date=42).SerializeToString()

    client.store.claim, client._call_bytes = claim, send
    task = asyncio.create_task(client._outbox_worker())
    client._tasks.append(task)
    try:
        await asyncio.wait_for(transmitted.wait(), 0.2)
    finally:
        await client.close()
