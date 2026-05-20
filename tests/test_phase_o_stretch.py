"""Phase O stretch CLI smokes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *argv],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def test_inventory_buffer_bundle_in_suite():
    from fragility_engine.benchmarks.suite import BUNDLE_IDS

    assert "inventory_buffer_rollout_v1" in BUNDLE_IDS


def test_fragility_robustness_stretch_dry_run():
    proc = _run(
        [
            str(ROOT / "scripts" / "fragility_robustness_stretch.py"),
            "--preset",
            "small",
            "--dry-run",
        ]
    )
    assert proc.returncode == 0, proc.stderr
    assert "fragility-robustness-stretch-v1" in proc.stdout


def test_export_static_dashboard(tmp_path: Path):
    out = tmp_path / "dash.html"
    proc = _run([str(ROOT / "scripts" / "export_static_dashboard.py"), "--out", str(out)])
    assert proc.returncode == 0, proc.stderr
    assert out.is_file()
    assert "Replay timeline" in out.read_text(encoding="utf-8")


def test_institutional_composite_hexa_cli():
    proc = _run(
        [
            str(ROOT / "scripts" / "institutional_composite_demo.py"),
            "--hexa",
            "--horizon",
            "6",
        ]
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["schema"] == "fragility-institutional-composite-v5"
    assert "inventory_buffer" in data
