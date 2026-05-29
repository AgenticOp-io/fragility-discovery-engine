"""Coupled fork mutation chain path."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAIN = ROOT / "tests" / "fixtures" / "coupling_chain.json"


def test_export_coupled_mutation_chain_cli(tmp_path: Path) -> None:
    out = tmp_path / "chain.json"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "export_coupled_mutation_chain.py"),
            "--chain-json",
            str(CHAIN),
            "--out",
            str(out),
        ],
        cwd=ROOT,
        check=True,
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["path_trace"]["schema"] == "explanation-mutation-chain-path-coupled-institution-v1"
    assert len(data["path_trace"]["nodes"]) == 4
