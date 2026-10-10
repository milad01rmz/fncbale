from __future__ import annotations

import asyncio
import hashlib
import inspect
import math
import mimetypes
from pathlib import Path
import uuid
import zlib
import os

import httpx

from .contracts import contract
from .errors import BaleError, TransportError
from .models import Media, MediaKind
from .proto import struct_pb2 as s


async def report_progress(callback, done, total):
    if callback:
        result = callback(done, total)
        if inspect.isawaitable(result):
            await result


async def disk_call(function, *args, cancel_cleanup=None, **kwargs):
    """Finish an outstanding file syscall before cancellation closes its handle."""
    task = asyncio.create_task(asyncio.to_thread(function, *args, **kwargs))
    cancelled = False
    while True:
        try:
            result = await asyncio.shield(task)
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
        if cancel_cleanup:
            await disk_call(cancel_cleanup, result)
        raise asyncio.CancelledError
    return result


async def open_file(path, mode):
    return await disk_call(Path(path).open, mode, cancel_cleanup=lambda stream: stream.close())


class MediaPipeline:
    def __init__(self, root, config, resources):
        self.root, self.config, self.resources = Path(root), config, resources
        self._metadata_cache = {}
        self._metadata_cache_enabled = True
        self.in_use = set()

    def close_cache(self):
        self._metadata_cache_enabled = False
        self._metadata_cache.clear()

    async def prepare(self, media: Media):
        owned = []
        try:
            return await self._prepare(media, owned)
        finally:
            self.in_use.difference_update(owned)

    async def _prepare(self, media: Media, owned):
        """Freeze source bytes before accepting a durable outbox operation."""
        spool = self.root / "spool"
        await asyncio.to_thread(spool.mkdir, parents=True, exist_ok=True)
        path = spool / (uuid.uuid4().hex + ".media")
        self.in_use.add(path.resolve())
        owned.append(path.resolve())
        source = media.source
        filename = media.filename or (Path(source).name if isinstance(source, (str, Path)) else "upload")
        mime = media.mime_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        digest, crc, size = hashlib.sha256(), 0, 0
        stream = None
        try:
            stream = await open_file(path, "wb")

            async def write(chunk):
                nonlocal crc, size
                if not isinstance(chunk, (bytes, bytearray, memoryview)):
                    raise TypeError("Media stream must yield bytes")
                size += len(chunk)
                if size > (1 << 31) - 1:
                    raise ValueError("Media exceeds current wire file-size range")
                digest.update(chunk)
                crc = zlib.crc32(chunk, crc)
                await disk_call(stream.write, chunk)

            if isinstance(source, (str, Path)):
                input_file = await open_file(source, "rb")
                try:
                    while chunk := await disk_call(input_file.read, self.config.stream_chunk_size):
                        await write(chunk)
                finally:
                    await disk_call(input_file.close)
            elif isinstance(source, bytes):
                for pos in range(0, len(source), self.config.stream_chunk_size):
                    await write(source[pos : pos + self.config.stream_chunk_size])
            elif hasattr(source, "__aiter__"):
                async for chunk in source:
                    await write(chunk)
            elif hasattr(source, "read"):
                while chunk := await disk_call(source.read, self.config.stream_chunk_size):
                    await write(chunk)
            else:
                raise TypeError("Expected path, bytes, binary stream, or async byte iterator")
            await disk_call(stream.flush)
            await disk_call(os.fsync, stream.fileno())
        except BaseException:
            if stream:
                await disk_call(stream.close)
            await disk_call(path.unlink, missing_ok=True)
            raise
        try:
            await disk_call(stream.close)
        except BaseException:
            await disk_call(path.unlink, missing_ok=True)
            raise
        try:
            if not size:
                raise ValueError("Empty media file")
            info = {
                "path": str(path.resolve()),
                "filename": filename,
                "mime": mime,
                "size": size,
                "sha256": digest.hexdigest(),
                "crc": crc,
                "kind": str(media.kind),
                "caption": media.caption,
                "width": 0,
                "height": 0,
                "duration": 0.0,
            }
            async with self.resources.metadata_limit:
                cache_key = (info["sha256"], media.kind)
                values = self._metadata_cache.get(cache_key)
                if values is None:
                    values = await disk_call(self._extract, path, media.kind)
                    if self._metadata_cache_enabled:
                        if len(self._metadata_cache) >= 512:
                            self._metadata_cache.pop(next(iter(self._metadata_cache)))
                        self._metadata_cache[cache_key] = values
                info.update(values)
            return info
        except BaseException:
            await disk_call(path.unlink, missing_ok=True)
            raise

    @staticmethod
    def _extract(path, kind):
        if kind == MediaKind.DOCUMENT:
            return {}
        if kind == MediaKind.PHOTO:
            from PIL import Image

            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                width, height = image.size
                return {"width": width, "height": height, "mime": Image.MIME.get(image.format, "image/jpeg")}
        import av

        with av.open(str(path)) as container:
            streams = container.streams.video if kind == MediaKind.VIDEO else container.streams.audio
            if not streams:
                raise ValueError(f"Media does not contain a {kind} stream")
            stream = streams[0]
            duration = (
                float(stream.duration * stream.time_base)
                if stream.duration is not None
                else float(container.duration / av.time_base)
                if container.duration
                else 0
            )
            if duration <= 0:
                # Decode metadata timing only when the container omitted its duration.
                for packet in container.demux(stream):
                    if packet.pts is not None:
                        duration = max(
                            duration, float((packet.pts + (packet.duration or 0)) * stream.time_base)
                        )
            if duration <= 0:
                raise ValueError("Could not determine media duration")
            return {
                "duration": duration,
                "width": getattr(stream.codec_context, "width", 0),
                "height": getattr(stream.codec_context, "height", 0),
            }

    async def upload(self, client, peer, info, progress=None):
        if info.get("file_id"):
            return self.document(info)
        async with client._upload_limit, self.resources.upload_limit:
            for attempt in range(2):
                request = contract("GetNasimFileUploadUrl").request(
                    expectedSize=info["size"],
                    crc=info["crc"],
                    uid=client.session.user_id,
                    name=info["filename"],
                    mimeType=info["mime"],
                    chunkSize=self.config.stream_chunk_size,
                )
                request.exPeer.type, request.exPeer.id = peer.out_type, peer.id
                request.exPeer.accessHash = peer.access_hash
                request.sendType.type = 1
                allocated = await client._rpc("GetNasimFileUploadUrl", request, readonly=True)
                if not allocated.fileId or not allocated.url:
                    raise BaleError("Upload allocation returned no file or URL")

                async def chunks():
                    stream = await open_file(info["path"], "rb")
                    done = 0
                    try:
                        while chunk := await disk_call(stream.read, self.config.stream_chunk_size):
                            done += len(chunk)
                            yield chunk
                            await report_progress(progress, done, info["size"])
                    finally:
                        await disk_call(stream.close)

                if not allocated.duplicate:
                    body = chunks()
                    try:
                        response = await self.resources.http.put(
                            allocated.url,
                            content=body,
                            headers={
                                "content-type": "application/octet-stream",
                                "content-length": str(info["size"]),
                            },
                            timeout=self.config.upload_timeout,
                            follow_redirects=False,
                        )
                        # A redirect, partial response or asynchronous acceptance
                        # is not proof that this allocated file is ready to send.
                        if response.status_code not in (200, 201, 204):
                            if attempt == 0 and response.status_code in (401, 403, 408, 410, 500, 502, 503):
                                continue
                            raise TransportError(f"Media upload HTTP {response.status_code}")
                    except TransportError:
                        raise
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        if attempt == 0:
                            continue
                        raise TransportError("Media upload interrupted") from None
                    finally:
                        # HTTP transports may stop reading without closing the
                        # caller-owned async iterator. Drain its file cleanup
                        # before retry, cancellation or adopting the allocation.
                        await body.aclose()
                info["file_id"], info["access_hash"] = allocated.fileId, client.session.user_id
                return self.document(info)
        raise TransportError("Media upload attempts exhausted")

    @staticmethod
    def document(info):
        doc = s.WebMedia(
            fileId=info["file_id"],
            accessHash=info["access_hash"],
            fileSize=info["size"],
            name=info["filename"],
            mimeType=info["mime"],
        )
        doc.caption.text = info["caption"]
        kind = MediaKind(info["kind"])
        if kind == MediaKind.PHOTO:
            doc.ext.documentExPhoto.w, doc.ext.documentExPhoto.h = info["width"], info["height"]
        elif kind == MediaKind.VIDEO:
            video = doc.ext.documentExVideo
            video.w, video.h, video.duration = info["width"], info["height"], math.ceil(info["duration"])
        elif kind == MediaKind.VOICE:
            doc.ext.documentExVoice.duration = round(info["duration"] * 1000)
        elif kind == MediaKind.AUDIO:
            doc.ext.documentExAudio.duration = round(info["duration"] * 1000)
        return doc

    async def download(self, client, message, destination, *, progress=None, expected_sha256=None, _url=None):
        media = message.media if hasattr(message, "media") else message
        if media is None:
            raise ValueError("Message has no media")
        request = contract("GetNasimFileUrl").request()
        request.file.fileId, request.file.accessHash = media.file_id, media.access_hash
        target = Path(destination)
        temporary = target.with_name(target.name + "." + uuid.uuid4().hex + ".part")
        await asyncio.to_thread(target.parent.mkdir, parents=True, exist_ok=True)
        for attempt in range(2):
            url = _url if attempt == 0 else None
            if not url:
                allocated = await client._rpc("GetNasimFileUrl", request)
                url = allocated.fileUrl.url
            if not url:
                raise BaleError("Download allocation returned no URL")
            stream = None
            digest, done = hashlib.sha256(), 0
            try:
                stream = await open_file(temporary, "wb")
                async with self.resources.http.stream(
                    "GET", url, timeout=self.config.upload_timeout, follow_redirects=False
                ) as response:
                    # This path requests the entire file and does not issue ranges.
                    if response.status_code != 200:
                        if attempt == 0 and response.status_code in (401, 403, 408, 410, 500, 502, 503):
                            continue
                        raise TransportError(f"Download HTTP {response.status_code}")
                    async for chunk in response.aiter_bytes(self.config.stream_chunk_size):
                        done += len(chunk)
                        if done > media.size:
                            raise BaleError("Download exceeds expected file size")
                        digest.update(chunk)
                        await disk_call(stream.write, chunk)
                        await report_progress(progress, done, media.size)
                if done != media.size or (expected_sha256 and digest.hexdigest() != expected_sha256):
                    raise BaleError("Downloaded file size or hash mismatch")
                await disk_call(stream.flush)
                await disk_call(os.fsync, stream.fileno())
                await disk_call(stream.close)
                stream = None
                await disk_call(temporary.replace, target)
                return target
            except httpx.HTTPError:
                if attempt:
                    raise TransportError("Media download interrupted") from None
            finally:
                if stream:
                    await disk_call(stream.close)
                await disk_call(temporary.unlink, missing_ok=True)
        raise TransportError("Media download attempts exhausted")
