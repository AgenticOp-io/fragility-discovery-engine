"""gce_write_workbench_status.py includes research fork validation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_gce_write_workbench_status_includes_research_fork(tmp_path: Path) -> None:
    out = tmp_path / "status.json"
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "gce_write_workbench_status.py"), "--out", str(out)],
        cwd=str(ROOT),
        check=True,
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "fragility-workbench-status-v1"
    assert data["benchmark_validate"] == "ok"
    assert data["research_fork_validate"] == "ok"
    assert data["research_fork_bundle_id"] == "coupled_institution_rollout_v1"
