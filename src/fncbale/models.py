from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any
from typing import BinaryIO
from collections.abc import AsyncIterable, Awaitable, Callable

if TYPE_CHECKING:
    from .client import Client
    from .proto.struct_pb2 import WebMember


class PeerKind(StrEnum):
    USER = "user"
    GROUP = "group"
    CHANNEL = "channel"


@dataclass(frozen=True, slots=True)
class Peer:
    kind: PeerKind
    id: int
    access_hash: int = 0
    username: str | None = None
    title: str | None = None

    def __post_init__(self):
        object.__setattr__(self, "kind", PeerKind(self.kind))
        if not -(1 << 63) <= self.id < (1 << 63):
            raise ValueError("Peer id must fit int64")

    @property
    def wire_type(self) -> int:
        return 1 if self.kind == PeerKind.USER else 2

    @property
    def out_type(self) -> int:
        return {PeerKind.USER: 1, PeerKind.GROUP: 2, PeerKind.CHANNEL: 3}[self.kind]

    @property
    def key(self) -> str:
        return f"{self.wire_type}:{self.id}"


@dataclass(frozen=True, slots=True)
class MessageRef:
    peer: Peer
    rid: int
    date: int
    seq: int = 0


class MediaKind(StrEnum):
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    DOCUMENT = "document"


MediaSource = str | Path | bytes | BinaryIO | AsyncIterable[bytes]
ProgressCallback = Callable[[int, int], None | Awaitable[None]]
DownloadProgressCallback = Callable[[int, int, int], None | Awaitable[None]]


@dataclass(frozen=True, slots=True)
class Media:
    source: MediaSource = field(repr=False)
    kind: MediaKind = MediaKind.DOCUMENT
    caption: str = ""
    filename: str | None = None
    mime_type: str | None = None

    def __post_init__(self):
        object.__setattr__(self, "kind", MediaKind(self.kind))


@dataclass(frozen=True, slots=True)
class MediaInfo:
    kind: MediaKind
    file_id: int
    access_hash: int
    size: int
    filename: str
    mime_type: str
    width: int = 0
    height: int = 0
    duration_seconds: float = 0


@dataclass(slots=True)
class Message:
    ref: MessageRef
    text: str = ""
    media: MediaInfo | None = None
    grouped_id: int | None = None
    sender_id: int = 0
    rpc_confirmed: bool = False
    history_verified: bool = False
    read: bool | None = None
    operation_id: str | None = None
    quoted: Any = field(default=None, repr=False)
    raw: bytes = field(default=b"", repr=False)
    author_signature: str | None = None

    @property
    def rid(self) -> int:
        return self.ref.rid


@dataclass(slots=True)
class Album:
    messages: tuple[Message, ...]
    grouped_id: int
    operation_id: str | None = None


@dataclass(frozen=True, slots=True)
class DownloadResult:
    index: int
    destination: Path
    completed: bool
    error_type: str | None = None


@dataclass(frozen=True, slots=True)
class MemberPage:
    peer: Peer
    members: tuple[WebMember, ...]
    cursor: bytes = field(repr=False)
    next_cursor: bytes = field(repr=False)
    raw: bytes = field(repr=False)

    @property
    def complete(self) -> bool:
        return not self.next_cursor


@dataclass(frozen=True, slots=True)
class MessageViews:
    ref: MessageRef
    count: int | None
    raw: bytes = field(default=b"", repr=False)

    @property
    def available(self) -> bool:
        return self.count is not None


class OperationStatus(StrEnum):
    QUEUED = "queued"
    WAITING = "waiting"
    RUNNING = "running"
    CONFIRMED = "confirmed"
    UNCERTAIN = "uncertain"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class Operation:
    operation_id: str
    status: OperationStatus
    method: str
    attempts: int
    error: str | None
    retry_at: float | None = None
    cycle_attempts: int = 0
    rpc_confirmed: bool = False
    history_verified: bool = False


class OperationHandle:
    def __init__(self, client: Client, operation_id: str, *, account: str | None = None):
        self.client, self.operation_id = client, operation_id
        self._account = client.account if account is None else account

    def _ensure_account(self):
        self.client._ensure_operation_account(self._account)

    async def status(self) -> Operation:
        self._ensure_account()
        return await self.client.get_operation(self.operation_id)

    async def wait(self):
        self._ensure_account()
        return await self.client.wait_operation(self.operation_id)

    async def cancel(self) -> bool:
        self._ensure_account()
        return await self.client.cancel_operation(self.operation_id)


PeerInput = Peer | Message | MessageRef | str | int
