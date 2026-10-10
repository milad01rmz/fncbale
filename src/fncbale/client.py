from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable, Iterable
from typing import Any, Literal
from dataclasses import asdict, replace
from functools import partial
import hashlib
import itertools
import os
import re
import json
from pathlib import Path
import random
import sqlite3
import time
import uuid


from .config import Config
from .contracts import contract
from .dispatcher import FSM, Router, conversation
from .errors import (
    AuthenticationError,
    PasswordRequired,
    BatchDownloadError,
    BaleError,
    ClientClosed,
    DeliveryUncertain,
    MessageReferencesUnavailable,
    HistoryPaginationGap,
    SearchSnapshotUnavailable,
    GroupCreationIncomplete,
    OperationFailed,
    PeerKindRequired,
    PeerNotFound,
    RpcError,
    StorageError,
    TransportError,
)
from .errors import ProtocolError
from .events import (
    Event,
    GapEvent,
    UnknownEvent,
    journal_events,
    message_content,
    message_from_history,
    normalize,
)
from .media import MediaPipeline, disk_call, report_progress
from .models import (
    Album,
    DownloadResult,
    DownloadProgressCallback,
    Media,
    MediaKind,
    MediaInfo,
    MediaSource,
    ProgressCallback,
    Message,
    MessageRef,
    MemberPage,
    MessageViews,
    Operation,
    OperationHandle,
    OperationStatus,
    Peer,
    PeerKind,
    PeerInput,
)
from .peer_cache import PeerCache
from .protocol import parse, short_peer, wire_peer
from .proto import request_pb2 as q, response_pb2 as r, struct_pb2 as s
from .resources import Resources
from .session import AccountLock, LoginChallenge, Session, SessionFile
from .storage import Store
from .transports import GrpcTransport, WebSocketTransport


def peer_dict(peer):
    return asdict(peer)


def new_rid():
    # Random positive int64; durable operation data preserves it across retries/processes.
    return uuid.uuid4().int & ((1 << 63) - 1) or 1


class Client:
    def __init__(
        self,
        session: Session | str | Path | None = None,
        *,
        data_dir=".fncbale",
        config=None,
        router=None,
        _resources=None,
        _store=None,
    ):
        self.config = config or Config()
        self.data_dir = Path(data_dir).resolve()
        self.session = session if isinstance(session, Session) else None
        self.session_file = SessionFile(
            session if isinstance(session, (str, Path)) else self.data_dir / "account.session"
        )
        self.resources = _resources or Resources(self.config)
        self.store = _store or Store(
            self.data_dir / "state.sqlite3",
            queue_size=self.config.queue_size,
            commit_window=self.config.commit_window,
        )
        self._owns_resources, self._owns_store = _resources is None, _store is None
        self.router = router or Router()
        self.media = MediaPipeline(self.data_dir, self.config, self.resources)
        self.store.register_spool(self.data_dir / "spool", self.media.in_use)
        self._rpc_limit = asyncio.Semaphore(self.config.rpc_limit)
        self._upload_limit = asyncio.Semaphore(self.config.upload_limit)
        self._download_limit = asyncio.Semaphore(self.config.download_limit)
        self._grpc = GrpcTransport(
            self.session.token if self.session else None, self.config, ssl_context=self.resources.ssl_context
        )
        self._ws = None
        self._lock = None
        self._tasks = []
        self._closed = False
        self._closing = False
        self._close_task = None
        self._disconnect_task = None
        self._active = False
        self._connect_lock = asyncio.Lock()
        self._recovery_lock = asyncio.Lock()
        self._wake = asyncio.Event()
        self._peer_cache = PeerCache(self.config.peer_cache_size)
        self._conversations = set()
        self._leased_events = set()
        self._event_consumer = False
        self._inbox_subscription = None
        self._inbox_wake = asyncio.Event()
        self._handler_task = None
        self._ingest_task = None
        self._progress = {}
        self._operation_waiters = {}
        self.account = ""
        self.fsm = None
        self.last_background_error = None
        self._login_challenge = None
        self._password_required = False
        self._auth_candidate = None

    @property
    def connected(self) -> bool:
        return self._active and self._ws is not None and self._ws.connected

    @property
    def login_challenge(self) -> LoginChallenge | None:
        """Current in-memory transaction, including a cancelled callback's request."""
        return self._login_challenge

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *_):
        await self.close()

    def _ensure_open(self):
        if self._closed or self._closing:
            raise ClientClosed("Client.close() is permanent; create another Client")

    async def login(
        self,
        phone_number: str,
        code_callback: Callable[[r.StartPhoneAuth], Awaitable[str]],
        *,
        password_callback: Callable[[], Awaitable[str]] | None = None,
    ) -> Session:
        # Serialize wire/commit stages, never application input. A callback can wait
        # indefinitely or close this client; late answers must pass staged validation.
        challenge = await self.start_login(phone_number)
        code = await code_callback(challenge.response())
        try:
            return await self.complete_login(challenge, code)
        except PasswordRequired:
            if password_callback is None:
                raise
            return await self.complete_password_login(challenge, await password_callback())

    def _ensure_auth_change(self):
        self._ensure_open()
        if self._active:
            raise BaleError("Disconnect before changing authentication")

    async def start_login(self, phone_number: str) -> LoginChallenge:
        async with self._connect_lock:
            return await self._start_login(phone_number)

    async def _auth_request(self, method, request):
        async with self._rpc_limit, self.resources.rpc_limit:
            return await self._grpc.request("bale.auth.v1.Auth", method, request.SerializeToString())

    async def _start_login(self, phone_number):
        self._ensure_auth_change()
        if not isinstance(phone_number, str) or not re.fullmatch(r"\+?[0-9\s()\-]+", phone_number.strip()):
            raise ValueError("Provide a phone number in local Iranian or international format")
        digits = "".join(ch for ch in phone_number if ch in "0123456789")
        if digits.startswith("0"):
            if len(digits) != 11:
                raise ValueError("Local Iranian phone numbers must contain 11 digits")
            digits = "98" + digits[1:]
        if not 8 <= len(digits) <= 15 or digits.startswith("0"):
            raise ValueError("Phone number length or country prefix is invalid")
        start = q.StartPhoneAuth(
            phone_number=int(digits),
            app_id=self.config.profile.app_id,
            api_key=self.config.profile.api_key,
            device_hash=uuid.uuid4().hex,
            device_title="fncbale async client",
            send_code_type=1,
            options=b"\x00\x01",
        )
        # Starting another transaction explicitly invalidates the previous local challenge,
        # even if the new request loses its response. Never repeat an OTP request blindly.
        self._login_challenge, self._auth_candidate, self._password_required = None, None, False
        raw = await self._auth_request("StartPhoneAuth", start)
        challenge = parse(r.StartPhoneAuth, raw)
        if not challenge.transaction_hash:
            raise AuthenticationError("Auth challenge returned no transaction")
        self._login_challenge = LoginChallenge(
            challenge.transaction_hash, challenge.is_registered, challenge.sent_code_type, raw
        )
        return self._login_challenge

    def _check_challenge(self, challenge):
        self._ensure_auth_change()
        if not isinstance(challenge, LoginChallenge) or challenge is not self._login_challenge:
            raise AuthenticationError("Challenge is consumed, superseded or belongs to another Client")

    async def complete_login(self, challenge: LoginChallenge, code: str) -> Session:
        async with self._connect_lock:
            return await self._complete_login(challenge, code)

    async def _complete_login(self, challenge, code):
        self._check_challenge(challenge)
        if self._auth_candidate is not None:
            return await self._commit_session(self._auth_candidate)
        if self._password_required:
            raise PasswordRequired(challenge)
        if not isinstance(code, str) or not code.strip():
            raise ValueError("Login code must be a nonempty string")
        request = q.ValidateCode(transaction_hash=challenge.transaction_hash, code=code.strip())
        request.is_jwt.value = True
        try:
            raw = await self._auth_request("ValidateCode", request)
        except RpcError as exc:
            # Literal discriminator independently found in the captured official web client.
            # A generic permission code (including 7) is not a password challenge.
            if exc.reason.strip().casefold() != "password needed for login":
                raise
            self._password_required = True
            raise PasswordRequired(challenge) from None
        return await self._commit_auth(raw)

    async def complete_password_login(self, challenge: LoginChallenge, password: str) -> Session:
        async with self._connect_lock:
            return await self._complete_password_login(challenge, password)

    async def _complete_password_login(self, challenge, password):
        self._check_challenge(challenge)
        if self._auth_candidate is not None:
            return await self._commit_session(self._auth_candidate)
        if not self._password_required:
            raise AuthenticationError("The server has not requested an account password")
        if not isinstance(password, str) or not password:
            raise ValueError("Account password must be a nonempty string")
        request = q.ValidatePassword(transaction_hash=challenge.transaction_hash, password=password)
        request.is_jwt.value = True
        raw = await self._auth_request("ValidatePassword", request)
        return await self._commit_auth(raw)

    async def _commit_auth(self, raw):
        auth = parse(r.Auth, raw)
        if not auth.jwt.value or not auth.user.id:
            raise AuthenticationError("Authentication returned no valid user and JWT")
        candidate = Session(auth.user.id, auth.jwt.value)
        self._auth_candidate = candidate
        return await self._commit_session(candidate)

    async def _commit_session(self, candidate):
        async def commit():
            changed_account = self.session is not None and candidate.user_id != self.session.user_id
            if self._lock and changed_account:
                await disk_call(self._lock.release)
                self._lock = None
            await self.session_file.save(candidate)
            self._peer_cache.clear()
            if changed_account:
                if self.account:
                    profile_key = hashlib.sha256(self.config.profile.grpc_url.encode()).hexdigest()[:12]
                    self.account = f"{profile_key}:{candidate.user_id}"
                self.fsm = None
                self._progress.clear()
                self.last_background_error = None
            self.session = candidate
            self._grpc._token = candidate.token
            self._login_challenge, self._auth_candidate, self._password_required = None, None, False

        task = asyncio.create_task(commit(), name="fncbale-session-commit")
        cancelled = False
        while True:
            try:
                await asyncio.shield(task)
                break
            except asyncio.CancelledError:
                if task.cancelled():
                    raise
                cancelled = True
            except Exception:
                if cancelled:
                    raise asyncio.CancelledError from None
                raise
        if cancelled:
            raise asyncio.CancelledError
        return candidate

    async def connect(self) -> None:
        self._ensure_open()
        if self._disconnect_task is not None and not self._disconnect_task.done():
            await asyncio.shield(self._disconnect_task)
        async with self._connect_lock:
            self._ensure_open()
            if self._active:
                return
            self.session = self.session or await self.session_file.load()
            if self.session is None:
                raise AuthenticationError("Provide a session or call login()")
            profile_key = hashlib.sha256(self.config.profile.grpc_url.encode()).hexdigest()[:12]
            self.account = f"{profile_key}:{self.session.user_id}"
            if self._lock is None:
                account_lock = AccountLock(
                    Path.home() / ".cache/fncbale/locks" / f"{profile_key}-{self.session.user_id}.lock"
                )
                await disk_call(account_lock.acquire, cancel_cleanup=lambda _: account_lock.release())
                self._lock = account_lock
            try:
                await self.store.start()
                await self.store.recover_operations(self.account)
                self._grpc._token = self.session.token
                await self._bootstrap_routes()
                self._ws = WebSocketTransport(self.session.token, self.config)
                await self._ws.connect()
                self._active = True
                self.fsm = FSM(self.store, self.account)
                self._start_ingest()
                await self.recover()
                self._tasks.append(asyncio.create_task(self._supervise(), name="fncbale-recovery"))
                for i in range(self.config.outbox_workers):
                    self._tasks.append(asyncio.create_task(self._outbox_worker(), name=f"fncbale-outbox-{i}"))
                if self.router.handlers:
                    self.start_handlers()
            except BaseException:
                await self._disconnect_unlocked()
                await disk_call(self._lock.release)
                self._lock = None
                raise

    async def disconnect(self) -> None:
        if self._closing:
            # Permanent close is already the lifecycle owner. Join its shielded
            # task (and original result/error), never queue cleanup after it.
            await self.close()
            return
        if self._disconnect_task is None or self._disconnect_task.done():
            self._disconnect_task = asyncio.create_task(self._disconnect_once(), name="fncbale-disconnect")

            def completed(task):
                if not task.cancelled() and (error := task.exception()) is not None:
                    self.last_background_error = type(error).__name__

            self._disconnect_task.add_done_callback(completed)
        # A handler must not wait directly on its own dispatcher cancellation.
        # Shield breaks that dependency when shutdown cancels the handler, while
        # the independent cleanup task keeps joining its workers/socket normally.
        await asyncio.shield(self._disconnect_task)

    async def _disconnect_once(self):
        async with self._connect_lock:
            if self._closed:
                # A previously admitted job may reach this lock after close.
                # The close task has released the lock and completed its result.
                if self._close_task is not None:
                    self._close_task.result()
                return
            await self._disconnect_unlocked()

    async def _disconnect_unlocked(self):
        self._active = False
        for scope in tuple(self._conversations):
            scope.close()
        self._conversations.clear()
        tasks, self._tasks = self._tasks, []
        for task in tasks:
            if task is not asyncio.current_task():
                task.cancel()
        if tasks:
            await asyncio.gather(
                *[t for t in tasks if t is not asyncio.current_task()], return_exceptions=True
            )
        if self._ws:
            await self._ws.close()
        # Explicit disconnect ends prior iterator ownership even if the caller
        # still holds a suspended generator. Its late finally cannot release a
        # consumer acquired after reconnect.
        self._unsubscribe_inbox()
        self._event_consumer = False
        self._leased_events.clear()
        self._handler_task = None
        self._ingest_task = None
        self._wake.set()
        for event, _ in self._operation_waiters.values():
            event.set()

    async def close(self) -> None:
        if self._close_task is None:
            self._closing = True
            self._close_task = asyncio.create_task(self._close_once(), name="fncbale-close")
            self._close_task.add_done_callback(
                lambda task: task.exception() if not task.cancelled() else None
            )
        await asyncio.shield(self._close_task)

    async def _close_once(self):
        async with self._connect_lock:
            errors = []
            try:
                closers = [self._disconnect_unlocked, self._grpc.close]
                if self._owns_store:
                    closers.append(self.store.close)
                if self._owns_resources:
                    closers.append(self.resources.close)
                for closer in closers:
                    try:
                        await closer()
                    except Exception as exc:
                        errors.append(exc)
            finally:
                if self._lock:
                    await disk_call(self._lock.release)
                    self._lock = None
                self._login_challenge, self._auth_candidate, self._password_required = None, None, False
                self._peer_cache.clear()
                self.media.close_cache()
                self._closed = True
            if errors:
                raise ExceptionGroup("Client cleanup failed", errors)

    async def _call_bytes(self, method, payload, route):
        c = contract(method)
        return await self._request(c.service, method, payload, route)

    def _ensure_rpc_account(self, account):
        if self.account != account:
            raise BaleError("RPC account changed; start the request with its intended account")

    def _stream_is_current(self, account):
        return not self._closing and not self._closed and self.account == account

    async def _request(self, service, method, payload, route):
        if route not in ("websocket", "http"):
            raise ValueError("route must be websocket or http")
        account = self.account
        self._ensure_open()
        if account:
            await self.store.start()
        while True:
            self._ensure_open()
            self._ensure_rpc_account(account)
            delay = self.store.rate_deadline(account) - time.time()
            if delay > 0:
                await asyncio.sleep(min(delay, 30))
                continue
            async with self._rpc_limit, self.resources.rpc_limit:
                self._ensure_open()
                self._ensure_rpc_account(account)
                if self.store.rate_deadline(account) > time.time():
                    continue
                transport = self._ws if route == "websocket" else self._grpc
                if transport is None:
                    raise TransportError("Transport is not connected")
                try:
                    return await transport.request(service, method, payload)
                except RpcError as exc:
                    if exc.code == 8 and account and not self._closing:
                        await self.store.limit_account(
                            account, exc.retry_after if exc.retry_after is not None else 1
                        )
                    raise

    async def _rpc(self, method, request, *, readonly=None, route=None):
        self._ensure_open()
        account = self.account
        c = contract(method)
        if not isinstance(request, c.request):
            raise TypeError(f"{method} expects {c.request.__name__}")
        payload = request.SerializeToString()
        is_read = c.readonly if readonly is None else readonly
        routes = [route] if route else ["websocket", "websocket", "http"]
        last = None
        for i, chosen in enumerate(routes):
            self._ensure_open()
            self._ensure_rpc_account(account)
            try:
                raw = await self._call_bytes(method, payload, chosen)
                self._ensure_rpc_account(account)
                return parse(c.response, raw)
            except RpcError as exc:
                if exc.code != 8 or not is_read:
                    raise
                last = exc
                self._ensure_open()
                self._ensure_rpc_account(account)
                await asyncio.sleep(exc.retry_after or 1)
            except TransportError as exc:
                last = exc
                if exc.possibly_sent and not is_read:
                    raise
                if i + 1 < len(routes):
                    await asyncio.sleep(0.2 + random.random() * 0.1)
        raise last

    async def invoke_raw(
        self,
        service: str,
        method: str,
        payload: bytes,
        *,
        retry_policy: Literal["none", "readonly"],
        route: Literal["websocket", "http"] = "websocket",
    ) -> bytes:
        """Explicit policy: 'none' or 'readonly'. No automatic write idempotency assumption."""
        if retry_policy not in ("none", "readonly"):
            raise ValueError("retry_policy must be none or readonly")
        self._ensure_open()
        account = self.account
        routes = [route] if retry_policy == "none" else [route, route, "http"]
        for i, chosen in enumerate(routes):
            self._ensure_open()
            self._ensure_rpc_account(account)
            try:
                response = await self._request(service, method, payload, chosen)
                if retry_policy == "readonly":
                    self._ensure_rpc_account(account)
                return response
            except RpcError as exc:
                if exc.code != 8 or retry_policy != "readonly" or i + 1 == len(routes):
                    raise
            except TransportError:
                if i + 1 == len(routes):
                    raise

    def _cache_peer(self, peer):
        expires = time.monotonic() + self.config.peer_cache_ttl
        self._peer_cache.put(peer, expires)
        return peer

    @staticmethod
    def _group_peer(group, fallback_hash=0):
        return Peer(
            PeerKind.CHANNEL if group.groupType == 1 else PeerKind.GROUP,
            group.id,
            group.accessHash or fallback_hash,
            group.nick.value or None,
            group.title,
        )

    async def resolve_peer(self, value: PeerInput, *, kind: PeerKind | str | None = None) -> Peer:
        if isinstance(value, Peer):
            return self._cache_peer(value)
        if isinstance(value, Message):
            return value.ref.peer
        if isinstance(value, MessageRef):
            return value.peer
        if isinstance(value, int) or isinstance(value, str) and value.lstrip("-").isdigit():
            number = int(value)
            if kind is not None:
                peer = Peer(PeerKind(kind), number)
                if peer.kind != PeerKind.USER:
                    return self._group_peer(await self.get_full_group(peer))
                return self._cache_peer(peer)
            candidates = {
                entry[1].key: entry[1]
                for prefix in (1, 2)
                if (entry := self._peer_cache.get(f"{prefix}:{number}")) is not None
            }
            if len(candidates) == 1:
                return next(iter(candidates.values()))
            raise PeerKindRequired("Numeric peer needs kind or an unambiguous cached identity")
        username = str(value).strip()
        if "://" in username:
            from urllib.parse import urlparse

            url = urlparse(username)
            if url.hostname not in ("ble.ir", "bale.ai", "web.bale.ai"):
                raise ValueError("Unsupported peer link")
            username = url.path.strip("/")
        username = username.lstrip("@").lower()
        if not username or "/" in username:
            raise ValueError("Expected public username")
        cached = self._peer_cache.get("@" + username)
        if cached and cached[0] > time.monotonic():
            return cached[1]
        candidates = []
        search = contract("SearchPeer").request()
        search.query.add().searchPieceText.query = username.encode()
        for method, request in (
            ("SearchPeer", search),
            ("SearchContacts", contract("SearchContacts").request(request=username)),
        ):
            try:
                response = await self._rpc(method, request)
            except RpcError:
                continue
            for group in response.groups:
                if group.nick.value.lower().lstrip("@") == username:
                    candidates.append(self._group_peer(group))
            for user in response.users:
                if user.nick.value.lower().lstrip("@") == username:
                    candidates.append(
                        Peer(PeerKind.USER, user.id, user.accessHash, user.nick.value, user.name)
                    )
            # Current search often returns references only. Hydrate before exact matching.
            for reference in response.groupPeers:
                group = await self.get_full_group(
                    Peer(PeerKind.GROUP, reference.groupId, reference.accessHash)
                )
                if group.nick.value.lower().lstrip("@") == username:
                    candidates.append(self._group_peer(group, reference.accessHash))
            if response.userPeers:
                users_request = contract("LoadUsers").request()
                users_request.peers.extend(response.userPeers)
                users = await self._rpc("LoadUsers", users_request)
                for user in users.users:
                    if user.nick.value.lower().lstrip("@") == username:
                        candidates.append(
                            Peer(PeerKind.USER, user.id, user.accessHash, user.nick.value, user.name)
                        )
            if candidates:
                break
        unique = {p.key: p for p in candidates}
        if len(unique) != 1:
            raise PeerNotFound("No unique exact username match")
        peer = next(iter(unique.values()))
        if peer.kind != PeerKind.USER:
            peer = self._group_peer(await self.get_full_group(peer), peer.access_hash)
            if (peer.username or "").lower().lstrip("@") != username:
                raise PeerNotFound("Full group username does not match search result")
        return self._cache_peer(peer)

    async def get_full_group(self, peer: PeerInput) -> s.WebFullGroup:
        if not isinstance(peer, Peer):
            peer = await self.resolve_peer(peer, kind=PeerKind.GROUP if isinstance(peer, int) else None)
        if peer.kind == PeerKind.USER:
            raise ValueError("Expected group/channel peer")
        request = contract("GetFullGroup").request()
        request.peer.groupId, request.peer.accessHash = peer.id, peer.access_hash
        try:
            response = await self._rpc("GetFullGroup", request)
        except RpcError:
            self._peer_cache.discard(peer.key)
            raise
        if (
            not response.HasField("fullGroup")
            or not response.fullGroup.id
            or response.fullGroup.id != peer.id
        ):
            self._peer_cache.discard(peer.key)
            raise ProtocolError("Full group response has an unexpected identity")
        self._cache_peer(self._group_peer(response.fullGroup, peer.access_hash))
        return response.fullGroup

    async def iter_history(
        self,
        peer: PeerInput,
        *,
        limit: int | None = None,
        page_size: int = 100,
        before: int = -1,
        route: Literal["websocket", "http"] | None = None,
    ) -> AsyncIterator[Message]:
        self._ensure_open()
        account = self.account
        peer = await self.resolve_peer(peer)
        if not 1 <= page_size <= 100:
            raise ValueError("page_size must be 1..100")
        if limit is not None and limit < 0:
            raise ValueError("limit must be nonnegative or None")
        remaining, cursor = limit, before
        boundary_date, boundary_rids = None, set()
        fetch_size = page_size
        while remaining is None or remaining > 0:
            if not self._stream_is_current(account):
                return
            request = contract("LoadHistory").request(
                date=cursor,
                loadMode=2,
                limit=fetch_size if boundary_rids or remaining is None else min(fetch_size, remaining),
            )
            request.peer.CopyFrom(short_peer(peer))
            response = await self._rpc("LoadHistory", request, route=route)
            if not self._stream_is_current(account):
                return
            if not response.history:
                break
            page = sorted(response.history, key=lambda item: item.date, reverse=True)
            if cursor != -1 and any(item.date > cursor for item in page):
                raise ProtocolError("History returned messages beyond its backward cursor")
            page_rids = set()
            for item in page:
                if not self._stream_is_current(account):
                    return
                identity = (item.date, item.rid)
                if identity in page_rids or (item.date == boundary_date and item.rid in boundary_rids):
                    continue
                page_rids.add(identity)
                message = message_from_history(peer, item)
                message.history_verified = True
                yield message
                if remaining is not None:
                    remaining -= 1
                    if remaining == 0:
                        return
            if not self._stream_is_current(account):
                return
            oldest = page[-1].date
            if len(page) < request.limit:
                break
            if oldest == boundary_date:
                boundary_rids.update(item.rid for item in page if item.date == oldest)
                if fetch_size == 100:
                    # There is no RID/offset in the verified LoadHistory contract.
                    # Never silently jump past a saturated equal-date bucket.
                    raise HistoryPaginationGap(peer, oldest)
                fetch_size = 100
            else:
                boundary_date = oldest
                boundary_rids = {item.rid for item in page if item.date == oldest}
                fetch_size = min(100, max(page_size, len(boundary_rids) + 1))
            cursor = oldest

    async def _enqueue(self, peer, method, request, context, *, idempotency_key=None, intent=None):
        self._ensure_open()
        if not self._active:
            raise BaleError("Connect before accepting durable operations")
        raw = request.SerializeToString() if request is not None else b""
        digest = hashlib.sha256(
            json.dumps(intent or context, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()
        account = self.account
        operation_id = await self.store.enqueue(
            account,
            peer.key,
            method,
            raw,
            json.dumps(context, ensure_ascii=False),
            idempotency_key,
            self.config.outbox_limit,
            digest,
        )
        self._wake.set()
        return OperationHandle(self, operation_id, account=account)

    async def enqueue_message(
        self,
        peer: PeerInput,
        text: str,
        *,
        reply_to: Message | MessageRef | None = None,
        idempotency_key: str | None = None,
        silent: bool = False,
    ) -> OperationHandle:
        peer = await self.resolve_peer(peer)
        request = contract("SendMessage").request(rid=new_rid(), isSilent=silent)
        request.peer.CopyFrom(short_peer(peer))
        request.message.textMessage.text = text
        self._apply_reply(request.quotedMessageReference, reply_to)
        context = {"kind": "message", "peer": peer_dict(peer), "rids": [request.rid]}
        intent = {
            "method": "SendMessage",
            "peer": peer.key,
            "text": text,
            "silent": silent,
            "reply": asdict(reply_to.ref if isinstance(reply_to, Message) else reply_to)
            if reply_to
            else None,
        }
        return await self._enqueue(
            peer, "SendMessage", request, context, idempotency_key=idempotency_key, intent=intent
        )

    @staticmethod
    def _apply_reply(target, reply_to):
        if reply_to is None:
            return
        ref = reply_to.ref if isinstance(reply_to, Message) else reply_to
        if not isinstance(ref, MessageRef):
            raise TypeError("reply_to requires Message or MessageRef")
        target.peer.CopyFrom(short_peer(ref.peer))
        target.rid = ref.rid
        if ref.date:
            target.date.value = ref.date
        if ref.seq:
            target.seq.value = ref.seq

    async def send_message(self, peer: PeerInput, text: str, **kwargs) -> Message:
        return await (await self.enqueue_message(peer, text, **kwargs)).wait()

    async def reply(self, message: Message | MessageRef, text: str, **kwargs) -> Message:
        ref = message.ref if isinstance(message, Message) else message
        return await self.send_message(ref.peer, text, reply_to=ref, **kwargs)

    async def enqueue_media(
        self,
        peer: PeerInput,
        media: Media,
        *,
        reply_to: Message | MessageRef | None = None,
        idempotency_key: str | None = None,
        progress: ProgressCallback | None = None,
    ) -> OperationHandle:
        return await self._enqueue_media(
            peer, [media], reply_to=reply_to, idempotency_key=idempotency_key, progress=progress
        )

    async def enqueue_album(
        self,
        peer: PeerInput,
        media: Iterable[Media],
        *,
        reply_to: Message | MessageRef | None = None,
        idempotency_key: str | None = None,
        progress: ProgressCallback | None = None,
    ) -> OperationHandle:
        self._ensure_open()
        items = tuple(media)
        if not 2 <= len(items) <= 10 or any(
            item.kind not in (MediaKind.PHOTO, MediaKind.VIDEO) for item in items
        ):
            raise ValueError("Album requires 2..10 photo/video items")
        return await self._enqueue_media(
            peer, items, reply_to=reply_to, idempotency_key=idempotency_key, progress=progress
        )

    async def _enqueue_media(self, peer, items, *, reply_to, idempotency_key, progress):
        self._ensure_open()
        if not self._active:
            raise BaleError("Connect before accepting durable operations")
        account = self.account
        peer = await self.resolve_peer(peer)
        self._ensure_operation_account(account)
        prepared = []
        accepting = False
        try:
            for item in items:
                if not isinstance(item, Media):
                    raise TypeError("Expected Media items")
                prepared.append(await self.media.prepare(item))
                self.media.in_use.add(Path(prepared[-1]["path"]).resolve())
                self._ensure_operation_account(account)
            rids = [new_rid() for _ in items]
            album = len(items) > 1
            context = {
                "kind": "album" if album else "media",
                "peer": peer_dict(peer),
                "rids": rids,
                "grouped_id": new_rid() if album else None,
                "media": prepared,
                "reply": asdict(reply_to.ref if isinstance(reply_to, Message) else reply_to)
                if reply_to
                else None,
            }
            intent = {
                "kind": context["kind"],
                "peer": peer.key,
                "reply": context["reply"],
                "media": [{k: v for k, v in item.items() if k != "path"} for item in prepared],
            }
            accepting = True
            handle = await self._enqueue(
                peer,
                "SendMultiMediaMessage" if album else "SendMessage",
                None,
                context,
                idempotency_key=idempotency_key,
                intent=intent,
            )
            # Admission is already committed: inspect its original account even
            # if the caller reauthenticated while waiting for that commit.
            accepted = json.loads((await self.store.operation(account, handle.operation_id))["context"])
            if [x["path"] for x in accepted.get("media", [])] != [x["path"] for x in prepared]:
                for info in prepared:
                    await asyncio.to_thread(Path(info["path"]).unlink, missing_ok=True)
            if progress and self.account == account:
                self._progress[handle.operation_id] = progress
            return handle
        except BaseException as exc:
            # Only remove unaccepted preparations; accepted operations own their spool.
            if "handle" not in locals() and not (accepting and isinstance(exc, asyncio.CancelledError)):
                for info in prepared:
                    await asyncio.to_thread(Path(info["path"]).unlink, missing_ok=True)
            raise
        finally:
            self.media.in_use.difference_update(Path(item["path"]).resolve() for item in prepared)

    async def send_album(self, peer: PeerInput, items: list[Media] | tuple[Media, ...], **kwargs) -> Album:
        return await (await self.enqueue_album(peer, items, **kwargs)).wait()

    async def _send_media(self, peer, source, kind, *, caption="", filename=None, mime_type=None, **kwargs):
        return await (
            await self.enqueue_media(peer, Media(source, kind, caption, filename, mime_type), **kwargs)
        ).wait()

    async def send_photo(self, peer: PeerInput, source: MediaSource, **kwargs: Any) -> Message:
        return await self._send_media(peer, source, MediaKind.PHOTO, **kwargs)

    async def send_video(self, peer: PeerInput, source: MediaSource, **kwargs: Any) -> Message:
        return await self._send_media(peer, source, MediaKind.VIDEO, **kwargs)

    async def send_audio(self, peer: PeerInput, source: MediaSource, **kwargs: Any) -> Message:
        return await self._send_media(peer, source, MediaKind.AUDIO, **kwargs)

    async def send_voice(self, peer: PeerInput, source: MediaSource, **kwargs: Any) -> Message:
        return await self._send_media(peer, source, MediaKind.VOICE, **kwargs)

    async def send_document(self, peer: PeerInput, source: MediaSource, **kwargs: Any) -> Message:
        return await self._send_media(peer, source, MediaKind.DOCUMENT, **kwargs)

    async def _copy_snapshots(self, messages):
        account = self.account
        refs = [item.ref if isinstance(item, Message) else item for item in messages]
        if not refs or any(not isinstance(ref, MessageRef) for ref in refs):
            raise TypeError("Copy requires Message or MessageRef")
        if len({ref.peer.key for ref in refs}) != 1 or len({ref.rid for ref in refs}) != len(refs):
            raise ValueError("Copy source references must be distinct and belong to one peer")
        wanted = {ref.rid: ref for ref in refs}
        found = {}
        before = max(ref.date for ref in refs) + 1 if all(ref.date > 0 for ref in refs) else -1
        async for item in self.iter_history(refs[0].peer, limit=100, before=before):
            self._ensure_operation_account(account)
            if item.rid in wanted:
                ref = wanted[item.rid]
                if (not ref.date or item.ref.date == ref.date) and (not ref.seq or item.ref.seq == ref.seq):
                    found[item.rid] = s.WebHistory.FromString(item.raw)
            if len(found) == len(wanted):
                break
        self._ensure_operation_account(account)
        if len(found) != len(wanted):
            raise ValueError("Copy source snapshot is unavailable in the bounded history window")
        return [found[ref.rid] for ref in refs]

    async def enqueue_copy_message(
        self,
        peer: PeerInput,
        message: Message | MessageRef,
        *,
        reply_to: Message | MessageRef | None = None,
        idempotency_key: str | None = None,
    ) -> OperationHandle:
        self._ensure_open()
        account = self.account
        snapshots = await self._copy_snapshots([message])
        self._ensure_operation_account(account)
        return await self._enqueue_copy_snapshots(
            peer, snapshots, reply_to=reply_to, idempotency_key=idempotency_key
        )

    async def copy_message(self, peer: PeerInput, message: Message | MessageRef, **kwargs) -> Message:
        return await (await self.enqueue_copy_message(peer, message, **kwargs)).wait()

    async def enqueue_copy_album(
        self,
        peer: PeerInput,
        album: Album,
        *,
        reply_to: Message | MessageRef | None = None,
        idempotency_key: str | None = None,
    ) -> OperationHandle:
        self._ensure_open()
        if not isinstance(album, Album) or not 2 <= len(album.messages) <= 10:
            raise ValueError("Copy album requires 2..10 ordered source messages")
        account = self.account
        snapshots = await self._copy_snapshots(album.messages)
        self._ensure_operation_account(account)
        if not album.grouped_id or any(item.groupedId.value != album.grouped_id for item in snapshots):
            raise ValueError("Copy source snapshots do not belong to the requested album")
        return await self._enqueue_copy_snapshots(
            peer, snapshots, reply_to=reply_to, idempotency_key=idempotency_key
        )

    async def copy_album(self, peer: PeerInput, album: Album, **kwargs) -> Album:
        return await (await self.enqueue_copy_album(peer, album, **kwargs)).wait()

    async def _enqueue_copy_snapshots(self, peer, snapshots, *, reply_to=None, idempotency_key=None):
        self._ensure_open()
        account = self.account
        # Freeze typed content before any await; exact metadata and unknown fields survive.
        contents = []
        for snapshot in snapshots:
            content = s.WebMessage()
            content.CopyFrom(snapshot.message)
            if not content.HasField("textMessage") and not content.HasField("documentMessage"):
                if snapshot.HasField("quotedMessage"):
                    content.CopyFrom(snapshot.quotedMessage.quotedMessageContent)
            fields = {field.name for field, _ in content.ListFields()}
            if fields not in ({"textMessage"}, {"documentMessage"}):
                raise ValueError(
                    "Copy supports direct text/document content; unsupported content is explicit"
                )
            if content.HasField("documentMessage"):
                doc = content.documentMessage
                if not doc.fileId or not doc.accessHash or doc.fileSize <= 0:
                    raise ValueError("Copy requires a valid existing media reference")
                doc.ClearField("groupedId")
            contents.append(content)
        album = len(contents) > 1
        if not contents or len(contents) > 10:
            raise ValueError("Copy requires 1..10 source snapshots")
        if album and any(
            not item.HasField("documentMessage")
            or not (
                item.documentMessage.ext.HasField("documentExPhoto")
                or item.documentMessage.ext.HasField("documentExVideo")
            )
            for item in contents
        ):
            raise ValueError("Copy album supports only photos and videos")
        peer = await self.resolve_peer(peer)
        self._ensure_operation_account(account)
        rids = [new_rid() for _ in contents]
        method = "SendMultiMediaMessage" if album else "SendMessage"
        request = contract(method).request()
        context = {
            "kind": "album" if album else "media" if contents[0].HasField("documentMessage") else "message",
            "peer": peer_dict(peer),
            "rids": rids,
        }
        if album:
            request.peer.CopyFrom(wire_peer(peer))
            request.groupedId = new_rid()
            context["grouped_id"] = request.groupedId
            for rid, content in zip(rids, contents, strict=True):
                request.multiMedia.add(randomId=rid).media.CopyFrom(content.documentMessage)
            self._apply_reply(request.repliedMessage, reply_to)
        else:
            request.peer.CopyFrom(short_peer(peer))
            request.rid = rids[0]
            request.message.CopyFrom(contents[0])
            self._apply_reply(request.quotedMessageReference, reply_to)
        intent = {
            "kind": "copy",
            "peer": peer.key,
            "content": [item.SerializeToString(deterministic=True).hex() for item in contents],
            "reply": asdict(reply_to.ref if isinstance(reply_to, Message) else reply_to)
            if reply_to
            else None,
        }
        return await self._enqueue(
            peer, method, request, context, idempotency_key=idempotency_key, intent=intent
        )

    async def enqueue_edit_message(
        self, message: Message | MessageRef, text: str, *, idempotency_key: str | None = None
    ) -> OperationHandle:
        ref = message.ref if isinstance(message, Message) else message
        request = contract("UpdateMessage").request(rid=ref.rid)
        request.peer.CopyFrom(short_peer(ref.peer))
        request.updatedMessage.textMessage.text = text
        context = {
            "kind": "edit",
            "peer": peer_dict(ref.peer),
            "rids": [ref.rid],
            "date": ref.date,
            "seq": ref.seq,
        }
        if isinstance(message, Message):
            context.update(
                grouped_id=message.grouped_id,
                author_signature=message.author_signature,
                quoted=message.quoted.SerializeToString().hex()
                if isinstance(message.quoted, s.WebQuotedMessage)
                else None,
            )
        return await self._enqueue(
            ref.peer,
            "UpdateMessage",
            request,
            context,
            idempotency_key=idempotency_key,
            intent={"method": "UpdateMessage", "ref": asdict(ref), "text": text},
        )

    async def edit_message(
        self, message: Message | MessageRef, text: str, *, idempotency_key: str | None = None
    ) -> Message:
        return await (await self.enqueue_edit_message(message, text, idempotency_key=idempotency_key)).wait()

    async def enqueue_edit_caption(
        self, message: Message | MessageRef, caption: str, *, idempotency_key: str | None = None
    ) -> OperationHandle:
        ref = message.ref if isinstance(message, Message) else message
        found = None
        async for item in self.iter_history(ref.peer, limit=100, before=ref.date + 1):
            if item.rid == ref.rid:
                found = item
                break
        if found is None:
            raise ValueError("Message was not found")
        history = s.WebHistory.FromString(found.raw)
        if not history.message.HasField("documentMessage"):
            raise ValueError("Message has no media caption")
        request = contract("UpdateMessage").request(rid=ref.rid)
        request.peer.CopyFrom(short_peer(ref.peer))
        request.updatedMessage.CopyFrom(history.message)
        request.updatedMessage.documentMessage.caption.text = caption
        context = {
            "kind": "edit",
            "peer": peer_dict(ref.peer),
            "rids": [ref.rid],
            "date": found.ref.date,
            "seq": found.ref.seq or ref.seq,
            "grouped_id": found.grouped_id,
            "author_signature": found.author_signature,
            "quoted": found.quoted.SerializeToString().hex() if found.quoted is not None else None,
        }
        return await self._enqueue(
            ref.peer,
            "UpdateMessage",
            request,
            context,
            idempotency_key=idempotency_key,
            intent={"method": "edit_caption", "ref": asdict(ref), "caption": caption},
        )

    async def edit_caption(
        self, message: Message | MessageRef, caption: str, *, idempotency_key: str | None = None
    ) -> Message:
        return await (
            await self.enqueue_edit_caption(message, caption, idempotency_key=idempotency_key)
        ).wait()

    async def enqueue_delete_messages(
        self,
        messages: Iterable[Message | MessageRef],
        *,
        just_mine: bool = False,
        idempotency_key: str | None = None,
    ) -> OperationHandle:
        refs = [m.ref if isinstance(m, Message) else m for m in messages]
        if not refs or len({m.peer.key for m in refs}) != 1:
            raise ValueError("Delete batch must contain messages from one peer")
        request = contract("DeleteMessage").request(rids=[ref.rid for ref in refs])
        request.peer.CopyFrom(short_peer(refs[0].peer))
        request.dates.dates.extend(ref.date for ref in refs)
        request.justMine.value = just_mine
        context = {"kind": "delete", "peer": peer_dict(refs[0].peer), "rids": [r.rid for r in refs]}
        return await self._enqueue(
            refs[0].peer,
            "DeleteMessage",
            request,
            context,
            idempotency_key=idempotency_key,
            intent={"method": "DeleteMessage", "refs": [asdict(x) for x in refs], "just_mine": just_mine},
        )

    async def delete_messages(
        self,
        messages: Iterable[Message | MessageRef],
        *,
        just_mine: bool = False,
        idempotency_key: str | None = None,
    ) -> tuple[int, ...]:
        return await (
            await self.enqueue_delete_messages(messages, just_mine=just_mine, idempotency_key=idempotency_key)
        ).wait()

    async def enqueue_delete_message(self, message: Message | MessageRef, **kwargs: Any) -> OperationHandle:
        return await self.enqueue_delete_messages([message], **kwargs)

    async def delete_message(self, message: Message | MessageRef, **kwargs: Any) -> tuple[int, ...]:
        return await self.delete_messages([message], **kwargs)

    async def enqueue_forward(
        self,
        peer: PeerInput,
        messages: Message | MessageRef | Iterable[Message | MessageRef],
        *,
        idempotency_key: str | None = None,
    ) -> OperationHandle:
        return await self._enqueue_forward(peer, messages, idempotency_key=idempotency_key)

    async def enqueue_forward_album(
        self, peer: PeerInput, album: Album, *, idempotency_key: str | None = None
    ) -> OperationHandle:
        self._ensure_open()
        if not isinstance(album, Album):
            raise TypeError("Expected Album with ordered photo/video message snapshots")
        items = tuple(album.messages)
        if (
            not 2 <= len(items) <= 10
            or not album.grouped_id
            or any(not isinstance(item, Message) for item in items)
            or len({item.ref.peer.key for item in items}) != 1
            or len({item.rid for item in items}) != len(items)
            or any(
                item.grouped_id != album.grouped_id
                or item.media is None
                or item.media.kind not in (MediaKind.PHOTO, MediaKind.VIDEO)
                for item in items
            )
        ):
            raise ValueError("Forward album requires 2..10 distinct photo/video items from one source album")
        return await self._enqueue_forward(peer, items, idempotency_key=idempotency_key, grouped=True)

    async def forward_album(
        self, peer: PeerInput, album: Album, *, idempotency_key: str | None = None
    ) -> Album:
        return await (await self.enqueue_forward_album(peer, album, idempotency_key=idempotency_key)).wait()

    async def _enqueue_forward(self, peer, messages, *, idempotency_key=None, grouped=False):
        peer = await self.resolve_peer(peer)
        if isinstance(messages, (Message, MessageRef)):
            messages = [messages]
        refs = [m.ref if isinstance(m, Message) else m for m in messages]
        if not refs:
            raise ValueError("Forward requires messages")
        request = contract("ForwardMessages").request(rid=[new_rid() for _ in refs])
        request.peer.CopyFrom(wire_peer(peer))
        for ref in refs:
            self._apply_reply(request.forwardedMessages.add(), ref)
        context = {"kind": "forward", "peer": peer_dict(peer), "rids": list(request.rid)}
        intent = {"method": "ForwardMessages", "peer": peer.key, "refs": [asdict(x) for x in refs]}
        if grouped:
            request.groupedId.value = new_rid()
            context["grouped_id"] = request.groupedId.value
            intent["grouped"] = True
        return await self._enqueue(
            peer,
            "ForwardMessages",
            request,
            context,
            idempotency_key=idempotency_key,
            intent=intent,
        )

    async def forward(
        self,
        peer: PeerInput,
        messages: Message | MessageRef | Iterable[Message | MessageRef],
        *,
        idempotency_key: str | None = None,
    ) -> tuple[Message, ...]:
        return await (await self.enqueue_forward(peer, messages, idempotency_key=idempotency_key)).wait()

    def _ensure_operation_account(self, account):
        if self.account != account:
            raise BaleError("Operation belongs to another Client account; use its original account")

    async def get_operation(self, operation_id: str) -> Operation:
        account = self.account
        row = await self.store.operation(account, operation_id)
        self._ensure_operation_account(account)
        return self._operation_summary(row)

    @staticmethod
    def _operation_summary(row) -> Operation:
        context = json.loads(row["context"])
        return Operation(
            row["id"],
            OperationStatus(row["status"]),
            row["method"],
            row["attempts"],
            row["error"],
            row["not_before"] or None,
            row["cycle_attempts"],
            bool(context.get("_rpc_confirmed")),
            bool(context.get("_history_verified")),
        )

    async def iter_operations(
        self,
        *,
        statuses: Iterable[OperationStatus | str] | None = None,
        limit: int | None = None,
        page_size: int = 100,
    ) -> AsyncIterator[Operation]:
        """Read account-local summaries ordered by creation time/id using bounded pages."""
        if not 1 <= page_size <= 1000 or (limit is not None and limit < 0):
            raise ValueError("Invalid operation page size or limit")
        if isinstance(statuses, (str, OperationStatus)):
            statuses = (statuses,)
        selected = (
            tuple(sorted({OperationStatus(status).value for status in statuses}))
            if statuses is not None
            else None
        )
        if selected == () or limit == 0:
            return
        after = None
        count = 0
        account = self.account
        while limit is None or count < limit:
            size = min(page_size, limit - count) if limit is not None else page_size
            if self.account != account:
                return
            rows = await self.store.operation_page(account, statuses=selected, after=after, limit=size)
            if not rows:
                return
            for row in rows:
                if self.account != account:
                    return
                yield self._operation_summary(row)
                count += 1
            after = (rows[-1]["created"], rows[-1]["id"])
            if len(rows) < size:
                return

    async def cancel_operation(self, operation_id: str) -> bool:
        cancelled = await self.store.cancel_unsent(self.account, operation_id)
        self._notify_operation(operation_id)
        return cancelled

    async def wait_operation(self, operation_id):
        account = self.account
        event, users = self._operation_waiters.get(operation_id, (asyncio.Event(), 0))
        self._operation_waiters[operation_id] = (event, users + 1)
        try:
            while True:
                event.clear()
                self._ensure_operation_account(account)
                row = await self.store.operation(account, operation_id)
                self._ensure_operation_account(account)
                if row["status"] == "confirmed":
                    row = await self._hydrate_result_refs(row)
                    self._ensure_operation_account(account)
                    return self._operation_result(row)
                if row["status"] == "uncertain":
                    raise DeliveryUncertain(operation_id)
                if row["status"] in ("failed", "cancelled"):
                    raise OperationFailed(operation_id, row["error"] or row["status"])
                self._ensure_open()
                if not self._active:
                    raise BaleError("Operation is durable but Client is disconnected")
                try:
                    await asyncio.wait_for(event.wait(), 5)
                except TimeoutError:
                    pass
        finally:
            _, users = self._operation_waiters[operation_id]
            if users == 1:
                self._operation_waiters.pop(operation_id, None)
            else:
                self._operation_waiters[operation_id] = (event, users - 1)

    def _notify_operation(self, operation_id):
        item = self._operation_waiters.get(operation_id)
        if item:
            item[0].set()

    async def _hydrate_result_refs(self, row):
        account = row["account"]
        self._ensure_operation_account(account)
        context = json.loads(row["context"])
        if context["kind"] != "album" and not (context["kind"] == "forward" and len(context["rids"]) > 1):
            return row
        wanted = {str(rid) for rid in context["rids"]}
        if wanted <= context.get("_message_refs", {}).keys():
            return row
        peer = Peer(**context["peer"])
        acknowledgement = parse(contract(row["method"]).response, row["response"] or b"")
        for attempt in range(2):
            self._ensure_operation_account(account)
            try:
                matches = {}
                async for item in self.iter_history(
                    peer, limit=100, before=acknowledgement.date, route="http"
                ):
                    self._ensure_operation_account(account)
                    if (
                        str(item.rid) in wanted
                        and item.ref.date > 0
                        and (context.get("grouped_id") is None or item.grouped_id == context["grouped_id"])
                    ):
                        matches[str(item.rid)] = {"date": item.ref.date, "seq": item.ref.seq}
            except BaleError:
                matches = {}
            self._ensure_operation_account(account)
            if wanted <= matches.keys():
                await self.store.save_message_refs(account, row["id"], matches)
                self._ensure_operation_account(account)
                return await self.store.operation(account, row["id"])
            if not attempt:
                await asyncio.sleep(0.1)
        # The server ACK remains confirmed. No mutation is resent and no date is guessed.
        raise MessageReferencesUnavailable(row["id"])

    def _operation_result(self, row):
        context = json.loads(row["context"])
        peer = Peer(**context["peer"])
        response = parse(contract(row["method"]).response, row["response"] or b"")
        if context["kind"] == "delete":
            return tuple(context["rids"])
        request = parse(contract(row["method"]).request, row["payload"])
        date = getattr(response, "date", 0) or context.get("date", 0)
        if context["kind"] == "edit":
            date = context.get("date", date)  # ACK mutation time is not a new message identity.
        content = None
        if context["kind"] in ("message", "media"):
            content = request.message
        elif context["kind"] == "edit":
            content = request.updatedMessage
        if content is not None:
            message = message_content(peer, context["rids"][0], date, content)
            if context["kind"] == "edit":
                message.ref = MessageRef(peer, message.rid, date, context.get("seq", 0))
                message.grouped_id = context.get("grouped_id")
                message.author_signature = context.get("author_signature")
                if context.get("quoted") is not None:
                    message.quoted = s.WebQuotedMessage.FromString(bytes.fromhex(context["quoted"]))
            message.rpc_confirmed = bool(context.get("_rpc_confirmed"))
            message.history_verified = bool(context.get("_history_verified"))
            message.operation_id = row["id"]
            return message
        if context["kind"] == "album":
            result = []
            for item in request.multiMedia:
                content = s.WebMessage()
                content.documentMessage.CopyFrom(item.media)
                reference = context["_message_refs"][str(item.randomId)]
                message = message_content(
                    peer, item.randomId, reference["date"], content, grouped_id=request.groupedId
                )
                message.ref = MessageRef(peer, item.randomId, reference["date"], reference["seq"])
                message.rpc_confirmed = bool(context.get("_rpc_confirmed"))
                message.history_verified = bool(context.get("_history_verified"))
                message.operation_id = row["id"]
                result.append(message)
            return Album(tuple(result), request.groupedId, row["id"])
        # Forward content is stored by the server as a nested quote; fetch it with history.
        if context["kind"] == "forward":
            messages = tuple(
                Message(
                    MessageRef(
                        peer,
                        rid,
                        context.get("_message_refs", {}).get(str(rid), {}).get("date", date),
                        context.get("_message_refs", {}).get(str(rid), {}).get("seq", 0),
                    ),
                    grouped_id=context.get("grouped_id"),
                    rpc_confirmed=bool(context.get("_rpc_confirmed")),
                    history_verified=bool(context.get("_history_verified")),
                    operation_id=row["id"],
                )
                for rid in context["rids"]
            )
            if context.get("grouped_id") is not None:
                return Album(messages, context["grouped_id"], row["id"])
            return messages
        return response

    async def _prepare_operation(self, row):
        context = json.loads(row["context"])
        if row["payload"] or "media" not in context:
            return row
        peer = Peer(**context["peer"])
        documents = [None] * len(context["media"])
        indices = iter(range(len(documents)))
        progress = self._progress.get(row["id"])
        progress_lock = asyncio.Lock()

        async def progress_serialized(done, total):
            async with progress_lock:
                await report_progress(progress, done, total)

        async def upload_items():
            for index in indices:
                info = context["media"][index]
                document = await self.media.upload(
                    self, peer, info, progress_serialized if progress else None
                )
                # Only merge this item, never write an older full sibling snapshot.
                # Commit failure retries the DB while retaining the completed upload.
                await self._persist_dispatch(
                    self.store.commit_media_upload,
                    self.account,
                    row["id"],
                    index,
                    sha256=info["sha256"],
                    file_id=info["file_id"],
                    access_hash=info["access_hash"],
                )
                documents[index] = document

        try:
            async with asyncio.TaskGroup() as uploads:
                for _ in range(min(self.config.upload_limit, len(documents))):
                    uploads.create_task(upload_items(), name="fncbale-album-upload")
        except ExceptionGroup as errors:
            error = errors.exceptions[0]
            while isinstance(error, ExceptionGroup):
                error = error.exceptions[0]
            raise error from None
        request = contract(row["method"]).request()
        if context["kind"] == "album":
            request.peer.CopyFrom(wire_peer(peer))
            request.groupedId = context["grouped_id"]
            for rid, doc in zip(context["rids"], documents, strict=True):
                request.multiMedia.add(randomId=rid).media.CopyFrom(doc)
            reply_field = request.repliedMessage
        else:
            request.peer.CopyFrom(short_peer(peer))
            request.rid = context["rids"][0]
            request.message.documentMessage.CopyFrom(documents[0])
            reply_field = request.quotedMessageReference
        if context["reply"]:
            ref = context["reply"]
            self._apply_reply(
                reply_field, MessageRef(Peer(**ref["peer"]), ref["rid"], ref["date"], ref["seq"])
            )
        raw, encoded = request.SerializeToString(), json.dumps(context, ensure_ascii=False)
        await self._persist_dispatch(self.store.commit_media_payload, self.account, row["id"], raw, encoded)
        row["payload"], row["context"] = raw, encoded
        return row

    async def _reconcile_row(self, row):
        account = row["account"]
        self._ensure_operation_account(account)
        context = json.loads(row["context"])
        if context["kind"] not in ("message", "media", "album", "forward", "edit"):
            return False
        peer = Peer(**context["peer"])
        try:
            matches = {}
            async for m in self.iter_history(peer, limit=100, route="http"):
                self._ensure_operation_account(account)
                if m.rid in context["rids"]:
                    matches[m.rid] = m
        except BaleError:
            self._ensure_operation_account(account)
            return False
        self._ensure_operation_account(account)
        if len(matches) != len(context["rids"]):
            return False
        request = parse(contract(row["method"]).request, row["payload"])
        if context["kind"] == "edit":
            actual = s.WebHistory.FromString(matches[context["rids"][0]].raw).message
            if actual.SerializeToString(deterministic=True) != request.updatedMessage.SerializeToString(
                deterministic=True
            ):
                return False
        if context.get("grouped_id") is not None and any(
            m.grouped_id != context["grouped_id"] for m in matches.values()
        ):
            return False
        response = contract(row["method"]).response()
        if hasattr(response, "date"):
            response.date = max(m.ref.date for m in matches.values())
        await self.store.finish(
            account,
            row["id"],
            "confirmed",
            response=response.SerializeToString(),
            basis="history",
            context_patch={
                "_message_refs": {
                    str(rid): {"date": item.ref.date, "seq": item.ref.seq} for rid, item in matches.items()
                }
            },
        )
        return True

    async def reconcile_operation(self, operation_id: str) -> Operation:
        account = self.account
        row = await self.store.operation(account, operation_id)
        self._ensure_operation_account(account)
        if row["status"] != "uncertain":
            return await self.get_operation(operation_id)
        await self.recover()
        self._ensure_operation_account(account)
        await self._reconcile_row(row)
        self._ensure_operation_account(account)
        self._notify_operation(operation_id)
        self._wake.set()
        return await self.get_operation(operation_id)

    async def retry_operation(self, operation_id: str) -> OperationHandle:
        account = self.account
        row = await self.store.operation(account, operation_id)
        self._ensure_operation_account(account)
        if row["status"] == "uncertain" and row["method"] not in self.config.verified_idempotent_methods:
            raise DeliveryUncertain(operation_id)
        if row["status"] not in ("uncertain", "failed"):
            raise BaleError("Only failed or verified-idempotent uncertain operations can be retried")
        if not await self.store.retry(
            account,
            operation_id,
            allow_uncertain=row["method"] in self.config.verified_idempotent_methods,
        ):
            raise BaleError("Operation status changed before retry")
        self._wake.set()
        return OperationHandle(self, operation_id, account=account)

    async def _outbox_worker(self):
        while self._active:
            self._wake.clear()
            try:
                row = await self.store.claim(self.account)
            except (sqlite3.Error, StorageError) as exc:
                self.last_background_error = type(exc).__name__
                await asyncio.sleep(0.5)
                continue
            if row is None:
                try:
                    await asyncio.wait_for(self._wake.wait(), 0.5)
                except TimeoutError:
                    pass
                continue
            call_started = False
            final = True
            try:
                row = await self._prepare_operation(row)
                attempt = await self.store.attempted(self.account, row["id"])
                route = ("websocket", "websocket", "http")[attempt - 1]
                call_started = True
                try:
                    response = await self._call_bytes(row["method"], row["payload"], route)
                    # Validate response before announcing confirmation. A DB failure
                    # after this point retries the commit, never the network write.
                    acknowledgement = parse(contract(row["method"]).response, response)
                    if (
                        row["method"] in ("SendMessage", "SendMultiMediaMessage", "ForwardMessages")
                        and acknowledgement.date <= 0
                    ):
                        raise ProtocolError("Message acknowledgement has no usable date")
                    if row["method"] in ("CreateGroup", "JoinGroup", "JoinPublicGroup"):
                        if not acknowledgement.HasField("group") or not acknowledgement.group.id:
                            raise ProtocolError("Group acknowledgement has no usable identity")
                        if row["method"] == "JoinPublicGroup":
                            requested = parse(contract(row["method"]).request, row["payload"])
                            if acknowledgement.group.id != requested.peer.id:
                                raise ProtocolError("Group acknowledgement belongs to another destination")
                    await self._persist_dispatch(
                        self.store.finish, self.account, row["id"], "confirmed", response=response
                    )
                except RpcError as exc:
                    if exc.code == 8:
                        next_status = await self._persist_dispatch(
                            self.store.reschedule,
                            self.account,
                            row["id"],
                            delay=exc.retry_after if exc.retry_after is not None else 1,
                            account_wait=True,
                            error="rate limited",
                        )
                        final = next_status != "waiting"
                    elif exc.code in (13, 14) or row["ambiguous"]:
                        if not await self._reconcile_row(row):
                            await self._persist_dispatch(
                                self.store.finish,
                                self.account,
                                row["id"],
                                "uncertain",
                                error=f"ambiguous RPC status:{exc.code}",
                            )
                    else:
                        await self._persist_dispatch(
                            self.store.finish, self.account, row["id"], "failed", error=f"RpcError:{exc.code}"
                        )
                except TransportError as exc:
                    if exc.possibly_sent and await self._reconcile_row(row):
                        pass
                    elif exc.possibly_sent and row["method"] not in self.config.verified_idempotent_methods:
                        await self._persist_dispatch(
                            self.store.finish,
                            self.account,
                            row["id"],
                            "uncertain",
                            error="acknowledgement unavailable",
                        )
                    else:
                        next_status = await self._persist_dispatch(
                            self.store.reschedule,
                            self.account,
                            row["id"],
                            delay=0.3 + random.random() * 0.1,
                            ambiguous=exc.possibly_sent,
                            error="transport attempts exhausted"
                            if attempt == 3
                            else "transport retry pending",
                        )
                        final = next_status != "waiting"
                except ProtocolError:
                    if not await self._reconcile_row(row):
                        await self._persist_dispatch(
                            self.store.finish,
                            self.account,
                            row["id"],
                            "uncertain",
                            error="invalid acknowledgement",
                        )
                self._wake.set()
                if final:
                    self._progress.pop(row["id"], None)
            except asyncio.CancelledError:
                # Mark conservatively; recover_operations distinguishes pre-send work.
                raise
            except Exception as exc:
                code = f":{exc.code}" if isinstance(exc, RpcError) else ""
                await self._persist_dispatch(
                    self.store.finish,
                    self.account,
                    row["id"],
                    "uncertain" if call_started or row["ambiguous"] else "failed",
                    error=type(exc).__name__ + code,
                )
                self._progress.pop(row["id"], None)
            finally:
                self._notify_operation(row["id"])

    async def _persist_dispatch(self, callback, *args, **kwargs):
        while self._active:
            try:
                return await callback(*args, **kwargs)
            except (sqlite3.Error, StorageError) as exc:
                self.last_background_error = type(exc).__name__
                await asyncio.sleep(0.5)
        # Leave the in-flight marker for conservative recovery after reconnect.
        raise asyncio.CancelledError

    @staticmethod
    def _route_key(state):
        return str(state.groupPeer.groupId) if state.HasField("groupPeer") else "global"

    async def _ingest(self):
        while self._active:
            raw = await self._ws.updates.get()
            try:
                try:
                    response = parse(r.Response, raw)
                    update = response.ws_update.update.composed_update
                    records = journal_events(update)
                except Exception as exc:
                    self.last_background_error = type(exc).__name__
                    records = [("unknown", "unknown_decode", raw, None)]
                while self._active:
                    try:
                        await self.store.record(self.account, raw, records)
                        break
                    except (sqlite3.Error, BaleError) as exc:
                        # Retain this frame in memory until it can commit, and keep
                        # old route cursors for recovery. Never abandon the consumer.
                        self.last_background_error = type(exc).__name__
                        await self._ws.close()
                        await asyncio.sleep(0.5)
            finally:
                self._ws.updates.task_done()

    def _start_ingest(self):
        self._ingest_task = asyncio.create_task(self._ingest(), name="fncbale-inbox")
        self._tasks.append(self._ingest_task)

    async def recover(self):
        async with self._recovery_lock:
            existing = await self.store.routes(self.account)
            fresh = await self._rpc("GetRoutesStates", contract("GetRoutesStates").request(), route="http")
            known = {row["route"] for row in existing}
            additions = []
            for state in fresh.seqs:
                if self._route_key(state) in known:
                    continue
                initial = s.WebState()
                initial.CopyFrom(state)
                if existing:
                    initial.seq = 0
                additions.append((self._route_key(initial), initial.SerializeToString(), initial.seq))
            if additions:
                await self.store.record(self.account, fresh.SerializeToString(), [], additions)
            if not existing:
                return
            for _ in range(1000):
                states = await self.store.routes(self.account)
                request = contract("GetDiff").request(
                    states=[s.WebState.FromString(row["state"]) for row in states]
                )
                diff = await self._rpc("GetDiff", request, route="http")
                more, progressed = False, False
                old_seq = {row["route"]: row["seq"] for row in states}
                for batch in diff.updates:
                    state = batch.state
                    events = []
                    for update in batch.updates:
                        events.extend(journal_events(update))
                    for new_update in batch.newUpdates:
                        events.extend(journal_events(new_update.update))
                    route = self._route_key(state)
                    if batch.tooLong.value:
                        events.append(("gap:" + route, "gap", b"server history gap", None))
                    await self.store.record(
                        self.account,
                        batch.SerializeToString(),
                        events,
                        [(route, state.SerializeToString(), state.seq)] if batch.HasField("state") else [],
                    )
                    progressed |= state.seq > old_seq.get(route, -1)
                    more |= bool(batch.needMore)
                if not more:
                    break
                if not progressed:
                    raise BaleError("GetDiff requires more but made no checkpoint progress")
            else:
                raise BaleError("GetDiff pagination exceeded safety bound; checkpoints preserved")

    async def _bootstrap_routes(self):
        """Anchor first-session recovery before WS can receive/overflow live updates."""
        if await self.store.routes(self.account):
            return
        fresh = await self._rpc("GetRoutesStates", contract("GetRoutesStates").request(), route="http")
        states = list(fresh.seqs) or [s.WebState(seq=0)]
        await self.store.record(
            self.account,
            fresh.SerializeToString(),
            [],
            [(self._route_key(state), state.SerializeToString(), state.seq) for state in states],
        )

    async def _supervise(self):
        retry = 0.5
        while self._active:
            try:
                try:
                    await asyncio.wait_for(self._ws.disconnected.wait(), self.config.recovery_interval)
                except TimeoutError:
                    pass
                if not self._active:
                    break
                if self._handler_task is not None and self._handler_task.done():
                    previous = self._handler_task
                    if not previous.cancelled():
                        error = previous.exception()
                        self.last_background_error = type(error).__name__ if error else "DispatcherStopped"
                    self.start_handlers()
                if self._ingest_task is not None and self._ingest_task.done():
                    previous = self._ingest_task
                    if not previous.cancelled():
                        error = previous.exception()
                        self.last_background_error = type(error).__name__ if error else "IngestStopped"
                    self._tasks.remove(previous)
                    # Disconnect before recovery so a failed durable consumer
                    # cannot hide behind an otherwise healthy live connection.
                    await self._ws.close()
                    self._start_ingest()
                if not self._ws.connected:
                    await self._ws.connect()
                await self.recover()
                await self.store.maintain(self.config.retention_days)
                retry = 0.5
                self.last_background_error = None
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.last_background_error = type(exc).__name__
                await asyncio.sleep(retry + random.random() * 0.2)
                retry = min(retry * 2, 30)

    async def events(self) -> AsyncIterator[Event]:
        owner = self._claim_event_consumer()
        iterator = self._owned_events(owner)
        try:
            async for event in iterator:
                yield event
        finally:
            await iterator.aclose()
            self._release_event_consumer(owner)

    def _claim_event_consumer(self):
        if self._event_consumer:
            raise BaleError("Choose one durable event consumer per Client")
        owner = object()
        self._event_consumer = owner
        self._inbox_wake = asyncio.Event()
        self._inbox_subscription = (self.account, self._inbox_wake)
        self.store._watch_inbox(*self._inbox_subscription)
        return owner

    def _unsubscribe_inbox(self):
        if self._inbox_subscription is not None:
            account, wake = self._inbox_subscription
            self._inbox_subscription = None
            self.store._unwatch_inbox(account, wake)
            wake.set()

    def _release_event_consumer(self, owner):
        if self._event_consumer is owner:
            self._unsubscribe_inbox()
            self._event_consumer = False
            self._leased_events.clear()

    async def _owned_events(self, owner, *, release_on_close=True):
        account = self.account
        wake = self._inbox_wake
        try:
            while self._active and self._event_consumer is owner and self.account == account:
                # Clear before scanning, so a commit during/after the read remains
                # signaled. Notifications are hints; the durable inbox is truth.
                wake.clear()
                if len(self._leased_events) >= self.config.queue_size:
                    await self._wait_inbox(wake)
                    continue
                rows = await self._persist_dispatch(
                    self.store.pending_events,
                    account,
                    self.config.queue_size - len(self._leased_events),
                    self._leased_events,
                )
                if not rows:
                    await self._wait_inbox(wake)
                    continue
                for row in rows:
                    if not self._active or self._event_consumer is not owner or self.account != account:
                        return
                    self._leased_events.add(row["id"])
                    yield self._decode_event(row)
        finally:
            if release_on_close:
                self._release_event_consumer(owner)

    @staticmethod
    async def _wait_inbox(wake):
        try:
            await asyncio.wait_for(wake.wait(), 0.5)
        except TimeoutError:
            pass  # Periodic safety scan covers changes outside supported writers.

    def _decode_event(self, row):
        account = row.get("account", self.account)
        ack = partial(self._ack_event, account=account)
        if row["kind"] == "gap":
            event = GapEvent(row["id"], "gap", None, row["raw"], _ack=ack)
        elif row["kind"] == "unknown_decode":
            event = UnknownEvent(row["id"], "unknown_decode", None, row["raw"], _ack=ack)
        else:
            decoded = normalize(s.WebUpdate.FromString(row["raw"]), row["id"], ack)
            event = next((item for item in decoded if item.kind == row["kind"]), decoded[0])
        if (
            account == self.account
            and event.peer
            and (cached := self._peer_cache.get(event.peer.key)) is not None
        ):
            event.peer = cached[1]
            if event.message:
                ref = event.message.ref
                event.message.ref = MessageRef(event.peer, ref.rid, ref.date, ref.seq)
        event._handler_failures = row["attempts"]
        return event

    async def _ack_event(self, event_id, *, account=None):
        account = self.account if account is None else account
        await self.store.ack(account, event_id)
        if account == self.account:
            self._leased_events.discard(event_id)
            self._inbox_wake.set()

    def start_handlers(self):
        self._ensure_open()
        if self._handler_task and not self._handler_task.done():
            return self._handler_task
        if self._event_consumer:
            raise BaleError("An explicit event iterator already owns this Client")
        if self._handler_task is not None and self._handler_task in self._tasks:
            self._tasks.remove(self._handler_task)
        owner = self._claim_event_consumer()
        coroutine = self._run_handlers(owner)
        try:
            self._handler_task = asyncio.create_task(coroutine, name="fncbale-dispatcher")
        except BaseException:
            coroutine.close()
            self._release_event_consumer(owner)
            raise

        def completed(task):
            # A task cancelled before its first step never enters the iterator's
            # finally. A late callback may only release its own reservation.
            self._release_event_consumer(owner)
            if not task.cancelled():
                task.exception()

        self._handler_task.add_done_callback(completed)
        self._tasks.append(self._handler_task)
        return self._handler_task

    async def run_handlers(self):
        self._ensure_open()
        if self._event_consumer:
            raise BaleError("Choose one durable event consumer per Client")
        # Direct callers await the same tracked child used by connect/start_handlers.
        # Disconnect can cancel and join its worker cleanup without waiting for the
        # caller's unrelated code after this coroutine returns. Await propagates
        # caller cancellation and TaskGroup failures to the caller normally.
        await self.start_handlers()

    async def _run_handlers(self, owner):
        account = self.account
        # Fixed peer shards preserve per-peer order and bound task/queue counts.
        workers = min(8, self.config.queue_size)
        queues = [asyncio.Queue(max(1, self.config.queue_size // workers)) for _ in range(workers)]

        async def worker(queue):
            while True:
                event = await queue.get()
                try:
                    for scope in tuple(self._conversations):
                        if event.peer and scope.peer.key == event.peer.key and event.kind == "new":
                            await scope._deliver(event)
                    attempts = event._handler_failures
                    while True:
                        if attempts >= self.config.handler_attempts:
                            await self._persist_dispatch(
                                self.store.fail_event,
                                account,
                                event.event_id,
                                self.config.handler_attempts,
                                expected_attempts=attempts,
                            )
                            break
                        try:
                            await self.router.dispatch(event)
                        except (asyncio.CancelledError, Exception) as exc:
                            if (
                                isinstance(exc, asyncio.CancelledError)
                                and asyncio.current_task().cancelling()
                            ):
                                raise
                            result = await self._persist_dispatch(
                                self.store.fail_event,
                                account,
                                event.event_id,
                                self.config.handler_attempts,
                                expected_attempts=attempts,
                            )
                            if result is None or result["status"] != "pending":
                                break
                            attempts = result["attempts"]
                            await asyncio.sleep(0.1)
                        else:
                            # Storage failure is not a user-handler failure. Keep
                            # its lease and retry the ACK without rerunning user code.
                            await self._persist_dispatch(event.ack)
                            break
                    self._leased_events.discard(event.event_id)
                    self._inbox_wake.set()
                finally:
                    queue.task_done()

        async with asyncio.TaskGroup() as group:
            tasks = [group.create_task(worker(queue)) for queue in queues]
            # Keep the handler reservation until its TaskGroup has quiesced,
            # including asynchronous user-handler cleanup after cancellation.
            iterator = self._owned_events(owner, release_on_close=False)
            try:
                async for event in iterator:
                    key = event.peer.key if event.peer else "unknown"
                    index = (
                        int.from_bytes(hashlib.blake2b(key.encode(), digest_size=2).digest(), "big") % workers
                    )
                    await queues[index].put(event)
            finally:
                await iterator.aclose()
                for task in tasks:
                    task.cancel()

    def conversation(self, peer, **kwargs):
        return conversation(self, peer, **kwargs)

    async def replay_event(self, event_id: str) -> bool:
        return bool(await self.store.replay_event(self.account, event_id))

    async def iter_failed_events(
        self, *, limit: int | None = None, page_size: int = 100
    ) -> AsyncIterator[Event]:
        """Inspect account-local quarantine using bounded pages without leasing delivery."""
        if not 1 <= page_size <= 1000 or (limit is not None and limit < 0):
            raise ValueError("Invalid event page size or limit")
        count, after = 0, 0
        account = self.account
        while limit is None or count < limit:
            size = min(page_size, limit - count) if limit is not None else page_size
            if self.account != account:
                return
            rows = await self.store.failed_event_page(account, after=after, limit=size)
            if not rows:
                return
            for row in rows:
                if self.account != account:
                    return
                yield self._decode_event(row)
                count += 1
            after = rows[-1]["position"]
            if len(rows) < size:
                return

    async def download(self, message: Message | MediaInfo, destination: str | Path, **kwargs) -> Path:
        self._ensure_open()
        async with self._download_limit, self.resources.download_limit:
            return await self.media.download(self, message, destination, **kwargs)

    async def download_many(
        self,
        jobs: Iterable[tuple[Message | MediaInfo, str | Path]],
        *,
        expected_sha256: Iterable[str | None] | None = None,
        progress: DownloadProgressCallback | None = None,
    ) -> tuple[Path, ...]:
        """Download up to 100 explicit (Message/MediaInfo, path) jobs with ordered partial results."""
        self._ensure_open()
        jobs = list(itertools.islice(iter(jobs), 101))
        if not 1 <= len(jobs) <= 100:
            raise ValueError("Downloads require 1..100 jobs")
        hashes = (
            [None] * len(jobs)
            if expected_sha256 is None
            else list(itertools.islice(iter(expected_sha256), 101))
        )
        if len(hashes) != len(jobs):
            raise ValueError("Download hash count differs from job count")
        files, targets, identities = [], [], {}
        for index, (message, destination) in enumerate(jobs):
            media = message.media if hasattr(message, "media") else message
            if media is None or media.size < 0:
                raise ValueError("Download has no valid media")
            if not media.file_id or any(
                not isinstance(value, int) or not -(1 << 63) <= value < (1 << 63)
                for value in (media.file_id, media.access_hash)
            ):
                raise ValueError("Invalid download file identity")
            target = Path(destination)
            if hashes[index] is not None:
                if not isinstance(hashes[index], str) or not re.fullmatch(r"[0-9a-fA-F]{64}", hashes[index]):
                    raise ValueError("Invalid download SHA256")
                hashes[index] = hashes[index].lower()
            if media.file_id in identities and identities[media.file_id] != media.access_hash:
                raise ValueError("Conflicting access hashes for one file ID")
            identities[media.file_id] = media.access_hash
            files.append(media)
            targets.append(target)
        # Resolving aliases can perform filesystem I/O. Keep it off the network loop.
        canonical = await disk_call(lambda: [os.path.normcase(str(target.resolve())) for target in targets])
        if len(set(canonical)) != len(canonical):
            raise ValueError("Download destinations must be distinct")
        urls = {}
        unique = list(identities.items())
        for offset in range(0, len(unique), 10):
            request = contract("GetNasimFileUrls").request()
            selected = dict(unique[offset : offset + 10])
            for file_id, access_hash in selected.items():
                request.files.add(fileId=file_id, accessHash=access_hash)
            try:
                allocated = await self._rpc("GetNasimFileUrls", request)
            except RpcError as exc:
                if exc.code not in (12, 404, 501):
                    raise
                break  # Unsupported batch endpoint: use verified singular allocation.
            except TransportError:
                break
            ambiguous = set()
            for item in allocated.fileUrls:
                if item.fileId not in selected or not item.url:
                    continue
                if item.fileId in urls and urls[item.fileId] != item.url:
                    ambiguous.add(item.fileId)
                urls[item.fileId] = item.url
            for file_id in ambiguous:
                urls.pop(file_id, None)
        results = [None] * len(jobs)
        indices = iter(range(len(jobs)))
        progress_lock = asyncio.Lock()

        async def worker():
            for index in indices:

                async def update(done, total, index=index):
                    async with progress_lock:
                        result = progress(index, done, total)
                        if hasattr(result, "__await__"):
                            await result

                try:
                    path = await self.download(
                        files[index],
                        targets[index],
                        progress=update if progress else None,
                        expected_sha256=hashes[index],
                        _url=urls.get(files[index].file_id),
                    )
                    results[index] = DownloadResult(index, path, True)
                except asyncio.CancelledError:
                    if asyncio.current_task().cancelling():
                        raise
                    results[index] = DownloadResult(index, targets[index], False, "CancelledError")
                except Exception as exc:
                    results[index] = DownloadResult(index, targets[index], False, type(exc).__name__)

        async with asyncio.TaskGroup() as group:
            for _ in range(min(self.config.download_limit, len(jobs))):
                group.create_task(worker())
        if not all(item.completed for item in results):
            raise BatchDownloadError(results) from None
        return tuple(item.destination for item in results)

    async def download_album(self, album: Album, directory: str | Path, **kwargs) -> tuple[Path, ...]:
        """Download items in album order to index/RID filenames, never server-supplied paths."""
        jobs = []
        for index, message in enumerate(album.messages):
            if message.media is None:
                raise ValueError("Album item has no media")
            extension = Path(message.media.filename).suffix
            if not re.fullmatch(r"\.[a-zA-Z0-9]{1,10}", extension):
                extension = ".bin"
            jobs.append((message, Path(directory) / f"{index + 1:02d}-{message.rid}{extension}"))
        return await self.download_many(jobs, **kwargs)

    async def get_album(self, peer: PeerInput, grouped_id: int, *, include_deleted: bool = False) -> Album:
        """Latest durable received album snapshot; server does not announce a total count."""
        peer = await self.resolve_peer(peer)

        def load(db):
            return [
                dict(row)
                for row in db.execute(
                    "SELECT * FROM album_items WHERE account=? AND peer=? AND grouped=? ORDER BY date,rowid",
                    (self.account, peer.key, grouped_id),
                )
                if include_deleted or not row["deleted"]
            ]

        rows = await self.store.run(load, write=False)
        items = []
        for row in rows:
            message = normalize(s.WebUpdate.FromString(row["raw"]))[0].message
            message.ref = MessageRef(peer, message.rid, message.ref.date, message.ref.seq)
            items.append(message)
        return Album(tuple(items), grouped_id)

    async def iter_albums(self, peer: PeerInput, *, limit: int = 100) -> AsyncIterator[Album]:
        """Group a bounded history window, restoring its reverse server order."""
        self._ensure_open()
        account = self.account
        groups = {}
        async for message in self.iter_history(peer, limit=limit):
            if not self._stream_is_current(account):
                return
            if message.grouped_id:
                groups.setdefault(message.grouped_id, []).append(message)
        for group, messages in groups.items():
            if not self._stream_is_current(account):
                return
            yield Album(tuple(reversed(messages)), group)

    async def get_member_page(
        self, peer: PeerInput, *, cursor: bytes = b"", page_size: int = 100
    ) -> MemberPage:
        self._ensure_open()
        if not isinstance(cursor, bytes) or not 1 <= page_size <= 100:
            raise ValueError("Member cursor must be bytes and page_size must be 1..100")
        peer = await self.resolve_peer(peer)
        if peer.kind == PeerKind.USER:
            raise ValueError("Members require a group or channel")
        request = contract("LoadMembers").request(limit=page_size)
        request.group.groupId, request.group.accessHash = peer.id, peer.access_hash
        if cursor:
            request.next.value = cursor
        response = await self._rpc("LoadMembers", request)
        return MemberPage(
            peer, tuple(response.members), cursor, bytes(response.next.value), response.SerializeToString()
        )

    async def iter_members(
        self, peer: PeerInput, *, page_size: int = 100, cursor: bytes = b"", limit: int | None = None
    ) -> AsyncIterator[s.WebMember]:
        self._ensure_open()
        account = self.account
        if not isinstance(cursor, bytes) or not 1 <= page_size <= 100 or (limit is not None and limit < 0):
            raise ValueError("Invalid member cursor, page size or limit")
        if limit == 0:
            return
        peer = await self.resolve_peer(peer)
        seen, cursors, count = set(), {cursor} if cursor else set(), 0
        while True:
            if not self._stream_is_current(account):
                return
            page = await self.get_member_page(peer, cursor=cursor, page_size=page_size)
            for member in page.members:
                if not self._stream_is_current(account):
                    return
                if member.uid not in seen:
                    seen.add(member.uid)
                    yield member
                    count += 1
                    if limit is not None and count >= limit:
                        return
            if not self._stream_is_current(account):
                return
            next_cursor = page.next_cursor
            if not next_cursor:
                break
            if next_cursor in cursors:
                raise BaleError("Member cursor did not advance")
            cursors.add(next_cursor)
            cursor = next_cursor

    async def member_count(self, peer: PeerInput, *, source: Literal["auto", "full"] = "auto") -> int:
        """Read a compact count; ambiguous scalar zero uses presence-aware full state."""
        self._ensure_open()
        if source not in ("auto", "full"):
            raise ValueError("Member count source must be auto or full")
        peer = await self.resolve_peer(peer)
        if peer.kind == PeerKind.USER:
            raise ValueError("Member counts require a group or channel")
        if source == "auto":
            request = contract("GetGroupMembersCount").request()
            request.group.groupId, request.group.accessHash = peer.id, peer.access_hash
            try:
                response = await self._rpc("GetGroupMembersCount", request)
            except RpcError as exc:
                # Only the verified UNIMPLEMENTED status permits changing methods.
                # Auth, permission, validation and exhausted read budgets propagate.
                if exc.code != 12:
                    raise
            else:
                if response.membersCount < 0:
                    raise ProtocolError("Dedicated group response has a negative member count")
                if response.membersCount > 0:
                    return response.membersCount
                # Scalar proto3 zero has no presence. Preserve the existing API's
                # absent-vs-explicit-zero distinction rather than inventing a count.
        full = await self.get_full_group(peer)
        if not full.HasField("membersCount") or full.membersCount.value < 0:
            raise ProtocolError("Group response has no valid member count")
        return full.membersCount.value

    async def get_views(
        self, peer: PeerInput, messages: Iterable[Message | MessageRef], *, increment: bool = False
    ) -> r.WebGetMessagesViewsResponse:
        peer = await self.resolve_peer(peer)
        request = contract("GetMessagesViews").request(increment=increment)
        request.peer.CopyFrom(short_peer(peer))
        for message in messages:
            ref = message.ref if isinstance(message, Message) else message
            if not isinstance(ref, MessageRef) or ref.peer.key != peer.key:
                raise ValueError("View references must belong to the requested peer")
            request.mids.add(date=ref.date, rid=ref.rid, seq=ref.seq)
        if not request.mids:
            return contract("GetMessagesViews").response()
        if increment:
            context = {"kind": "action", "peer": peer_dict(peer), "rids": []}
            return await (await self._enqueue(peer, "GetMessagesViews", request, context)).wait()
        return await self._rpc("GetMessagesViews", request, readonly=True)

    async def iter_views(
        self,
        peer: PeerInput,
        messages: Iterable[Message | MessageRef],
        *,
        batch_size: int = 100,
    ) -> AsyncIterator[MessageViews]:
        """Read counts in bounded batches, preserving input order and explicit unknowns."""
        self._ensure_open()
        account = self.account
        if not 1 <= batch_size <= 100:
            raise ValueError("View batch_size must be 1..100")
        peer = await self.resolve_peer(peer)
        source = iter(messages)
        while self._stream_is_current(account):
            batch = list(itertools.islice(source, batch_size))
            if not batch or not self._stream_is_current(account):
                return
            refs, unique = [], {}
            for message in batch:
                ref = message.ref if isinstance(message, Message) else message
                if not isinstance(ref, MessageRef) or ref.peer.key != peer.key:
                    raise ValueError("View references must belong to the requested peer")
                if (
                    any(
                        not isinstance(value, int) or isinstance(value, bool) or not 0 < value < (1 << 63)
                        for value in (ref.rid, ref.date)
                    )
                    or not isinstance(ref.seq, int)
                    or isinstance(ref.seq, bool)
                    or not 0 <= ref.seq < (1 << 31)
                ):
                    raise ValueError("Invalid view message identity")
                refs.append(ref)
                unique.setdefault((ref.rid, ref.date, ref.seq), ref)
            response = await self.get_views(peer, unique.values(), increment=False)
            if not self._stream_is_current(account):
                return
            candidates = {}
            for container in response.containers:
                if not container.HasField("mId"):
                    continue
                identity = (container.mId.rid, container.mId.date)
                candidates.setdefault(identity, []).append(container)
            values = {}
            for key, ref in unique.items():
                matches = [
                    item
                    for item in candidates.get((ref.rid, ref.date), ())
                    if not ref.seq or item.mId.seq == ref.seq
                ]
                if not matches:
                    values[key] = MessageViews(ref, None)
                    continue
                raw = matches[0].SerializeToString()
                count = matches[0].views.value if matches[0].HasField("views") else None
                if count is not None and count < 0:
                    raise ProtocolError("Message view count is negative")
                for item in matches[1:]:
                    other = item.views.value if item.HasField("views") else None
                    if other != count:
                        raise ProtocolError("Conflicting view counts for one message identity")
                values[key] = MessageViews(ref, count, raw)
            for ref in refs:
                if not self._stream_is_current(account):
                    return
                value = values[(ref.rid, ref.date, ref.seq)]
                yield MessageViews(ref, value.count, value.raw)

    async def iter_search(
        self, peer: PeerInput, text: str, *, limit: int | None = None
    ) -> AsyncIterator[s.WebSearchResult]:
        self._ensure_open()
        account = self.account
        if limit is not None and limit < 0:
            raise ValueError("limit must be nonnegative or None")
        if limit == 0:
            return
        peer = await self.resolve_peer(peer)
        request = contract("SearchMessages").request()
        # Query alternatives are combined through an explicit AND node, as in the web contract.
        conditions = request.query.searchAndCondition.andQuery
        conditions.add().searchPeerCondition.peer.CopyFrom(short_peer(peer))
        conditions.add().searchPieceText.query = text.encode()
        count, cursor, cursors = 0, b"", set()
        while True:
            if not self._stream_is_current(account):
                return
            response = await self._rpc("SearchMessages" if not cursor else "SearchMessageMore", request)
            # The current service returns an opaque state even on an exhausted page.
            # Reusing that empty-page state is rejected by the server (code 7).
            if not response.searchResults:
                return
            for result in response.searchResults:
                if not self._stream_is_current(account):
                    return
                yield result
                count += 1
                if limit is not None and count >= limit:
                    return
            if not self._stream_is_current(account):
                return
            next_cursor = bytes(response.loadMoreState.value)
            if not next_cursor:
                return
            if next_cursor in cursors:
                raise BaleError("Search cursor did not advance")
            cursors.add(next_cursor)
            cursor = next_cursor
            more = contract("SearchMessageMore").request()
            more.query.CopyFrom(request.query)
            more.loadMoreState.value = cursor
            request = more

    async def get_contacts(self) -> r.WebGetContactsResponse:
        return await self._rpc("GetContacts", contract("GetContacts").request())

    async def iter_search_messages(
        self, peer: PeerInput, text: str, *, limit: int | None = None
    ) -> AsyncIterator[Message]:
        """Typed indexed snapshots; preserve full media, quotes, sequence and album data."""
        self._ensure_open()
        account = self.account
        peer = await self.resolve_peer(peer)
        history_window = {}
        async for result in self.iter_search(peer, text, limit=limit):
            if not self._stream_is_current(account):
                return
            value = result.result
            if not value.HasField("peer") or value.peer.id != peer.id or value.peer.type != peer.wire_type:
                raise ProtocolError("Search result belongs to an unexpected peer")
            if value.HasField("messageContainer"):
                container = value.messageContainer
                if container.rid != value.rid or container.date != value.date:
                    raise ProtocolError("Search container identity disagrees with its result")
            else:
                container = None
            if container is not None and container.HasField("message") and container.message.ByteSize():
                message = message_from_history(peer, container)
            else:
                # Current search often returns only an indexed caption rendered as
                # text, even for photos/videos. That projection is not a full message.
                identity = (value.rid, value.date)
                if identity not in history_window:
                    history_window = {
                        (m.rid, m.ref.date): m
                        async for m in self.iter_history(peer, limit=100, before=value.date)
                    }
                if not self._stream_is_current(account):
                    return
                message = history_window.get(identity)
                if message is None:
                    raise SearchSnapshotUnavailable(MessageRef(peer, value.rid, value.date))
            message.history_verified = True
            yield message

    async def get_full_user(self, peer: PeerInput) -> r.WebGetFullUserResponse:
        peer = await self.resolve_peer(peer, kind=PeerKind.USER if isinstance(peer, int) else None)
        if peer.kind != PeerKind.USER:
            raise ValueError("Full user requires a user peer")
        request = contract("GetFullUser").request()
        request.peer.uid, request.peer.accessHash = peer.id, peer.access_hash
        return await self._rpc("GetFullUser", request)

    async def get_dialogs(self, *, before: int = -1, limit: int = 100) -> r.WebLoadDialogsResponse:
        if not 1 <= limit <= 100:
            raise ValueError("Dialog limit must be 1..100")
        return await self._rpc("LoadDialogs", contract("LoadDialogs").request(minDate=before, limit=limit))

    async def enqueue_account_action(self, method, request, *, idempotency_key=None) -> OperationHandle:
        """Durable typed group/profile operations from the curated capability registry."""
        allowed = {
            "CreateGroup",
            "EditChannelNick",
            "SetRestriction",
            "EditGroupAbout",
            "EditGroupTitle",
            "InviteUser",
            "JoinGroup",
            "JoinPublicGroup",
            "KickUser",
            "LeaveGroup",
            "EditAbout",
            "EditName",
            "EditNickName",
        }
        if method not in allowed or not isinstance(request, contract(method).request):
            raise ValueError("Unsupported action or wrong typed request")
        if self.session is None:
            raise AuthenticationError("No account session")
        # Freeze a copy; never mutate a caller's reusable typed request. The
        # caller intent excludes an automatically assigned nonce so idem replay
        # resolves the original committed operation instead of conflicting.
        intent = {"method": method, "payload": request.SerializeToString().hex()}
        frozen = type(request)()
        frozen.CopyFrom(request)
        request = frozen
        rids = []
        for field in ("rid", "randomId"):
            if field in request.DESCRIPTOR.fields_by_name:
                if not getattr(request, field):
                    setattr(request, field, new_rid())
                rids.append(getattr(request, field))
        peer = Peer(PeerKind.USER, self.session.user_id)
        for field in ("groupPeer", "groupOutPeer", "group", "peer"):
            if hasattr(request, field) and request.HasField(field):
                target = getattr(request, field)
                if hasattr(target, "groupId"):
                    peer = self._peer_cache.get(
                        f"2:{target.groupId}", (0, Peer(PeerKind.GROUP, target.groupId))
                    )[1]
                elif hasattr(target, "id") and hasattr(target, "type"):
                    peer = Peer(PeerKind.USER if target.type == 1 else PeerKind.GROUP, target.id)
                break
        context = {"kind": "action", "peer": peer_dict(peer), "rids": rids}

        def invalidate_identity():
            if method in ("EditAbout", "EditName", "EditNickName", "SetRestriction"):
                self._peer_cache.discard(peer.key)

        try:
            handle = await self._enqueue(
                peer, method, request, context, idempotency_key=idempotency_key, intent=intent
            )
        except asyncio.CancelledError:
            # Cancellation cannot prove the store did not accept/commit. A raw
            # typed action must invalidate self aliases just like its builder.
            invalidate_identity()
            raise
        else:
            invalidate_identity()
            return handle

    async def account_action(self, method, request, *, idempotency_key=None):
        return await (
            await self.enqueue_account_action(method, request, idempotency_key=idempotency_key)
        ).wait()

    async def _enqueue_profile_action(self, method, value, *, idempotency_key):
        self._ensure_open()
        if value is not None and not isinstance(value, str):
            raise TypeError("Profile value must be a string or None")
        request = contract(method).request()
        if method == "EditName":
            if value is None or not value.strip():
                raise ValueError("Profile name must not be empty")
            request.name = value
        elif value is not None:
            if method == "EditNickName":
                value = value.removeprefix("@")
                if any(character.isspace() for character in value):
                    raise ValueError("Profile username must not contain whitespace")
            getattr(request, "about" if method == "EditAbout" else "nickname").value = value
        return await self.enqueue_account_action(method, request, idempotency_key=idempotency_key)

    async def enqueue_edit_profile_name(
        self, name: str, *, idempotency_key: str | None = None
    ) -> OperationHandle:
        return await self._enqueue_profile_action("EditName", name, idempotency_key=idempotency_key)

    async def enqueue_edit_profile_about(
        self, about: str | None, *, idempotency_key: str | None = None
    ) -> OperationHandle:
        return await self._enqueue_profile_action("EditAbout", about, idempotency_key=idempotency_key)

    async def enqueue_edit_profile_username(
        self, username: str | None, *, idempotency_key: str | None = None
    ) -> OperationHandle:
        return await self._enqueue_profile_action("EditNickName", username, idempotency_key=idempotency_key)

    async def edit_profile_name(
        self, name: str, *, idempotency_key: str | None = None
    ) -> r.WebEditNameResponse:
        return await (await self.enqueue_edit_profile_name(name, idempotency_key=idempotency_key)).wait()

    async def edit_profile_about(
        self, about: str | None, *, idempotency_key: str | None = None
    ) -> r.WebEditAboutResponse:
        return await (await self.enqueue_edit_profile_about(about, idempotency_key=idempotency_key)).wait()

    async def edit_profile_username(
        self, username: str | None, *, idempotency_key: str | None = None
    ) -> r.WebEditNickNameResponse:
        return await (
            await self.enqueue_edit_profile_username(username, idempotency_key=idempotency_key)
        ).wait()

    async def create_group(
        self,
        title: str,
        *,
        members: Iterable[PeerInput] = (),
        channel: bool = False,
        username: str | None = None,
        idempotency_key: str | None = None,
    ) -> Peer:
        self._ensure_open()
        if not title.strip():
            raise ValueError("Group/channel title must not be empty")
        request = contract("CreateGroup").request(title=title, groupType=int(channel))
        if username is not None:
            if not isinstance(username, str):
                raise TypeError("Username must be a string or None")
            nickname = username.removeprefix("@")
            if nickname:
                if any(character.isspace() for character in nickname):
                    raise ValueError("Username must not contain whitespace")
                request.restriction = 1  # Captured official RESTRICTION_PUBLIC.
            request.nick.value = nickname
        for member in members:
            member = await self.resolve_peer(member)
            if member.kind != PeerKind.USER:
                raise ValueError("Group members must be user peers")
            request.users.add(uid=member.id, accessHash=member.access_hash)
        response = await self.account_action("CreateGroup", request, idempotency_key=idempotency_key)
        if not response.HasField("group") or not response.group.id:
            raise ProtocolError("CreateGroup acknowledgement has no group identity")
        peer = self._cache_peer(self._group_peer(response.group))
        if response.notAddedUserPeers:
            raise GroupCreationIncomplete(peer, [user.uid for user in response.notAddedUserPeers])
        return peer

    async def create_channel(
        self,
        title: str,
        *,
        username: str | None = None,
        idempotency_key: str | None = None,
    ) -> Peer:
        return await self.create_group(
            title, channel=True, username=username, idempotency_key=idempotency_key
        )

    async def _group_request(self, method: str, peer: PeerInput):
        self._ensure_open()
        peer = await self.resolve_peer(peer)
        if peer.kind == PeerKind.USER:
            raise ValueError("Operation requires a group or channel peer")
        request = contract(method).request()
        request.groupPeer.groupId, request.groupPeer.accessHash = peer.id, peer.access_hash
        return peer, request

    async def edit_group_title(
        self,
        peer: PeerInput,
        title: str,
        *,
        idempotency_key: str | None = None,
    ) -> Peer:
        if not title.strip():
            raise ValueError("Group/channel title must not be empty")
        peer, request = await self._group_request("EditGroupTitle", peer)
        request.title = title
        await self.account_action("EditGroupTitle", request, idempotency_key=idempotency_key)
        return self._cache_peer(replace(peer, title=title))

    async def edit_group_about(
        self,
        peer: PeerInput,
        about: str | None,
        *,
        idempotency_key: str | None = None,
    ) -> None:
        peer, request = await self._group_request("EditGroupAbout", peer)
        if about is not None:
            request.about.value = about
        await self.account_action("EditGroupAbout", request, idempotency_key=idempotency_key)

    async def edit_channel_username(
        self,
        peer: PeerInput,
        username: str,
        *,
        idempotency_key: str | None = None,
    ) -> Peer:
        peer, request = await self._group_request("EditChannelNick", peer)
        if peer.kind != PeerKind.CHANNEL:
            raise ValueError("Channel username requires a channel peer")
        request.nick = username.removeprefix("@")
        await self.account_action("EditChannelNick", request, idempotency_key=idempotency_key)
        self._peer_cache.discard(peer.key)
        return self._cache_peer(replace(peer, username=request.nick or None))

    async def set_group_visibility(
        self,
        peer: PeerInput,
        *,
        public: bool,
        username: str | None = None,
        idempotency_key: str | None = None,
    ) -> Peer:
        """Explicit visibility change; setting a nickname alone never promotes privacy."""
        self._ensure_open()
        if not isinstance(public, bool):
            raise TypeError("public must be a bool")
        if public:
            if not isinstance(username, str) or not username.removeprefix("@").strip():
                raise ValueError("Public visibility requires an explicit username")
            username = username.removeprefix("@")
            if any(character.isspace() for character in username):
                raise ValueError("Username must not contain whitespace")
        elif username is not None:
            raise ValueError("Private visibility must not specify a public username")
        peer = await self.resolve_peer(peer)
        if peer.kind == PeerKind.USER:
            raise ValueError("Visibility requires a group or channel peer")
        request = contract("SetRestriction").request(restriction=int(public))
        request.groupOutPeer.groupId, request.groupOutPeer.accessHash = peer.id, peer.access_hash
        request.nick.value = username if public else ""
        await self.account_action("SetRestriction", request, idempotency_key=idempotency_key)
        self._peer_cache.discard(peer.key)
        return self._cache_peer(replace(peer, username=username if public else None))

    async def join_group(self, invite_token: str, *, idempotency_key: str | None = None) -> Peer:
        self._ensure_open()
        if not isinstance(invite_token, str):
            raise TypeError("Invite token must be a string")
        if not invite_token or any(character.isspace() for character in invite_token):
            raise ValueError("Provide an invite token without whitespace")
        request = contract("JoinGroup").request(token=invite_token)
        response = await self.account_action("JoinGroup", request, idempotency_key=idempotency_key)
        if not response.HasField("group") or not response.group.id:
            raise ProtocolError("JoinGroup acknowledgement has no group identity")
        return self._cache_peer(self._group_peer(response.group))

    async def join_public_group(self, peer: PeerInput, *, idempotency_key: str | None = None) -> Peer:
        """Join by public peer; this is distinct from private invite-token joining."""
        self._ensure_open()
        peer = await self.resolve_peer(peer)
        if peer.kind == PeerKind.USER:
            raise ValueError("Public membership requires a group or channel peer")
        request = contract("JoinPublicGroup").request()
        request.peer.type, request.peer.id = peer.wire_type, peer.id
        response = await self.account_action("JoinPublicGroup", request, idempotency_key=idempotency_key)
        if not response.HasField("group") or response.group.id != peer.id:
            raise ProtocolError("JoinPublicGroup acknowledgement has an unexpected group identity")
        return self._cache_peer(self._group_peer(response.group))

    async def get_group_invite_url(self, peer: PeerInput) -> str:
        """Read the current invite URL; the caller must treat it as private data."""
        _, request = await self._group_request("GetGroupInviteURL", peer)
        response = await self._rpc("GetGroupInviteURL", request)
        if not response.url:
            raise ProtocolError("GetGroupInviteURL returned no URL")
        return response.url

    async def leave_group(
        self,
        peer: PeerInput,
        *,
        make_orphan: bool = False,
        idempotency_key: str | None = None,
    ) -> None:
        peer, request = await self._group_request("LeaveGroup", peer)
        request.makeOrphan.value = make_orphan
        await self.account_action("LeaveGroup", request, idempotency_key=idempotency_key)
        self._peer_cache.discard(peer.key)

    async def _membership_action(self, method, peer, user, *, idempotency_key):
        peer, request = await self._group_request(method, peer)
        user = await self.resolve_peer(user)
        if user.kind != PeerKind.USER:
            raise ValueError("Membership changes require a user peer")
        request.user.uid, request.user.accessHash = user.id, user.access_hash
        await self.account_action(method, request, idempotency_key=idempotency_key)

    async def invite_user(
        self,
        peer: PeerInput,
        user: PeerInput,
        *,
        idempotency_key: str | None = None,
    ) -> None:
        await self._membership_action("InviteUser", peer, user, idempotency_key=idempotency_key)

    async def kick_user(
        self,
        peer: PeerInput,
        user: PeerInput,
        *,
        idempotency_key: str | None = None,
    ) -> None:
        await self._membership_action("KickUser", peer, user, idempotency_key=idempotency_key)
