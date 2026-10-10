import json
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.parametrize("method", ["disconnect", "close", "pool-close"])
def test_shutdown_from_handler_breaks_cancellation_cycle_and_preserves_inbox(tmp_path, method):
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "helpers/callback_shutdown.py"), str(tmp_path), method],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0
    receipt = json.loads(result.stdout)
    assert receipt["pass"], receipt
    assert receipt["cleanup_joined"] and receipt["pending_id_preserved"] and not receipt["loop_errors"]
