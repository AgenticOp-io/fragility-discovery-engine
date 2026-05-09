"""Light subprocess smoke for CLI scripts (repo root as cwd)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def py_exe() -> str:
    return sys.executable


def test_week1_smoke_exports_replay(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "w.json"
    subprocess.run(
        [py_exe, str(ROOT / "scripts" / "week1_smoke.py"), "--export-replay", str(out)],
        check=True,
        cwd=str(ROOT),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema_version"]
    assert data["meta"]["cli"] == "week1_smoke"
    assert data["trajectory"]


def test_fragility_surface_cli_minimal_grid(py_exe: str, tmp_path: Path) -> None:
    out = tmp_path / "g.csv"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "fragility_surface.py"),
            "--out",
            str(out),
            "--panic-points",
            "3",
            "--depeg-points",
            "3",
            "--steps",
            "8",
        ],
        check=True,
        cwd=str(ROOT),
    )
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 10
    assert "integral_instability" in lines[0]


def test_export_counterfactual_writes_replay_pair(py_exe: str, tmp_path: Path) -> None:
    out_json = tmp_path / "cf.json"
    repdir = tmp_path / "replays"
    subprocess.run(
        [
            py_exe,
            str(ROOT / "scripts" / "export_counterfactual.py"),
            "--out",
            str(out_json),
            "--export-replay-dir",
            str(repdir),
            "--horizon",
            "10",
            "--remove",
            "0",
            "--seed",
            "11",
            "--genome-seed",
            "12",
        ],
        check=True,
        cwd=str(ROOT),
    )
    assert out_json.is_file()
    b = json.loads((repdir / "baseline.json").read_text(encoding="utf-8"))
    c = json.loads((repdir / "counterfactual.json").read_text(encoding="utf-8"))
    assert b["meta"]["variant"] == "baseline"
    assert c["meta"]["variant"] == "counterfactual"
