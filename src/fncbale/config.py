from dataclasses import dataclass, field
import math


@dataclass(frozen=True, slots=True)
class ProtocolProfile:
    websocket_url: str = "wss://next-ws.bale.ai/ws/"
    grpc_url: str = "https://next-ws.bale.ai"
    origin: str = "https://web.bale.ai"
    app_version: str = "173855"
    browser_version: str = "138.0.0.0"
    browser_type: str = "1"
    os_type: str = "3"
    language: str = "fa"
    # Public application credential observed in the current web auth contract.
    app_id: int = 4
    api_key: str = field(
        default="C28D46DC4C3A7A26564BFCC48B929086A95C93C98E789A19847BEE8627DE4E7D", repr=False
    )


@dataclass(frozen=True, slots=True)
class Config:
    profile: ProtocolProfile = field(default_factory=ProtocolProfile)
    rpc_limit: int = 32
    global_rpc_limit: int = 256
    upload_limit: int = 2
    global_upload_limit: int = 8
    download_limit: int = 4
    global_download_limit: int = 16
    metadata_workers: int = 4
    rpc_timeout: float = 20
    upload_timeout: float = 120
    heartbeat_interval: float = 15
    recovery_interval: float = 30
    peer_cache_ttl: float = 900
    peer_cache_size: int = 1024
    queue_size: int = 256
    outbox_limit: int = 4096
    outbox_workers: int = 8
    handler_attempts: int = 3
    retention_days: int = 7
    commit_window: float = 0.003
    max_frame_size: int = 32 * 1024 * 1024
    stream_chunk_size: int = 262144
    # These must be populated only after cross-route duplicate tests for this profile.
    verified_idempotent_methods: frozenset[str] = frozenset()

    def __post_init__(self):
        counts = (
            "rpc_limit",
            "global_rpc_limit",
            "upload_limit",
            "global_upload_limit",
            "download_limit",
            "global_download_limit",
            "metadata_workers",
            "peer_cache_size",
            "queue_size",
            "outbox_limit",
            "outbox_workers",
            "handler_attempts",
            "retention_days",
            "max_frame_size",
            "stream_chunk_size",
        )
        for name in counts:
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{name} must be an integer")
            if value < 1:
                raise ValueError(f"{name} must be positive")
        for name in (
            "rpc_timeout",
            "upload_timeout",
            "heartbeat_interval",
            "recovery_interval",
            "peer_cache_ttl",
            "commit_window",
        ):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be a finite number")
            try:
                finite = math.isfinite(value)
            except OverflowError:
                finite = False
            if not finite or value < 0 or (value == 0 and name not in ("peer_cache_ttl", "commit_window")):
                raise ValueError(f"{name} is outside its finite timing range")
        methods = self.verified_idempotent_methods
        if not isinstance(methods, (frozenset, set, tuple, list)) or any(
            not isinstance(name, str) or not name or name.strip() != name for name in methods
        ):
            raise TypeError("verified_idempotent_methods must contain nonempty method names")
        object.__setattr__(self, "verified_idempotent_methods", frozenset(methods))
