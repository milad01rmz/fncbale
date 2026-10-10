"""Typed synthetic server for independent multiaccount fault/recovery QA."""

import asyncio
from collections import defaultdict

import httpx

from fncbale import contract
from fncbale.errors import RpcError, TransportError
from fncbale.protocol import grpc_decode, grpc_frame
from fncbale.proto import response_pb2 as r, struct_pb2 as s


class ModelServer:
    def __init__(self):
        self.logs = defaultdict(list)
        self.messages = defaultdict(dict)
        self.streams = {}
        self.drop_live = set()
        self.lost_ack = set()
        self.limited = set()
        self.calls = defaultdict(int)
        self.active, self.peak = 0, 0
        self.date = 1720000000000
        self.files = {}
        self.allocations = 0
        self.errors = []

    async def publish(self, uid, peer, update):
        self.logs[uid, peer].append(update.SerializeToString())
        stream = self.streams.get(uid)
        if stream and stream.connected and uid not in self.drop_live:
            frame = r.Response()
            frame.ws_update.update.composed_update.CopyFrom(update)
            try:
                stream.updates.put_nowait(frame.SerializeToString())
            except asyncio.QueueFull:
                await stream.close()

    async def rpc(self, uid, method, payload):
        self.active += 1
        self.peak = max(self.peak, self.active)
        self.calls[uid, method] += 1
        try:
            await asyncio.sleep(0.001)
            request = contract(method).request.FromString(payload)
            response = contract(method).response()
            if method == "GetRoutesStates":
                response.seqs.add(seq=len(self.logs[uid, 0]))
                for peer in (101, 102):
                    state = response.seqs.add(seq=len(self.logs[uid, peer]))
                    state.groupPeer.groupId = peer
            elif method == "GetDiff":
                for old in request.states:
                    peer = old.groupPeer.groupId if old.HasField("groupPeer") else 0
                    pending = self.logs[uid, peer][old.seq :]
                    batch = response.updates.add()
                    batch.state.CopyFrom(old)
                    page = pending[:3]
                    batch.state.seq += len(page)
                    batch.needMore = int(len(pending) > len(page))
                    for raw in page:
                        batch.updates.add().ParseFromString(raw)
            elif method == "LoadHistory":
                histories = sorted(
                    self.messages[uid, request.peer.id].values(), key=lambda item: item.date, reverse=True
                )
                for history in [item for item in histories if request.date < 0 or item.date <= request.date][
                    : request.limit
                ]:
                    response.history.add().CopyFrom(history)
            elif method in ("SendMessage", "SendMultiMediaMessage"):
                if uid in self.limited:
                    self.limited.remove(uid)
                    raise RpcError(8, method, retry_after=0.02)
                self.date += 1
                response.date = self.date
                update = s.WebUpdate()
                if method == "SendMessage":
                    peer, rid = request.peer.id, request.rid
                    assert request.peer.type == 2 and not request.HasField("exPeer")
                    history = s.WebHistory(rid=rid, date=self.date, senderUid=uid)
                    history.message.CopyFrom(request.message)
                    self.messages[uid, peer][rid] = history
                    item = update.message
                    item.peer.type, item.peer.id = request.peer.type, request.peer.id
                    item.rid, item.date, item.senderUid = rid, self.date, uid
                    item.message.CopyFrom(request.message)
                else:
                    peer = request.peer.id
                    assert request.peer.type == 3
                    update.messages.peer.type, update.messages.peer.id = request.peer.type, request.peer.id
                    self.date += len(request.multiMedia) - 1
                    response.date = self.date
                    for index, media in reversed(list(enumerate(request.multiMedia))):
                        item_date = self.date - (len(request.multiMedia) - 1 - index)
                        history = s.WebHistory(rid=media.randomId, date=item_date, senderUid=uid)
                        history.groupedId.value = request.groupedId
                        history.message.documentMessage.CopyFrom(media.media)
                        self.messages[uid, peer][history.rid] = history
                        update.messages.messageContainers.add().CopyFrom(history)
                await self.publish(uid, peer, update)
                if uid in self.lost_ack:
                    self.lost_ack.remove(uid)
                    raise TransportError("synthetic post-commit ACK loss", possibly_sent=True)
            elif method == "UpdateMessage":
                peer = request.peer.id
                self.messages[uid, peer][request.rid].message.CopyFrom(request.updatedMessage)
                update = s.WebUpdate()
                item = update.messageContentChanged
                item.peer.type, item.peer.id = request.peer.type, request.peer.id
                item.rid = request.rid
                item.date.value = self.messages[uid, peer][request.rid].date
                item.message.CopyFrom(request.updatedMessage)
                await self.publish(uid, peer, update)
            elif method == "DeleteMessage":
                assert len(request.rids) == len(request.dates.dates)
                assert all(
                    rid not in self.messages[uid, request.peer.id]
                    or self.messages[uid, request.peer.id][rid].date == date
                    for rid, date in zip(request.rids, request.dates.dates, strict=True)
                ), "Delete requires each actual message creation date, not a shared batch ACK date"
                update = s.WebUpdate()
                update.messageDelete.peer.type, update.messageDelete.peer.id = (
                    request.peer.type,
                    request.peer.id,
                )
                update.messageDelete.rids.extend(request.rids)
                for rid in request.rids:
                    self.messages[uid, request.peer.id].pop(rid, None)
                await self.publish(uid, request.peer.id, update)
            elif method == "GetNasimFileUploadUrl":
                self.allocations += 1
                response.fileId = self.allocations
                response.url = f"https://files.invalid/{self.allocations}"
                assert request.exPeer.type == 3
            elif method == "GetNasimFileUrl":
                response.fileUrl.url = f"https://files.invalid/{request.file.fileId}"
            else:
                raise AssertionError(f"Unexpected QA method {method}")
            return response.SerializeToString()
        except (RpcError, TransportError):
            raise
        except Exception as error:
            self.errors.append(f"{method}: {error}")
            raise AssertionError(f"Model method {method}: {error}") from error
        finally:
            self.active -= 1

    async def http_rpc(self, request):
        uid = int(request.headers["cookie"].split("synthetic-")[1])
        method = request.url.path.rsplit("/", 1)[1]
        try:
            raw = await self.rpc(uid, method, grpc_decode(await request.aread(), {}, method))
            return httpx.Response(200, headers={"grpc-status": "0"}, content=grpc_frame(raw))
        except RpcError as error:
            return httpx.Response(
                200, headers={"grpc-status": str(error.code), "retry-after": str(error.retry_after or 0)}
            )

    async def file_http(self, request):
        file_id = int(request.url.path.strip("/"))
        if request.method == "PUT":
            self.files[file_id] = await request.aread()
            return httpx.Response(200)
        return httpx.Response(200, content=self.files[file_id])

    async def connect(self, transport):
        class Socket:
            async def close(self):
                pass

        uid = int(transport._token.split("synthetic-")[1])
        self.streams[uid] = transport
        transport.socket = Socket()
        transport.generation += 1
        transport.disconnected.clear()

    async def websocket_rpc(self, transport, service, method, payload):
        uid = int(transport._token.split("synthetic-")[1])
        return await self.rpc(uid, method, payload)
