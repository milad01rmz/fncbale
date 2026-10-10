import asyncio

import pytest

from fncbale import Config
from fncbale.resources import Resources


@pytest.mark.parametrize("value", [1.5, float("nan"), float("inf"), True])
def test_noninteger_rpc_limit_is_rejected_before_resource_creation(value):
    with pytest.raises((TypeError, ValueError)):
        Config(global_rpc_limit=value)


@pytest.mark.parametrize("field", ["rpc_timeout", "commit_window", "peer_cache_ttl"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_time_configuration_is_rejected(field, value):
    with pytest.raises((TypeError, ValueError)):
        Config(**{field: value})


async def test_integer_pool_limit_really_blocks_and_releases_waiter():
    resources = Resources(Config(global_rpc_limit=2))
    try:
        await resources.rpc_limit.acquire()
        await resources.rpc_limit.acquire()
        entered = asyncio.Event()

        async def wait():
            entered.set()
            async with resources.rpc_limit:
                return True

        task = asyncio.create_task(wait())
        await entered.wait()
        await asyncio.sleep(0)
        assert not task.done()
        resources.rpc_limit.release()
        assert await asyncio.wait_for(task, 3)
        resources.rpc_limit.release()
    finally:
        await resources.close()


def test_timing_zero_policy_and_retry_policy_snapshot():
    methods = {"CallerVerifiedMethod"}
    config = Config(commit_window=0, peer_cache_ttl=0, rpc_timeout=0.5, verified_idempotent_methods=methods)
    methods.add("SendMessage")
    assert config.verified_idempotent_methods == frozenset({"CallerVerifiedMethod"})
    with pytest.raises(ValueError):
        Config(rpc_timeout=0)
    with pytest.raises(TypeError):
        Config(verified_idempotent_methods="SendMessage")
    with pytest.raises(TypeError):
        Config(verified_idempotent_methods={""})


@pytest.mark.parametrize("field", ["queue_size", "upload_limit", "outbox_workers", "stream_chunk_size"])
def test_worker_queue_and_buffer_counts_require_positive_integers(field):
    with pytest.raises(TypeError):
        Config(**{field: 1.5})
    with pytest.raises(ValueError):
        Config(**{field: 0})
