"""Shared coupled fork benchmark helpers."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fragility_engine.benchmarks.coupled_fork import (
    COUPLED_FORK_ARTIFACT_NAMES,
    coupled_fork_artifact_paths,
    coupled_fork_artifacts_dir,
)

ROOT = Path(__file__).resolve().parents[1]


def test_coupled_fork_artifact_paths_match_checked_in_names() -> None:
    art = coupled_fork_artifacts_dir(ROOT)
    assert art.is_dir()
    paths = coupled_fork_artifact_paths(ROOT)
    names = {p.name for p in paths}
    for n in COUPLED_FORK_ARTIFACT_NAMES:
        if (art / n).is_file():
            assert n in names


def test_refresh_flagship_bundled_certificate_cli() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "refresh_flagship_bundled_certificate.py")],
        cwd=str(ROOT),
        check=True,
    )
    cert = json.loads((ROOT / "artifacts" / "flagship" / "bundled" / "fragility_certificate.json").read_text())
    assert cert.get("research_fork_validation", {}).get("status") == "passed"
    assert cert.get("research_fork_validation", {}).get("tetra_bundle_id") == (
        "coupled_institution_tetra_rollout_v1"
    )
    rows = cert.get("research_fork_artifact_sha256") or []
    assert len(rows) >= 6
    paths = {r.get("path", "") for r in rows}
    assert any(p.endswith("sample_coupled_tetra_replay.json") for p in paths)
