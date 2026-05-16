"""Bundled artifact registry and check script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from fragility_engine.benchmarks.bundled_artifacts import BUNDLED_ARTIFACT_PATHS

ROOT = Path(__file__).resolve().parents[1]


def test_bundled_registry_paths_exist() -> None:
    for rel in BUNDLED_ARTIFACT_PATHS:
        assert (ROOT / rel).is_file(), rel


def test_check_bundled_artifacts_script() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_bundled_artifacts.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "OK:" in proc.stdout
