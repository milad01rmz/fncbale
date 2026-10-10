from tools.multiaccount_qa import scenario


async def test_shared_pool_media_faults_and_paginated_recovery_are_account_isolated():
    result = await scenario(accounts=4, rounds=2)
    assert result["accounts"] == 4 and result["operations"] == 28
    assert result["inbox"] == result["acked"]
    assert result["pending_leaks"] == 0 and result["max_parallel_rpc"] <= result["rpc_limit"]
