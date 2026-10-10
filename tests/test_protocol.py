from pathlib import Path

import pytest
from google.protobuf.unknown_fields import UnknownFieldSet

from fncbale.events import normalize
from fncbale.errors import ProtocolError, RpcError
from fncbale.protocol import grpc_decode, grpc_frame
from fncbale.proto import response_pb2 as r, struct_pb2 as s

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_grpc_string_zero_trailer_and_truncation():
    trailer = b"grpc-status: 0\r\n"
    body = grpc_frame(b"hello") + b"\x80" + len(trailer).to_bytes(4, "big") + trailer
    assert grpc_decode(body, {"grpc-status": "0"}, "test") == b"hello"
    with pytest.raises(ProtocolError):
        grpc_decode(body[:-1], {}, "test")
    with pytest.raises(RpcError):
        grpc_decode(grpc_frame(b""), {"grpc-status": "7"}, "test")


def test_all_event_fields_and_large_rid_unknown_preserved():
    update = s.WebUpdate()
    update.message.peer.type, update.message.peer.id = 1, 9
    update.message.rid, update.message.date = (1 << 53) + 321, 1720000000000
    update.message.message.textMessage.text = "سلام ✅"
    update.messageDelete.peer.type, update.messageDelete.peer.id = 1, 9
    update.messageDelete.rids.extend([8, 7])
    raw = update.SerializeToString() + b"\xfa\x3e\x02hi"  # field 1007, unknown
    decoded = s.WebUpdate.FromString(raw)
    events = normalize(decoded)
    assert {e.kind for e in events} == {"new", "delete", "unknown"}
    assert next(e.message.rid for e in events if e.kind == "new") == (1 << 53) + 321
    assert next(e.message.quoted for e in events if e.kind == "new") is None
    assert list(UnknownFieldSet(s.WebUpdate.FromString(decoded.SerializeToString())))


def test_media_decode_order_is_independent():
    from fncbale.events import message_from_history
    from fncbale.models import Peer, PeerKind

    peer = Peer(PeerKind.USER, 9)
    for order in [
        ("documentExVoice", "documentExAudio", "documentExVideo"),
        ("documentExVideo", "documentExAudio", "documentExVoice"),
    ]:
        result = []
        for name in order:
            history = s.WebHistory(rid=3, date=4)
            history.message.documentMessage.fileId = 5
            getattr(history.message.documentMessage.ext, name).duration = (
                1 if name.endswith("Video") else 1000
            )
            result.append(message_from_history(peer, history).media)
        assert all(item.file_id == 5 and item.duration_seconds == 1 for item in result)


def test_empty_wrapper_presence():
    value = s.WebUpdate()
    value.messageReadByMe.unreadCounter.SetInParent()
    decoded = s.WebUpdate.FromString(value.SerializeToString())
    assert decoded.messageReadByMe.HasField("unreadCounter")
    assert normalize(decoded)[0].kind == "read_by_me"


def test_research_fixtures_decode():
    # These are sanitized wire evidence, never account traffic or credentials.
    actual = list(FIXTURES.glob("*.bin"))
    updates = {
        "new-message.bin",
        "message-sent.bin",
        "delete-packed-two.bin",
        "edit-update-1.bin",
        "edit-update-2.bin",
        "read-by-me-empty-wrapper.bin",
        "unknown-update.bin",
    }
    checked = 0
    for path in actual:
        if path.name in updates:
            value = r.Response.FromString(path.read_bytes())
            assert value.HasField("ws_update")
            assert normalize(value.ws_update.update.composed_update)
            checked += 1
    assert checked == len(updates)


def test_rate_hints_http_date_and_grpc_trailer():
    from fncbale.protocol import retry_delay

    assert retry_delay("Thu, 08 Oct 2026 17:00:30 GMT", now=1791478800) == 30
    assert retry_delay("-1") == 0
    assert retry_delay("NaN") is None
    assert retry_delay(None, reason="FLOOD_WAIT_17") == 17
    trailer = b"grpc-status: 8\r\ngrpc-message: retry_after%3D2.5\r\n"
    with pytest.raises(RpcError) as error:
        grpc_decode(b"\x80" + len(trailer).to_bytes(4, "big") + trailer, {}, "send")
    assert error.value.retry_after == 2.5
    trailer = b"grpc-status: \xff\r\n"
    with pytest.raises(ProtocolError):
        grpc_decode(b"\x80" + len(trailer).to_bytes(4, "big") + trailer, {}, "send")


def test_current_search_imported_container_and_signature_golden_wire():
    # Hand-encoded facts from the cached web codec, without calling the new field setters:
    # SearchResult.result(1) -> result.messageContainer(6) -> history.rid(2),
    # history.date(3), history.authorSign(19), and unknown history field 1007.
    history = b"\x10\x7b\x18\x64\x9a\x01\x00\xfa\x3e\x02hi"
    inner = b"\x32" + bytes([len(history)]) + history
    raw = b"\x0a" + bytes([len(inner)]) + inner
    result = s.WebSearchResult.FromString(raw)
    assert result.result.HasField("messageContainer")
    item = result.result.messageContainer
    assert (item.rid, item.date) == (123, 100)
    assert item.HasField("authorSign") and item.authorSign.value == ""
    assert list(UnknownFieldSet(item)) and s.WebSearchResult.FromString(result.SerializeToString()) == result
