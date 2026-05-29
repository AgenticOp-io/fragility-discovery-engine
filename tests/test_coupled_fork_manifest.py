"""Research fork bundle validation (non-charter)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_lists_research_fork_bundle() -> None:
    from fragility_engine.benchmarks.manifest import build_benchmark_manifest

    manifest = build_benchmark_manifest()
    forks = manifest.get("research_fork_bundles") or []
    ids = [f["bundle_id"] for f in forks if isinstance(f, dict)]
    assert "coupled_institution_rollout_v1" in ids


def test_validate_coupled_fork_bundle_cli() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_coupled_fork_bundle.py")],
        cwd=str(ROOT),
        check=True,
    )


def test_coupled_sweep_artifact_schema() -> None:
    path = ROOT / "forks" / "coupled_institution" / "artifacts" / "coupling_strength_sweep.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema"] == "coupled-institution-coupling-sweep-v1"
    assert len(data.get("rows") or []) >= 3
