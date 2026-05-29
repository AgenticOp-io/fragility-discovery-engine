"""Coupling strength sweep artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_coupling_strength_sweep_cli(tmp_path: Path) -> None:
    out = tmp_path / "sweep.json"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "coupling_strength_sweep.py"),
            "--out",
            str(out),
            "--strengths",
            "0,0.3,0.6",
        ],
        cwd=ROOT,
        check=True,
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "coupled-institution-coupling-sweep-v1"
    assert len(data["rows"]) == 3
    assert data["rows"][0]["coupling_strength"] == 0.0
