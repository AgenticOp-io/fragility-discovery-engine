#!/usr/bin/env python3
"""Emit fragility-certificate-v1 for coupled_institution research fork artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fragility_engine.benchmarks.certificate import build_fragility_certificate
from fragility_engine.benchmarks.coupled_fork import (
    coupled_fork_artifact_paths,
    run_coupled_fork_bundle_validation,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    p = argparse.ArgumentParser(description="fragility-certificate-v1 for coupled fork only.")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--notes", type=str, default="Research fork citation bundle (not main charter).")
    args = p.parse_args()

    fork_val = run_coupled_fork_bundle_validation(ROOT)
    if fork_val["status"] != "passed":
        print(fork_val.get("error", fork_val), file=sys.stderr)
        raise SystemExit(1)

    cert = build_fragility_certificate(
        research_fork_artifact_paths=coupled_fork_artifact_paths(ROOT),
        research_fork_validation=fork_val,
        include_benchmark_manifest=True,
        git_commit=None,
        repo_root=ROOT,
        notes=args.notes,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {"out": str(args.out), "research_fork_artifacts": len(coupled_fork_artifact_paths(ROOT))},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
