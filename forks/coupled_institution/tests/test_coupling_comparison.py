"""Coupling comparison attribution-style JSON."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_export_coupling_comparison_cli(tmp_path: Path) -> None:
    out = tmp_path / "cmp.json"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "export_coupling_comparison.py"),
            "--out",
            str(out),
        ],
        cwd=ROOT,
        check=True,
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "coupled-institution-coupling-comparison-v1"
    assert "baseline" in data and "variant" in data
