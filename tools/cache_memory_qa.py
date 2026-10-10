"""Fresh-process RSS/cache churn measurement; no network/account authentication.

Driver produces one Peer at a time and does not retain arrivals. Use the same
arguments/interpreter in separate installed baseline/current processes. This is
local SDK identity-cache retention, not messaging/service throughput or full load.
"""

import argparse
import asyncio
import ctypes
import gc
import json
from pathlib import Path
import platform
import statistics
import tempfile
import time

from fncbale import AccountPool, Peer, PeerKind, Session, __version__


def memory():
    if platform.system() == "Windows":
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
                (name, ctypes.c_size_t)
                for name in (
                    "PeakWorkingSetSize",
                    "WorkingSetSize",
                    "QuotaPeakPagedPoolUsage",
                    "QuotaPagedPoolUsage",
                    "QuotaPeakNonPagedPoolUsage",
                    "QuotaNonPagedPoolUsage",
                    "PagefileUsage",
                    "PeakPagefileUsage",
                    "PrivateUsage",
                )
            ]

        current = ctypes.windll.kernel32.GetCurrentProcess
        current.restype = wintypes.HANDLE
        read = ctypes.windll.psapi.GetProcessMemoryInfo
        read.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        read.restype = wintypes.BOOL
        counters = Counters(cb=ctypes.sizeof(Counters))
        if not read(current(), ctypes.byref(counters), counters.cb):
            raise ctypes.WinError()
        return {
            "rss_bytes": counters.WorkingSetSize,
            "peak_rss_bytes": counters.PeakWorkingSetSize,
            "private_commit_bytes": counters.PrivateUsage,
        }
    values = {}
    for line in Path("/proc/self/status").read_text().splitlines():
        name, _, value = line.partition(":")
        if name in ("VmRSS", "VmHWM"):
            values[name] = int(value.split()[0]) * 1024
    return {"rss_bytes": values["VmRSS"], "peak_rss_bytes": values["VmHWM"], "private_commit_bytes": None}


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--accounts", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=2048)
    parser.add_argument("--batches", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert 1 <= args.accounts <= 100 and args.batch_size > 0 and args.batches > 0
    result = {
        "version": __version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "accounts": args.accounts,
        "batch_size": args.batch_size,
        "batches": [],
        "before": memory(),
    }
    with tempfile.TemporaryDirectory(prefix="fncbale-cache-") as directory:
        root = Path(directory).resolve()
        assert root.parent == Path(tempfile.gettempdir()).resolve() and root.name.startswith("fncbale-cache-")
        pool = AccountPool(data_dir=root)
        clients = [pool.add(str(index), Session(index + 1, "synthetic")) for index in range(args.accounts)]
        try:
            gc.collect()
            result["initialized"] = memory()
            for batch in range(args.batches):
                started = time.perf_counter()
                for client in clients:
                    for index in range(batch * args.batch_size, (batch + 1) * args.batch_size):
                        peer = Peer(PeerKind.CHANNEL, index + 1, index + 11, username="qa" + str(index + 1))
                        client._cache_peer(peer)
                samples = []
                for client in clients:
                    for offset in range(8):
                        number = (batch + 1) * args.batch_size - offset
                        begin = time.perf_counter_ns()
                        resolved = await client.resolve_peer(number)
                        samples.append((time.perf_counter_ns() - begin) / 1000)
                        assert resolved.id == number and resolved.access_hash == number + 10
                peers = sum(sum(not key.startswith("@") for key in client._peer_cache) for client in clients)
                aliases = sum(sum(key.startswith("@") for key in client._peer_cache) for client in clients)
                gc.collect()
                case = {
                    "arrivals_per_account": (batch + 1) * args.batch_size,
                    "retained_peers": peers,
                    "retained_aliases": aliases,
                    "seconds_including_driver_probes_gc": time.perf_counter() - started,
                    "numeric_lookup_median_us": statistics.median(samples),
                    **memory(),
                }
                result["batches"].append(case)
                print(json.dumps(case), flush=True)
            result["configured_identity_limit"] = getattr(pool.config, "peer_cache_size", None)
            if result["configured_identity_limit"] is not None:
                assert all(
                    case["retained_peers"] <= args.accounts * result["configured_identity_limit"]
                    and case["retained_aliases"] <= case["retained_peers"]
                    for case in result["batches"]
                )
        finally:
            await pool.close()
        gc.collect()
        result["after_close_retained_keys"] = sum(len(client._peer_cache) for client in clients)
        result["after_close"] = memory()
    result["pass"] = True
    result["scope"] = (
        "Fresh process, real AccountPool/Clients and actual OS RSS/HWM, synthetic cache-only arrivals; no network/auth/WS/SQLite traffic/media loads/real-server throughput. One arrival retained by driver at a time; Python allocator/import/client/model overhead is included. RSS after close can retain allocator arenas. Baseline is measured, not acceptance of unbounded retention."
    )
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
