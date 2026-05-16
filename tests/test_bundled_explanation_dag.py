"""Explanation DAG export from bundled counterfactual chain samples."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATTR = ROOT / "artifacts" / "attribution_viewer"

_CHAIN_SAMPLES = (
    "sample_aggregate_chain_rumor_depeg.json",
    "sample_network_chain_contagion_base_panic.json",
    "sample_resource_cascade_chain_coupling_rumor.json",
    "sample_service_backlog_chain_process_ingest.json",
    "sample_liquidity_ladder_chain_margin_haircut.json",
)


@pytest.mark.parametrize("chain_file", _CHAIN_SAMPLES)
def test_explanation_dag_from_bundled_chain(chain_file: str) -> None:
    chain = ATTR / chain_file
    out = ATTR / f"_test_dag_{chain_file}"
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "export_explanation_dag.py"),
            "--from-counterfactual",
            str(chain),
            "--out",
            str(out),
        ],
        cwd=str(ROOT),
    )
    try:
        assert proc.returncode == 0, proc.stderr
        dag = json.loads(out.read_text(encoding="utf-8"))
        assert dag["schema"] == "explanation-dag-v1"
        assert dag.get("nodes")
    finally:
        if out.is_file():
            out.unlink()
