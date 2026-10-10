import pytest

from google.protobuf.unknown_fields import UnknownFieldSet
from fncbale import Client, Peer, PeerKind, Session, contract
from fncbale.errors import ProtocolError, SearchSnapshotUnavailable
from fncbale.proto import struct_pb2 as s


async def test_full_search_container_preserves_media_album_quote_presence_and_unknown(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    peer = Peer(PeerKind.CHANNEL, 10, 99)
    result = s.WebSearchResult()
    value = result.result
    value.peer.type, value.peer.id = 2, 10
    value.rid, value.date = 2**60 + 3, 1720000000010
    item = value.messageContainer
    item.rid, item.date, item.senderUid = value.rid, value.date, 7
    item.seq.value, item.groupedId.value = 2**55 + 1, 2**59 + 2
    item.authorSign.SetInParent()  # Present empty signature differs from absent.
    item.quotedMessage.messageId.value = 2**60 + 2
    doc = item.message.documentMessage
    doc.fileId, doc.accessHash, doc.fileSize = 88, 99, 128
    doc.caption.text = "سلام 🧪"
    doc.ext.documentExVideo.duration = 2
    item.ParseFromString(item.SerializeToString() + b"\xfa\x3e\x02hi")
    # Even a conflicting flattened summary must not override the full snapshot.
    value.content.textMessage.text = "summary"

    async def rpc(method, request, **kwargs):
        response = contract(method).response()
        assert method == "SearchMessages"
        response.searchResults.add().CopyFrom(result)
        return response

    client._rpc = rpc
    try:
        messages = [m async for m in client.iter_search_messages(peer, "text")]
        assert len(messages) == 1
        message = messages[0]
        assert message.rid == value.rid and message.ref.seq == item.seq.value
        assert message.media.file_id == 88 and message.text == "سلام 🧪"
        assert message.grouped_id == item.groupedId.value
        assert message.quoted.messageId.value == 2**60 + 2 and message.author_signature == ""
        assert message.history_verified and not message.rpc_confirmed and message.read is None
        decoded = s.WebHistory.FromString(message.raw)
        assert list(UnknownFieldSet(decoded)) and decoded.HasField("authorSign")
    finally:
        await client.close()


@pytest.mark.parametrize("fault", ["peer", "identity", "no_content", "fallback"])
async def test_search_snapshot_validation_and_flattened_fallback(tmp_path, fault):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    result = s.WebSearchResult()
    value = result.result
    value.peer.type, value.peer.id, value.rid, value.date = 2, 10, 77, 100
    if fault == "peer":
        value.peer.id = 20
        value.content.textMessage.text = "wrong target"
    elif fault == "identity":
        value.messageContainer.rid, value.messageContainer.date = 78, 100
    elif fault == "fallback":
        value.content.textMessage.text = "flat"

    async def rpc(method, request, **kwargs):
        response = contract(method).response()
        if method == "LoadHistory":
            if fault == "fallback":
                history = response.history.add(rid=77, date=100, senderUid=7)
                history.message.documentMessage.fileId = 88
                history.message.documentMessage.caption.text = "full caption"
        else:
            response.searchResults.add().CopyFrom(result)
        return response

    client._rpc = rpc
    try:
        iterator = client.iter_search_messages(Peer(PeerKind.CHANNEL, 10), "text")
        if fault == "fallback":
            message = await anext(iterator)
            assert message.text == "full caption" and message.media.file_id == 88
            assert message.author_signature is None and message.history_verified
            await iterator.aclose()
        else:
            with pytest.raises(SearchSnapshotUnavailable if fault == "no_content" else ProtocolError):
                await anext(iterator)
    finally:
        await client.close()


async def test_projection_hydration_window_is_shared_and_bounded(tmp_path):
    client = Client(Session(1, "synthetic"), data_dir=tmp_path)
    calls = []

    async def rpc(method, request, **kwargs):
        calls.append(method)
        response = contract(method).response()
        if method == "LoadHistory":
            for rid in (3, 2, 1):
                item = response.history.add(rid=rid, date=100)
                item.message.documentMessage.fileId = rid + 10
        else:
            for rid in (1, 2, 3):
                result = response.searchResults.add().result
                result.peer.type, result.peer.id, result.rid, result.date = 2, 10, rid, 100
                result.content.textMessage.text = "indexed caption"
        return response

    client._rpc = rpc
    try:
        iterator = client.iter_search_messages(Peer(PeerKind.CHANNEL, 10), "text")
        results = []
        async for message in iterator:
            results.append(message)
            assert len(iterator.ag_frame.f_locals["history_window"]) <= 100
        assert [m.media.file_id for m in results] == [11, 12, 13]
        assert calls == ["SearchMessages", "LoadHistory"]
    finally:
        await client.close()
