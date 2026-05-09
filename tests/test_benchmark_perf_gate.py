"""Wall-clock ceiling on benchmark_rollout.

Skipped locally unless ``FRAGILITY_PERF_GATE=1``. CI enables this via ``.github/workflows/ci.yml``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.skipif(
    os.environ.get("FRAGILITY_PERF_GATE") != "1",
    reason="Set FRAGILITY_PERF_GATE=1 to run perf gate locally or in CI.",
)
def test_benchmark_rollout_network_under_ceiling() -> None:
    py_exe = sys.executable
    ceiling_ms = float(os.environ.get("FRAGILITY_PERF_GATE_MS", "120000"))
    proc = subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "benchmark_rollout.py"),
            "--mode",
            "network",
            "--nodes",
            "24",
            "--repeat",
            "4",
            "--warmup",
            "1",
            "--max-steps",
            "24",
            "--horizon",
            "12",
            "--json",
        ],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert data["mean_ms_per_rollout"] <= ceiling_ms
