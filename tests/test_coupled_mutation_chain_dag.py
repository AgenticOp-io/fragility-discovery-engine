"""Export explanation-dag-v1 from coupled fork mutation-chain path_trace."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAIN = ROOT / "forks" / "coupled_institution" / "artifacts" / "sample_coupled_mutation_chain.json"


def test_export_mutation_chain_explanation_dag(tmp_path: Path) -> None:
    if not CHAIN.is_file():
        return
    out = tmp_path / "chain.dag.json"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "export_explanation_dag.py"),
            "--from-mutation-chain",
            str(CHAIN),
            "--out",
            str(out),
        ],
        cwd=ROOT,
        check=True,
    )
    dag = json.loads(out.read_text(encoding="utf-8"))
    assert dag["schema"] == "explanation-dag-v1"
    assert dag["kind"] == "mutation_chain_path"
    assert len(dag["nodes"]) >= 2
    assert len(dag["edges"]) >= 1
