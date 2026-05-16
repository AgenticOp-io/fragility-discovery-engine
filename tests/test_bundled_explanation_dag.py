"""Explanation DAG export from bundled counterfactual samples."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGG_CHAIN = ROOT / "artifacts/attribution_viewer/sample_aggregate_chain_rumor_depeg.json"


def test_explanation_dag_from_bundled_aggregate_chain() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "export_explanation_dag.py"),
            "--from-counterfactual",
            str(AGG_CHAIN),
            "--out",
            str(ROOT / "artifacts" / "attribution_viewer" / "_test_dag_out.json"),
        ],
        cwd=str(ROOT),
    )
    out = ROOT / "artifacts" / "attribution_viewer" / "_test_dag_out.json"
    try:
        assert proc.returncode == 0, proc.stderr
        dag = json.loads(out.read_text(encoding="utf-8"))
        assert dag["schema"] == "explanation-dag-v1"
        assert dag.get("nodes")
    finally:
        if out.is_file():
            out.unlink()
