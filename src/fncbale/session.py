from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import tempfile

from .errors import AuthenticationError, SessionInUse
from .protocol import grpc_decode, parse
from .proto.response_pb2 import Auth
from .media import disk_call


@dataclass(frozen=True, slots=True)
class Session:
    user_id: int
    token: str = field(repr=False)

    @classmethod
    def import_aiobale(cls, path: str | Path):
        """Read a native .bale auth response without importing AioBale."""
        raw = Path(path).read_bytes()
        if raw[:1] == b"\x00":
            raw = grpc_decode(raw, {}, "import-session")
        value = parse(Auth, raw)
        if not value.jwt.value or not value.user.id:
            raise AuthenticationError("Session has no user and JWT")
        return cls(value.user.id, value.jwt.value)


@dataclass(frozen=True, slots=True)
class LoginChallenge:
    """In-memory, client-bound challenge; never serialize it to application logs."""

    transaction_hash: str = field(repr=False)
    is_registered: bool
    sent_code_type: int
    _raw: bytes = field(repr=False)

    def response(self):
        from .proto.response_pb2 import StartPhoneAuth

        return parse(StartPhoneAuth, self._raw)


class SessionFile:
    def __init__(self, path):
        self.path = Path(path)

    async def load(self):
        def load():
            if not self.path.exists():
                return None
            value = json.loads(self.path.read_text("utf-8"))
            if value.get("version") != 1 or not value.get("token") or not value.get("user_id"):
                raise AuthenticationError("Invalid fncbale session")
            return Session(int(value["user_id"]), value["token"])

        return await asyncio.to_thread(load)

    async def save(self, session):
        def save():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary = tempfile.mkstemp(dir=self.path.parent, prefix=".session-")
            try:
                if os.name != "nt":
                    os.fchmod(descriptor, 0o600)
                with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                    json.dump(dict(version=1, user_id=session.user_id, token=session.token), stream)
                    stream.flush()
                    os.fsync(stream.fileno())
                if os.name == "nt":
                    # Restrict inherited Windows ACLs to the current Windows identity.
                    import subprocess

                    identity = subprocess.check_output(["whoami"], text=True).strip()
                    subprocess.run(
                        ["icacls", temporary, "/inheritance:r", "/grant:r", f"{identity}:(F)"],
                        check=True,
                        capture_output=True,
                        creationflags=0x08000000,
                    )
                os.replace(temporary, self.path)
            finally:
                with contextlib.suppress(FileNotFoundError):
                    os.unlink(temporary)

        await disk_call(save)


class AccountLock:
    def __init__(self, path):
        self.path = Path(path)
        self.stream = None

    def acquire(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        stream = self.path.open("a+b")
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            stream.close()
            raise SessionInUse("This account is already owned by another client") from exc
        self.stream = stream

    def release(self):
        if self.stream:
            if os.name == "nt":
                import msvcrt

                self.stream.seek(0)
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.stream.fileno(), fcntl.LOCK_UN)
            self.stream.close()
            self.stream = None
