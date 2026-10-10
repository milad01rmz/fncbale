from tools.mixed_pool_qa import scenario


async def test_concurrent_pool_traffic_stream_faults_and_durable_restart():
    result = await scenario(
        accounts=6,
        rounds=2,
        controlled_overlap=True,
        measure_memory=True,
        photo_size=(768, 512),
        stream_chunk_size=262144,
    )
    assert result["operations"] == result["confirmed"] == 78
    assert result["inbox"] == result["acked"] == result["delivered_unique"]
    assert result["independent_file_hashes"] == 24
    assert result["restart_accepted_operations"] == 6
    assert result["accepted_write_reissues"] == 0
    assert all(result["actual_overlap"].values())
    measurements = result["process_memory"]
    assert measurements["enabled"] and measurements["sample_count"] > 0
    assert measurements["sampled_rss_peak_bytes"] > 0
    assert 0 < len(measurements["samples"]) <= 512
    assert measurements["stages"]["closed_model_retained"]["sdk_retained_peer_keys"] == 0
    assert all(size > result["sdk_stream_chunk_size"] for size in result["input_file_sizes"])
