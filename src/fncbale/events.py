from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from typing import Any

from google.protobuf.unknown_fields import UnknownFieldSet

from .models import MediaInfo, MediaKind, Message, MessageRef, Peer, PeerKind
from .proto import struct_pb2 as s


def peer_from_wire(value):
    return Peer(
        PeerKind.USER if value.type == 1 else PeerKind.GROUP, value.id, getattr(value, "accessHash", 0)
    )


def message_content(peer, rid, date, content, *, grouped_id=None, sender_id=0, raw=b"", quoted=None):
    text = content.textMessage.text if content.HasField("textMessage") else ""
    media = None
    if content.HasField("documentMessage"):
        doc = content.documentMessage
        text = doc.caption.text
        ext, kind, width, height, duration = doc.ext, MediaKind.DOCUMENT, 0, 0, 0
        for name, target in (
            ("documentExPhoto", MediaKind.PHOTO),
            ("documentExVideo", MediaKind.VIDEO),
            ("documentExVoice", MediaKind.VOICE),
            ("documentExAudio", MediaKind.AUDIO),
            ("documentExGif", MediaKind.VIDEO),
        ):
            if ext.HasField(name):
                value = getattr(ext, name)
                kind, width, height = target, getattr(value, "w", 0), getattr(value, "h", 0)
                duration = getattr(value, "duration", 0) / (
                    1000 if target in (MediaKind.VOICE, MediaKind.AUDIO) else 1
                )
                break
        media = MediaInfo(
            kind, doc.fileId, doc.accessHash, doc.fileSize, doc.name, doc.mimeType, width, height, duration
        )
    return Message(
        MessageRef(peer, rid, date),
        text,
        media,
        grouped_id or None,
        sender_id,
        quoted=quoted,
        raw=raw or content.SerializeToString(),
    )


def message_from_history(peer, value):
    message = message_content(
        peer,
        value.rid,
        value.date,
        value.message,
        grouped_id=value.groupedId.value,
        sender_id=value.senderUid,
        raw=value.SerializeToString(),
        quoted=value.quotedMessage if value.HasField("quotedMessage") else None,
    )
    message.ref = MessageRef(peer, value.rid, value.date, value.seq.value)
    message.author_signature = value.authorSign.value if value.HasField("authorSign") else None
    return message


@dataclass(slots=True)
class Event:
    event_id: str
    kind: str
    peer: Peer | None
    raw: bytes = field(repr=False)
    message: Message | None = None
    rids: tuple[int, ...] = ()
    data: Any = field(default=None, repr=False)
    _ack: Any = field(default=None, repr=False)
    _handler_failures: int = field(default=0, repr=False)

    async def ack(self):
        if self._ack:
            await self._ack(self.event_id)

    @property
    def handler_failures(self) -> int:
        """Failures committed before this delivery or failed-event snapshot."""
        return self._handler_failures


@dataclass(slots=True)
class UnknownEvent(Event):
    pass


@dataclass(slots=True)
class GapEvent(Event):
    pass


KINDS = {
    "message": "new",
    "messageSent": "sent",
    "messageContentChanged": "edit",
    "messageDelete": "delete",
    "messageRead": "read",
    "messageReadByMe": "read_by_me",
    "messageReceived": "received",
}


def normalize(update, event_id="", ack=None):
    result = []
    for descriptor, value in update.ListFields():
        if descriptor.name == "messages":
            # Album/channel updates arrive as bulk history containers as well as
            # individual field-55 updates. The server history order is newest first.
            parent = s.WebMessages()
            parent.CopyFrom(value)
            parent.ClearField("messageContainers")
            for history in reversed(value.messageContainers):
                single = s.WebUpdate()
                single.messages.CopyFrom(parent)
                single.messages.messageContainers.add().CopyFrom(history)
                peer = peer_from_wire(value.peer)
                message = message_from_history(peer, history)
                result.append(
                    Event(
                        event_id,
                        "new",
                        peer,
                        single.SerializeToString(deterministic=True),
                        message=message,
                        data=single.messages.messageContainers[0],
                        _ack=ack,
                    )
                )
            continue
        single = s.WebUpdate()
        if descriptor.is_repeated:
            getattr(single, descriptor.name).extend(value)
        else:
            getattr(single, descriptor.name).CopyFrom(value)
        raw = single.SerializeToString(deterministic=True)
        kind = KINDS.get(descriptor.name, "unknown." + descriptor.name)
        peer = peer_from_wire(value.peer) if hasattr(value, "peer") and value.HasField("peer") else None
        message = None
        rids = ()
        if kind == "new":
            message = message_content(
                peer,
                value.rid,
                value.date,
                value.message,
                grouped_id=value.groupedId.value,
                sender_id=value.senderUid,
                raw=raw,
                quoted=value.quotedMessage if value.HasField("quotedMessage") else None,
            )
        elif kind == "edit":
            content = (
                value.updatedContentTypeMessage
                if value.HasField("updatedContentTypeMessage")
                else value.message
            )
            message = message_content(peer, value.rid, value.date.value, content, raw=raw)
        elif kind == "delete":
            rids = tuple(value.rids)
        elif kind == "sent":
            message = Message(MessageRef(peer, value.rid, value.date), rpc_confirmed=True, raw=raw)
        cls = UnknownEvent if kind.startswith("unknown") else Event
        result.append(cls(event_id, kind, peer, raw, message, rids, value, ack))
    if list(UnknownFieldSet(update)):
        result.append(UnknownEvent(event_id, "unknown", None, update.SerializeToString(), _ack=ack))
    return result


def journal_events(update):
    records = []
    for event in normalize(update):
        key = event.peer.key if event.peer else "unknown"
        dedupe = None
        # No edit dedupe based solely on text or frame bytes: two identical edits
        # can be separate user actions without a revision identifier.
        if event.kind in ("new", "sent"):
            identity = f"{key}:{event.kind}:{event.message.rid}:{event.message.ref.date}"
            dedupe = hashlib.sha256(identity.encode()).hexdigest()
        records.append((key, event.kind, event.raw, dedupe))
    return records
