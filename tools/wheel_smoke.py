"""Run under a clean wheel environment: synthetic data, no network or Bale SDK."""

import asyncio
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import tempfile

from fncbale import Client, Media, MediaKind, Session, __version__
from fncbale import Conversation, ConversationClosed, HistoryPaginationGap, Peer, PeerKind
from fncbale.errors import ClientClosed
import fncbale
from fncbale.proto.struct_pb2 import WebUpdate, WebSearchResult
from fncbale.events import journal_events
from PIL import Image


async def media_account_boundary(root):
    from fncbale.errors import BaleError

    client = Client(Session(1, "synthetic"), data_dir=root)
    client.account, client._active = "original", True
    entered, release = asyncio.Event(), asyncio.Event()
    prepare = client.media.prepare

    async def paused_prepare(media):
        info = await prepare(media)
        entered.set()
        await release.wait()
        return info

    client.media.prepare = paused_prepare
    task = asyncio.create_task(client.enqueue_media(Peer(PeerKind.USER, 7), Media(b"original content")))
    try:
        await asyncio.wait_for(entered.wait(), 3)
        client.account = "replacement"
        release.set()
        try:
            await task
        except BaleError:
            pass
        else:
            raise AssertionError("Media preparation crossed an account boundary")
        assert not await client.store.operation_page("replacement")
        assert not await client.store.operation_page("original")
        assert not list((root / "spool").glob("*.media"))
        assert not client.media.in_use
    finally:
        release.set()
        await asyncio.gather(task, return_exceptions=True)
        await client.close()


async def main():
    assert Path(fncbale.__file__).is_relative_to(Path(sys.prefix)), "Use a clean wheel environment"
    from fncbale import Config, contract

    cache_client = Client(
        Session(1, "synthetic"),
        data_dir=Path(tempfile.gettempdir()) / "unused-cache-smoke",
        config=Config(peer_cache_size=2),
    )
    try:
        old_peer = cache_client._cache_peer(Peer(PeerKind.CHANNEL, 10, 11, username="old"))
        from dataclasses import replace

        refreshed = cache_client._cache_peer(replace(old_peer, username="new", access_hash=22))
        assert "@old" not in cache_client._peer_cache
        assert await cache_client.resolve_peer(10) == refreshed
        cache_client._cache_peer(Peer(PeerKind.USER, 20, username="second"))
        assert await cache_client.resolve_peer("@new") == refreshed
        cache_client._cache_peer(Peer(PeerKind.USER, 30, username="third"))
        assert "1:20" not in cache_client._peer_cache and "@second" not in cache_client._peer_cache
        assert cache_client._peer_cache.peer_count == 2
        cache_client.media._metadata_cache["synthetic"] = {}
    finally:
        await cache_client.close()
    assert not cache_client._peer_cache and not cache_client.media._metadata_cache

    import httpx
    from fncbale.errors import TransportError
    from fncbale.protocol import grpc_frame
    from fncbale.transports import GrpcTransport, WebSocketTransport

    for exception, ambiguous in (
        (httpx.ConnectTimeout, False),
        (httpx.PoolTimeout, False),
        (httpx.ReadTimeout, True),
        (httpx.WriteTimeout, True),
    ):

        def failure(request, error_type=exception):
            raise error_type("synthetic phase failure", request=request)

        async with httpx.AsyncClient(transport=httpx.MockTransport(failure)) as http:
            transport = GrpcTransport("synthetic", Config(), http)
            try:
                await transport.request("s", "write", b"frozen")
            except TransportError as exc:
                assert exc.possibly_sent is ambiguous
            else:
                raise AssertionError("Phase failure must preserve delivery ambiguity")

    calls = []

    def redirect(request):
        calls.append(request)
        return httpx.Response(
            307, headers={"grpc-status": "0", "location": "/again"}, content=grpc_frame(b"false-success")
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(redirect), follow_redirects=True) as http:
        transport = GrpcTransport("synthetic", Config(), http)
        try:
            await transport.request("s", "write", b"frozen")
        except TransportError as exc:
            assert exc.possibly_sent and len(calls) == 1
        else:
            raise AssertionError("Redirect cannot confirm/replay an RPC")

    async def blocked_headers(request):
        await asyncio.Event().wait()

    async with httpx.AsyncClient(transport=httpx.MockTransport(blocked_headers), timeout=None) as http:
        transport = GrpcTransport("synthetic", Config(rpc_timeout=0.03), http)
        async with asyncio.timeout(1):
            try:
                await transport.request("s", "write", b"frozen")
            except TransportError as exc:
                assert exc.possibly_sent
            else:
                raise AssertionError("Header wait must have a deadline")

    class BlockedSocket:
        closed = False

        async def send(self, raw):
            await asyncio.Event().wait()

        async def close(self):
            self.closed = True

    for partial in (False, True):
        ws = WebSocketTransport("synthetic", Config(rpc_timeout=0.03))
        ws.socket = socket = BlockedSocket()
        if not partial:
            await ws._send_lock.acquire()
        try:
            async with asyncio.timeout(1):
                try:
                    await ws.request("s", "write", b"frozen")
                except TransportError as exc:
                    assert exc.possibly_sent is partial
                else:
                    raise AssertionError("Send/lock wait must have a deadline")
            assert ws.pending_count == 0 and socket.closed is partial
        finally:
            if ws._send_lock.locked():
                ws._send_lock.release()
            await ws.close()

    for value in (1.5, float("nan"), float("inf"), True):
        try:
            Config(global_rpc_limit=value)
        except (TypeError, ValueError):
            pass
        else:
            raise AssertionError("Invalid count cannot create an unbounded semaphore")
    mutable = {"CallerVerifiedMethod"}
    frozen = Config(verified_idempotent_methods=mutable)
    mutable.add("SendMessage")
    assert frozen.verified_idempotent_methods == frozenset({"CallerVerifiedMethod"})
    with tempfile.TemporaryDirectory(prefix="fncbale-wheel-") as directory:
        root = Path(directory).resolve()
        assert root.parent == Path(tempfile.gettempdir()).resolve()
        assert root.name.startswith("fncbale-wheel-")
        ownership = Client(Session(1, "synthetic"), data_dir=root / "consumer-ownership")
        ownership.account, ownership._active = "original", True
        first, second = None, None
        rejected = ownership.events()
        try:
            from fncbale.errors import BaleError

            handler_task = ownership.start_handlers()
            try:
                await anext(rejected)
            except BaleError:
                pass
            else:
                raise AssertionError("Explicit iterator overtook reserved handler")
            handler_task.cancel()
            await asyncio.gather(handler_task, return_exceptions=True)
            assert not ownership._event_consumer
            update = WebUpdate()
            update.message.peer.type, update.message.peer.id = 1, 10
            update.message.rid, update.message.date = 1, 1
            raw = update.SerializeToString()
            original_id = (await ownership.store.record("original", raw, journal_events(update)))[0]
            first = ownership.events()
            old_event = await anext(first)
            await ownership.disconnect()
            ownership.account, ownership._active = "next", True
            next_id = (await ownership.store.record("next", raw, journal_events(update)))[0]
            second = ownership.events()
            next_event = await anext(second)
            assert next_event.event_id == next_id
            await old_event.ack()
            await first.aclose()
            assert next_id in ownership._leased_events and ownership._event_consumer
            statuses = await ownership.store.run(
                lambda db: {row["id"]: row["status"] for row in db.execute("SELECT id,status FROM inbox")},
                write=False,
            )
            assert statuses == {original_id: "acked", next_id: "pending"}
            await next_event.ack()
        finally:
            await rejected.aclose()
            if first is not None:
                await first.aclose()
            if second is not None:
                await second.aclose()
            await ownership.close()
        direct = Client(Session(1, "synthetic"), data_dir=root / "direct-handler")
        direct.account, direct._active = "a", True
        entered, cleaning, finish = asyncio.Event(), asyncio.Event(), asyncio.Event()

        @direct.router.on("new")
        async def held_handler(event):
            entered.set()
            try:
                await asyncio.Event().wait()
            finally:
                cleaning.set()
                await finish.wait()

        caller, stopping, interrupted, joined = None, None, None, None
        socket_entered, socket_release = asyncio.Event(), asyncio.Event()
        close_calls = []
        try:
            event_id = (await direct.store.record("a", raw, journal_events(update)))[0]
            caller = asyncio.create_task(direct.run_handlers())
            await asyncio.wait_for(entered.wait(), 2)
            assert direct._handler_task is not caller and direct._handler_task in direct._tasks
            stopping = asyncio.create_task(direct.disconnect())
            await asyncio.wait_for(cleaning.wait(), 2)
            assert not stopping.done() and direct._event_consumer
            finish.set()
            await asyncio.wait_for(stopping, 2)
            await asyncio.gather(caller, return_exceptions=True)
            assert not direct._event_consumer
            rows = await direct.store.pending_events("a")
            assert len(rows) == 1 and rows[0]["id"] == event_id

            class HeldSocket:
                async def close(self):
                    close_calls.append(True)
                    socket_entered.set()
                    await socket_release.wait()

            direct._ws = HeldSocket()
            interrupted = asyncio.create_task(direct.disconnect())
            await asyncio.wait_for(socket_entered.wait(), 2)
            interrupted.cancel()
            await asyncio.gather(interrupted, return_exceptions=True)
            joined = asyncio.create_task(direct.disconnect())
            await asyncio.sleep(0.05)
            assert len(close_calls) == 1 and not joined.done()
            socket_release.set()
            await asyncio.wait_for(joined, 2)
        finally:
            finish.set()
            socket_release.set()
            if caller is not None:
                caller.cancel()
                await asyncio.gather(caller, return_exceptions=True)
            if stopping is not None:
                await asyncio.gather(stopping, return_exceptions=True)
            for pending in (interrupted, joined):
                if pending is not None:
                    await asyncio.gather(pending, return_exceptions=True)
            await direct.close()
        closed_calls = len(close_calls)
        await direct.disconnect()
        assert direct._closed and len(close_calls) == closed_calls
        image = root / "image.png"
        Image.new("RGB", (32, 24), "red").save(image)
        client = Client(Session(1, "synthetic"), data_dir=root)
        try:
            info = await client.media.prepare(Media(image, MediaKind.PHOTO))
            assert (info["width"], info["height"]) == (32, 24)
            operation = await client.store.enqueue("a", "p", "SendMessage", b"frozen", "{}")
            assert (await client.store.operation("a", operation))["status"] == "queued"
            client.account = "a"
            await client.store.finish("a", operation, "confirmed", response=b"", basis="history")
            proof = await client.get_operation(operation)
            assert proof.history_verified and not proof.rpc_confirmed
            value = WebUpdate()
            value.message.rid = 2**60 + 15
            assert WebUpdate.FromString(value.SerializeToString()).message.rid == 2**60 + 15
            indexed = WebSearchResult()
            indexed.result.messageContainer.authorSign.SetInParent()
            assert WebSearchResult.FromString(indexed.SerializeToString()).result.messageContainer.HasField(
                "authorSign"
            )
            assert callable(client.enqueue_account_action) and callable(client.iter_search_messages)
            assert callable(client.set_group_visibility)
            assert callable(client.join_public_group) and callable(client.get_group_invite_url)
            public_join = contract("JoinPublicGroup").request()
            public_join.peer.type, public_join.peer.id = 2, 10
            assert public_join.SerializeToString() == bytes.fromhex("0a040802100a")
            assert "rid" not in public_join.DESCRIPTOR.fields_by_name
            invite_url = contract("GetGroupInviteURL").request()
            invite_url.groupPeer.groupId, invite_url.groupPeer.accessHash = 10, 99
            assert invite_url.SerializeToString() == bytes.fromhex("0a04080a1063")
            assert contract("GetGroupInviteURL").response(url="x").SerializeToString() == bytes.fromhex(
                "0a0178"
            )
            assert contract("GetGroupInviteURL").readonly and not contract("JoinPublicGroup").readonly
            visibility = contract("SetRestriction").request(restriction=1)
            visibility.groupOutPeer.groupId, visibility.groupOutPeer.accessHash = 10, 99
            visibility.nick.value = "qa123"
            assert visibility.SerializeToString() == bytes.fromhex("0a04080a106310011a070a057161313233")
            visibility_peer = Peer(PeerKind.CHANNEL, 10, 99, username="old-visibility-alias")
            client._cache_peer(visibility_peer)
            client._active = True  # Controlled admission with no network/background worker.
            try:
                visibility_handle = await client.enqueue_account_action(
                    "SetRestriction", visibility, idempotency_key="visibility"
                )
            finally:
                client._active = False
            visibility_row = await client.store.operation(client.account, visibility_handle.operation_id)
            assert visibility_row["peer"] == visibility_peer.key
            assert json.loads(visibility_row["context"])["rids"] == []
            assert "@old-visibility-alias" not in client._peer_cache
            assert (
                await visibility_handle.cancel()
            )  # Finish this isolated queued fixture before later FIFO checks.
            summaries = [item async for item in client.iter_operations(statuses="confirmed", page_size=1)]
            assert len(summaries) == 1 and summaries[0].history_verified
            assert all(
                callable(getattr(client, method))
                for method in (
                    "enqueue_edit_message",
                    "enqueue_edit_caption",
                    "enqueue_delete_messages",
                    "enqueue_forward",
                )
            )
            assert callable(client.download_many) and callable(client.download_album)
            assert callable(client.get_member_page) and callable(client.iter_views)
            count_request = contract("GetGroupMembersCount").request()
            count_request.group.groupId, count_request.group.accessHash = 44, 99
            assert count_request.SerializeToString() == bytes.fromhex("0a04082c1063")
            assert contract("GetGroupMembersCount").readonly
            count_calls = []
            count_value = 6
            old_rpc, old_full = client._rpc, client.get_full_group

            async def count_rpc(method, request, **kwargs):
                count_calls.append(method)
                return contract(method).response(membersCount=count_value)

            async def count_full(peer):
                from fncbale.proto.struct_pb2 import WebFullGroup

                count_calls.append("GetFullGroup")
                value = WebFullGroup(id=peer.id)
                value.membersCount.SetInParent()
                return value

            client._rpc, client.get_full_group = count_rpc, count_full
            try:
                count_peer = Peer(PeerKind.CHANNEL, 44, 99)
                assert await client.member_count(count_peer) == 6
                assert count_calls == ["GetGroupMembersCount"]
                count_value = 0
                assert await client.member_count(count_peer) == 0
                assert count_calls == ["GetGroupMembersCount", "GetGroupMembersCount", "GetFullGroup"]
                assert await client.member_count(count_peer, source="full") == 0
            finally:
                client._rpc, client.get_full_group = old_rpc, old_full
            assert all(
                callable(getattr(client, method))
                for method in (
                    "edit_profile_name",
                    "edit_profile_about",
                    "edit_profile_username",
                    "enqueue_edit_profile_name",
                    "enqueue_edit_profile_about",
                    "enqueue_edit_profile_username",
                )
            )
            from fncbale import MemberPage, MessageViews, MessageRef

            view_ref = MessageRef(Peer(PeerKind.CHANNEL, 10), 3, 4)
            assert MessageViews(view_ref, 0).available and not MessageViews(view_ref, None).available
            page = MemberPage(view_ref.peer, (), b"input", b"", b"")
            assert page.complete and "input" not in repr(page)
            assert all(
                callable(getattr(client, name))
                for name in ("start_login", "complete_login", "complete_password_login")
            )
            assert client.config.download_limit == 4 and client.config.global_download_limit == 16
            from fncbale import BatchDownloadError, DownloadResult, SessionFile

            saved = SessionFile(root / "saved.session")
            await saved.save(Session(42, "synthetic-session"))
            assert (await saved.load()).user_id == 42
            result = DownloadResult(0, root / "file", False, "BaleError")
            assert BatchDownloadError([result]).results == (result,)
            album_operation = await client.store.enqueue(
                "a",
                "p",
                "SendMultiMediaMessage",
                b"",
                json.dumps({"media": [{"sha256": "one"}, {"sha256": "two"}]}),
            )
            assert (await client.store.claim("a"))["id"] == album_operation
            await asyncio.gather(
                client.store.commit_media_upload(
                    "a", album_operation, 0, sha256="one", file_id=10, access_hash=20
                ),
                client.store.commit_media_upload(
                    "a", album_operation, 1, sha256="two", file_id=11, access_hash=20
                ),
            )
            uploaded = json.loads((await client.store.operation("a", album_operation))["context"])["media"]
            assert [item["file_id"] for item in uploaded] == [10, 11]
            event_id = (
                await client.store.record("a", b"\xff", [("unknown", "unknown_decode", b"\xff", None)])
            )[0]
            await client.store.fail_event("a", event_id, 2, expected_attempts=0)
            assert await client.store.fail_event("a", event_id, 2, expected_attempts=0) == {
                "status": "pending",
                "attempts": 1,
            }
            await client.store.fail_event("a", event_id, 2, expected_attempts=1)
            failed = [event async for event in client.iter_failed_events(page_size=1)]
            assert len(failed) == 1 and failed[0].event_id == event_id and failed[0].handler_failures == 2
            assert failed[0].raw == b"\xff" and not client._leased_events
            assert await client.replay_event(event_id)
            await failed[0].ack()
            assert await client.store.fail_event("a", event_id, 2) == {"status": "acked", "attempts": 0}
            assert not [event async for event in client.iter_failed_events()]
            early = WebUpdate()
            early.messageContentChanged.peer.type, early.messageContentChanged.peer.id = 2, 10
            early.messageContentChanged.rid = 111
            early.messageContentChanged.message.documentMessage.caption.text = "early caption"
            early.messageDelete.peer.CopyFrom(early.messageContentChanged.peer)
            early.messageDelete.rids.append(112)
            for event_id in await client.store.record("a", early.SerializeToString(), journal_events(early)):
                await client.store.ack("a", event_id)
            base = WebUpdate()
            base.messages.peer.type, base.messages.peer.id = 3, 10
            for rid in (112, 111):
                item = base.messages.messageContainers.add(rid=rid, date=100)
                item.groupedId.value = 99
                item.message.documentMessage.caption.text = "old caption"
            await client.store.record("a", base.SerializeToString(), journal_events(base))
            snapshot = await client.get_album(Peer(PeerKind.CHANNEL, 10), 99)
            assert len(snapshot.messages) == 1 and snapshot.messages[0].text == "early caption"
            assert (
                await client.store.run(
                    lambda db: db.execute("PRAGMA user_version").fetchone()[0], write=False
                )
                == 3
            )
            assert (
                await client.store.run(
                    lambda db: db.execute("SELECT count(*) FROM album_pending").fetchone()[0], write=False
                )
                == 0
            )
            await client.store.limit_account("a", 1)
            assert client.store.rate_deadline("a") > 0
            scope = Conversation(client, Peer(PeerKind.USER, 2), 1)
            scope.close()
            try:
                await scope.receive()
            except ConversationClosed:
                pass
            else:
                raise AssertionError("Closed conversation must release installed API receive")
            assert HistoryPaginationGap(scope.peer, 20).date == 20
            client._active, client._closing = True, True
            try:
                await client.enqueue_message(scope.peer, "rejected closing operation")
            except ClientClosed:
                pass
            else:
                raise AssertionError("Closing client must reject new durable admission")
            import av

            assert av.library_versions
        finally:
            await client.close()

        from fncbale import FSM, LoginChallenge, PasswordRequired
        from fncbale.errors import RpcError
        from fncbale.proto import response_pb2 as r

        login_client = Client(Session(7, "synthetic-old"), data_dir=root / "native-login")
        login_client.account = "old-local-context"
        login_client.fsm = FSM(login_client.store, login_client.account)
        calls = []

        async def auth(service, method, payload):
            calls.append(method)
            if method == "StartPhoneAuth":
                return r.StartPhoneAuth(transaction_hash="synthetic-challenge").SerializeToString()
            if method == "ValidateCode":
                raise RpcError(7, method, reason="password needed for login")
            value = r.Auth()
            value.user.id, value.jwt.value = 42, "synthetic-new-session"
            return value.SerializeToString()

        login_client._grpc.request = auth
        try:
            challenge = await login_client.start_login("09000000000")
            assert isinstance(challenge, LoginChallenge) and "synthetic-challenge" not in repr(challenge)
            try:
                await login_client.complete_login(challenge, "synthetic-code")
            except PasswordRequired as exc:
                assert exc.challenge is challenge
            else:
                raise AssertionError("Missing explicit password challenge")
            session = await login_client.complete_password_login(challenge, "synthetic-password")
            assert session == await login_client.session_file.load()
            assert login_client.account.endswith(":42") and login_client.fsm is None
            assert calls == ["StartPhoneAuth", "ValidateCode", "ValidatePassword"]
        finally:
            await login_client.close()

        scoped = Client(Session(1, "synthetic"), data_dir=root / "operation-account")
        scoped.account, scoped._active = "original", True
        try:
            handles = [await scoped.enqueue_message(Peer(PeerKind.USER, 7), str(i)) for i in range(3)]
            operation_stream = scoped.iter_operations(page_size=3)
            await anext(operation_stream)
            scoped.account = "different"
            try:
                await anext(operation_stream)
            except StopAsyncIteration:
                pass
            else:
                raise AssertionError("Old account page must not yield after identity change")
            for method in (handles[0].status, handles[0].wait, handles[0].cancel):
                try:
                    await method()
                except BaleError as error:
                    assert "account" in str(error)
                else:
                    raise AssertionError("Old operation handle must retain admission account")
            assert not scoped._operation_waiters
            scoped.account = "original"
            assert (await handles[0].status()).status == "queued"
            assert await handles[0].cancel()
            assert (await handles[0].status()).status == "cancelled"
        finally:
            await scoped.close()

        queued_rpc = Client(Session(1, "synthetic"), data_dir=root / "queued-rpc")
        gate = queued_rpc._rpc_limit = asyncio.Semaphore(0)
        attempts = []

        async def rpc_after_wait(*arguments):
            attempts.append(True)
            return b"synthetic"

        queued_rpc._grpc.request = rpc_after_wait
        waiting_rpc = asyncio.create_task(
            queued_rpc.invoke_raw("synthetic", "method", b"frozen", route="http", retry_policy="none")
        )
        try:
            async with asyncio.timeout(10):
                while not gate._waiters:
                    await asyncio.sleep(0)
            await queued_rpc.close()
            gate.release()
            try:
                await waiting_rpc
            except ClientClosed:
                pass
            else:
                raise AssertionError("Queued RPC cannot enter transport after close")
            assert not attempts
        finally:
            gate.release()
            waiting_rpc.cancel()
            await asyncio.gather(waiting_rpc, return_exceptions=True)
            await queued_rpc.close()

        buffered = Client(Session(1, "synthetic"), data_dir=root / "buffered-history")
        buffered.account = "original"
        history_calls = []

        async def history_response(method, request, **kwargs):
            history_calls.append(buffered.account)
            response = contract(method).response()
            for index in range(3):
                response.history.add(rid=index + 1, date=50 - index)
            return response

        buffered._rpc = history_response
        stream = buffered.iter_history(Peer(PeerKind.USER, 7), limit=3, page_size=3)
        try:
            await anext(stream)
            buffered.account = "different"
            try:
                await anext(stream)
            except StopAsyncIteration:
                pass
            else:
                raise AssertionError("Buffered history cannot mix account identities")
            assert history_calls == ["original"]
        finally:
            await stream.aclose()
            await buffered.close()
        import httpx
        from fncbale.protocol import grpc_frame
        from fncbale.transports import GrpcTransport

        cookie_headers = []

        def response(request):
            cookie_headers.append(request.headers.get("cookie"))
            return httpx.Response(
                200,
                headers={"set-cookie": "access_token=synthetic-uncommitted; Path=/", "grpc-status": "0"},
                content=grpc_frame(b""),
            )

        async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as http:
            anonymous = GrpcTransport(None, login_client.config, http=http)
            await anonymous.request("auth", "validate", b"")
            await anonymous.request("read", "probe", b"")
            assert not cookie_headers[0] and not cookie_headers[1]
        from fncbale.errors import TransportError
        from fncbale.models import MediaInfo

        transfer = Client(Session(1, "synthetic"), data_dir=root / "media-http")
        await transfer.resources.http.aclose()
        transfer_calls = []

        def unfinished(request):
            transfer_calls.append(request.method)
            return httpx.Response(
                308 if request.method == "PUT" else 206,
                headers={"location": "https://other.invalid/?secret=hidden"},
                content=b"abcdef",
            )

        transfer.resources.http = httpx.AsyncClient(
            transport=httpx.MockTransport(unfinished), follow_redirects=True
        )

        async def allocate(method, request, **kwargs):
            response = fncbale.contract(method).response()
            if method == "GetNasimFileUploadUrl":
                response.fileId, response.url = 1, "https://signed.invalid/upload"
            else:
                response.fileUrl.url = "https://signed.invalid/download"
            return response

        transfer._rpc = allocate
        try:
            info = await transfer.media.prepare(Media(b"content"))
            try:
                await transfer.media.upload(transfer, Peer(PeerKind.USER, 2), info)
            except TransportError:
                assert "file_id" not in info
            else:
                raise AssertionError("Redirect cannot confirm an upload")
            target = root / "preserved.bin"
            target.write_bytes(b"old")
            media = MediaInfo(MediaKind.DOCUMENT, 1, 2, 6, "file", "application/octet-stream")
            try:
                await transfer.download(media, target)
            except TransportError:
                assert target.read_bytes() == b"old"
            else:
                raise AssertionError("Partial response cannot confirm a complete download")
            assert transfer_calls == ["PUT", "GET"] and not list(root.glob("*.part"))
            import fncbale.media as media_module

            await transfer.resources.http.aclose()
            retained, opened = [], []
            original_open = media_module.open_file

            async def track_open(path, mode):
                stream = await original_open(path, mode)
                if mode == "rb":
                    opened.append(stream)
                return stream

            class InterruptedBody(httpx.AsyncBaseTransport):
                async def handle_async_request(self, request):
                    retained.append(request)
                    iterator = request.stream.__aiter__()
                    if len(retained) == 1:
                        retained.append(iterator)
                        await anext(iterator)
                        raise httpx.WriteError("modeled interrupted upload body")
                    async for _ in iterator:
                        pass
                    return httpx.Response(200)

            transfer.resources.http = httpx.AsyncClient(transport=InterruptedBody())
            media_module.open_file = track_open
            try:
                info = await transfer.media.prepare(Media(b"content"))
                await transfer.media.upload(transfer, Peer(PeerKind.USER, 2), info)
                assert len(opened) == 2 and all(stream.closed for stream in opened)
            finally:
                media_module.open_file = original_open
                for iterator in retained:
                    if hasattr(iterator, "aclose"):
                        await iterator.aclose()
        finally:
            await transfer.close()
        admission = Client(Session(1, "synthetic"), data_dir=root / "admission")
        admission.account, admission._active = "admission", True
        cached = admission._cache_peer(Peer(PeerKind.USER, 1, username="old"))
        entered = asyncio.Event()
        original_enqueue, accepted = admission.store.enqueue, []

        async def accepted_then_wait(*args, **kwargs):
            accepted.append(await original_enqueue(*args, **kwargs))
            entered.set()
            await asyncio.Event().wait()

        admission.store.enqueue = accepted_then_wait
        request = contract("EditNickName").request()
        request.nickname.value = "new"
        task = asyncio.create_task(
            admission.enqueue_account_action("EditNickName", request, idempotency_key="same")
        )
        try:
            await asyncio.wait_for(entered.wait(), 3)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            assert cached.key not in admission._peer_cache and "@old" not in admission._peer_cache
            assert (await admission.get_operation(accepted[0])).status == "queued"
            admission.store.enqueue = original_enqueue
            replay = await admission.enqueue_edit_profile_username("@new", idempotency_key="same")
            assert replay.operation_id == accepted[0]
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
            await admission.close()
        await media_account_boundary(root / "media-account-boundary")
    distributions = sorted(
        distribution.metadata["Name"].lower() for distribution in importlib.metadata.distributions()
    )
    assert not any(
        name in distributions for name in ("aiobale", "balethon", "baleclient", "balenova", "nova")
    )
    result = {
        "pass": True,
        "version": __version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "bale_sdk_dependencies": [],
        "checks": [
            "installed wheel import",
            "Pillow metadata",
            "PyAV native libraries",
            "SQLite FULL WAL commit",
            "int64 protobuf",
            "client cleanup",
            "distinct delivery proof and committed account gate",
            "scoped conversation and history gap public API",
            "immediate close admission fence",
            "typed search container/signature and durable action API",
            "durable mutation handles and bounded account operation inspection",
            "atomic sibling upload merge in installed store",
            "guarded failure counter and failed-event inspection/replay/discard",
            "schema 3 and late album metadata edit/tombstone merge",
            "batch download API/limits/results and atomic native session file",
            "staged native auth and exact RPC password discriminator",
            "durable handle account ownership and buffered operation inspection fence",
            "queued raw RPC rejects permanent close before acquiring transport",
            "public history pagination ends before yielding another account's buffered row",
            "typed member pages and explicit view zero/unknown public API",
            "foreign-account session commit detaches prior ledger/FSM context",
            "Set-Cookie cannot implicitly adopt uncommitted RPC authentication",
            "durable profile action builders and explicit wrapper presence API",
            "redirected PUT and partial GET cannot confirm media transfer",
            "interrupted request body closes owned file before retry despite retained transport references",
            "cancelled durable profile admission invalidates self aliases without retracting accepted work",
            "strict finite configuration and immutable retry policy snapshot",
            "bounded WS send/lock and HTTP header deadlines; ambiguous redirects never followed",
            "HTTP connection/pool timeout is unsent; read/write timeout remains ambiguous",
            "independent SetRestriction wire wrapper, group FIFO namespace and explicit visibility API",
            "bounded peer identity LRU, alias replacement/eviction, constant-key numeric resolution and closed-cache cleanup",
            "distinct public short-peer join and private token join; typed current invite URL read",
            "compact member count API/typed wire with presence-aware zero and explicit full source",
            "synchronous handler reservation, pre-step cancellation, stale iterator fence and original-account ACK",
            "direct-await tracked dispatcher shutdown waits for worker cleanup and preserves unacknowledged event ID",
            "cancelled disconnect waiter cannot abandon socket cleanup; concurrent waiter joins once",
            "disconnect after permanent close joins its result without late socket cleanup",
            "media preparation rejects changed account before admission and removes unaccepted spool",
        ],
    }
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
