"""Typed protobuf helpers and strict gRPC-web framing."""

from __future__ import annotations

import struct
import math
import re
import time
from datetime import timezone
from email.utils import parsedate_to_datetime
from urllib.parse import unquote

from .errors import ProtocolError, RpcError


def grpc_frame(payload: bytes) -> bytes:
    return struct.pack(">BI", 0, len(payload)) + payload


def retry_delay(value, *, reason="", now=None):
    """Read HTTP Retry-After or explicit FLOOD_WAIT/retry_after hints; seconds."""
    if value is not None:
        try:
            delay = float(value)
            if math.isfinite(delay):
                return max(0.0, delay)
        except (TypeError, ValueError):
            try:
                date = parsedate_to_datetime(str(value))
                if date.tzinfo is None:
                    date = date.replace(tzinfo=timezone.utc)
                return max(0.0, date.timestamp() - (time.time() if now is None else now))
            except (TypeError, ValueError, OverflowError):
                pass
    match = re.search(r"(?:FLOOD_WAIT[_ :]+|retry_after[=: ]+)(\d+(?:\.\d+)?)", reason, re.I)
    return float(match[1]) if match else None


def grpc_decode(body: bytes, headers, method: str, limit: int = 32 * 1024 * 1024) -> bytes:
    status = headers.get("grpc-status")
    reason = headers.get("grpc-message", "")
    retry_after = headers.get("retry-after")
    data, pos = [], 0
    while pos < len(body):
        if len(body) - pos < 5:
            raise ProtocolError("Truncated gRPC-web frame header")
        flags, size = struct.unpack_from(">BI", body, pos)
        pos += 5
        if size > limit or size > len(body) - pos:
            raise ProtocolError("Invalid gRPC-web frame length")
        part = body[pos : pos + size]
        pos += size
        if flags == 128:
            try:
                lines = part.decode("ascii", errors="strict").splitlines()
            except UnicodeDecodeError as exc:
                raise ProtocolError("Non-ASCII gRPC-web trailer") from exc
            for line in lines:
                key, sep, value = line.partition(":")
                if sep:
                    key, value = key.lower().strip(), value.strip()
                    if key == "grpc-status":
                        status = value
                    elif key == "grpc-message":
                        reason = value
                    elif key == "retry-after":
                        retry_after = value
        elif flags == 0:
            data.append(part)
        else:
            raise ProtocolError("Unsupported compressed gRPC-web frame")
    if status is not None:
        try:
            code = int(unquote(str(status)))
        except ValueError as exc:
            raise ProtocolError("Invalid grpc-status") from exc
        if code:
            reason = unquote(reason)
            raise RpcError(code, method, retry_after=retry_delay(retry_after, reason=reason), reason=reason)
    if len(data) != 1:
        raise ProtocolError("Unary RPC requires exactly one data frame")
    return data[0]


def parse(cls, payload: bytes):
    try:
        return cls.FromString(payload)
    except Exception as exc:
        raise ProtocolError(f"Invalid {cls.__name__} protobuf") from exc


def wire_peer(peer):
    from .proto.struct_pb2 import WebOutPeer

    return WebOutPeer(type=peer.out_type, id=peer.id, accessHash=peer.access_hash)


def short_peer(peer):
    from .proto.struct_pb2 import WebPeer

    return WebPeer(type=peer.wire_type, id=peer.id, accessHash=peer.access_hash)
