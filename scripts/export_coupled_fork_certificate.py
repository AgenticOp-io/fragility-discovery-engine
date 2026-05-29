#!/usr/bin/env python3
"""Emit fragility-certificate-v1 for coupled_institution research fork artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from fragility_engine.benchmarks.certificate import build_fragility_certificate

ROOT = Path(__file__).resolve().parents[1]
FORK_ART = ROOT / "forks" / "coupled_institution" / "artifacts"


def _fork_artifact_paths() -> list[Path]:
    names = (
        "sample_coupled_replay.json",
        "coupling_strength_sweep.json",
        "sample_coupling_comparison.json",
        "sample_coupled_mutation_chain.json",
    )
    return [FORK_ART / n for n in names if (FORK_ART / n).is_file()]


def main() -> None:
    p = argparse.ArgumentParser(description="fragility-certificate-v1 for coupled fork only.")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--notes", type=str, default="Research fork citation bundle (not main charter).")
    args = p.parse_args()

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_coupled_fork_bundle.py")],
        cwd=str(ROOT),
        check=True,
    )

    cert = build_fragility_certificate(
        research_fork_artifact_paths=_fork_artifact_paths(),
        research_fork_validation={
            "status": "passed",
            "bundle_id": "coupled_institution_rollout_v1",
        },
        include_benchmark_manifest=True,
        git_commit=None,
        repo_root=ROOT,
        notes=args.notes,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "research_fork_artifacts": len(_fork_artifact_paths())}, indent=2))


if __name__ == "__main__":
    main()
