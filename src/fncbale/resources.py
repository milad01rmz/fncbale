import asyncio
import ssl
import certifi
import httpx


class Resources:
    def __init__(self, config):
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.rpc_limit = asyncio.Semaphore(config.global_rpc_limit)
        self.upload_limit = asyncio.Semaphore(config.global_upload_limit)
        self.download_limit = asyncio.Semaphore(config.global_download_limit)
        self.metadata_limit = asyncio.Semaphore(config.metadata_workers)
        # Used for signed file transfers only, never authenticated account RPCs.
        self.http = httpx.AsyncClient(
            http2=True,
            verify=self.ssl_context,
            timeout=config.upload_timeout,
            limits=httpx.Limits(max_connections=config.global_upload_limit + config.global_download_limit),
        )

    async def close(self):
        await self.http.aclose()
