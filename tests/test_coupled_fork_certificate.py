"""Coupled fork fragility-certificate integration."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_export_coupled_fork_certificate_cli(tmp_path: Path) -> None:
    out = tmp_path / "fork_cert.json"
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "export_coupled_fork_certificate.py"), "--out", str(out)],
        cwd=str(ROOT),
        check=True,
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "fragility-certificate-v1"
    assert data["research_fork_validation"]["status"] == "passed"
    assert data["research_fork_validation"].get("tetra_bundle_id") == (
        "coupled_institution_tetra_rollout_v1"
    )
    rows = data.get("research_fork_artifact_sha256") or []
    assert len(rows) >= 6
    paths = {r.get("path", "") for r in rows}
    assert any(p.endswith("sample_coupled_tetra_replay.json") for p in paths)
    assert any(p.endswith("worth_it_bar.json") for p in paths)


def test_export_fragility_certificate_research_fork_flag(tmp_path: Path) -> None:
    out = tmp_path / "cert.json"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "export_fragility_certificate.py"),
            "--out",
            str(out),
            "--research-fork",
            "--no-manifest",
        ],
        cwd=str(ROOT),
        check=True,
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["research_fork_validation"]["status"] == "passed"
    assert data.get("research_fork_artifact_sha256")
