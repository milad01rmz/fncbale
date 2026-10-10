import pytest

from fncbale import Client, HistoryPaginationGap, Peer, PeerKind, Session
from fncbale.contracts import contract


def history_model(client, dates):
    rows = [
        contract("LoadHistory").response().history.add(rid=i + 1, date=date) for i, date in enumerate(dates)
    ]
    calls = []

    async def rpc(method, request, **kwargs):
        assert method == "LoadHistory" and request.loadMode == 2
        calls.append((request.date, request.limit))
        result = contract(method).response()
        page = sorted(
            (r for r in rows if request.date == -1 or r.date <= request.date),
            key=lambda r: r.date,
            reverse=True,
        )[: request.limit]
        for row in page:
            result.history.add().CopyFrom(row)
        return result

    client._rpc = rpc
    return calls


@pytest.mark.parametrize("size", [1, 2, 3, 10, 100])
async def test_equal_timestamp_boundaries_never_skip_messages(tmp_path, size):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    dates = [10] * 7 + [9] * 4 + [8] * 5 + [6] * 3
    calls = history_model(client, dates)
    try:
        result = [m async for m in client.iter_history(Peer(PeerKind.USER, 2), page_size=size)]
        assert [m.rid for m in result] == list(range(1, len(dates) + 1))
        assert all(m.history_verified and not m.rpc_confirmed for m in result)
        assert len(calls) <= len(dates) + 3 and max(n for _, n in calls) <= 100
    finally:
        await client.close()


async def test_saturated_timestamp_reports_gap_instead_of_skipping(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    history_model(client, [10] * 101 + [9])
    result = []
    peer = Peer(PeerKind.USER, 2)
    try:
        with pytest.raises(HistoryPaginationGap) as caught:
            async for message in client.iter_history(peer, page_size=3):
                result.append(message)
        assert len(result) == 100 and len({m.rid for m in result}) == 100
        assert caught.value.peer == peer and caught.value.date == 10
        # A bounded caller receives exactly the requested prefix, without claiming completeness.
        assert len([m async for m in client.iter_history(peer, limit=100)]) == 100
    finally:
        await client.close()


async def test_history_limits_anchor_and_long_stream(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    dates = list(range(2000, 0, -1))
    calls = history_model(client, dates)
    peer = Peer(PeerKind.USER, 2)
    try:
        assert not [m async for m in client.iter_history(peer, limit=0)] and not calls
        with pytest.raises(ValueError):
            await anext(client.iter_history(peer, limit=-1))
        result = [m async for m in client.iter_history(peer, limit=11, before=1000, page_size=3)]
        assert [m.ref.date for m in result] == list(range(1000, 989, -1))
        count = 0
        iterator = client.iter_history(peer, page_size=3)
        async for _message in iterator:
            count += 1
            # Only the current timestamp bucket/page is retained, regardless of stream length.
            assert len(iterator.ag_frame.f_locals["boundary_rids"]) <= 3
            assert len(iterator.ag_frame.f_locals["page_rids"]) <= 3
        assert count == 2000
    finally:
        await client.close()
