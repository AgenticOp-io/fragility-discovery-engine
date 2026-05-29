#!/usr/bin/env python3
"""Recompute ``fragility_certificate.json`` in flagship/bundled without re-running GA."""

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
BUNDLED = ROOT / "artifacts" / "flagship" / "bundled"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--no-research-fork",
        action="store_true",
        help="Omit research_fork_* blocks (main charter replay/pareto only).",
    )
    args = ap.parse_args()

    replay = BUNDLED / "best_replay.json"
    pareto = BUNDLED / "pareto_front.json"
    cert_path = BUNDLED / "fragility_certificate.json"
    for p in (replay, pareto, cert_path):
        if not p.is_file():
            print(f"missing: {p}", file=sys.stderr)
            raise SystemExit(1)

    old = json.loads(cert_path.read_text(encoding="utf-8"))
    fork_val = None
    fork_paths: list[Path] = []
    if not args.no_research_fork:
        fork_val = run_coupled_fork_bundle_validation(ROOT)
        if fork_val["status"] != "passed":
            print(fork_val.get("error", fork_val), file=sys.stderr)
            raise SystemExit(1)
        fork_paths = coupled_fork_artifact_paths(ROOT)
        if len(fork_paths) < 3:
            print("expected at least 3 coupled fork artifacts", file=sys.stderr)
            raise SystemExit(1)

    cert = build_fragility_certificate(
        artifact_paths=[replay, pareto],
        include_benchmark_manifest=True,
        benchmark_validation=old.get("benchmark_validation"),
        research_fork_validation=fork_val,
        research_fork_artifact_paths=fork_paths or None,
        flagship_run=old.get("flagship_run"),
        repo_root=ROOT,
        notes=old.get(
            "notes",
            "Synthetic flagship bundle for reviewer walkthrough; not a forecast of any real institution.",
        ),
    )
    cert_path.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")
    fork_n = len(cert.get("research_fork_artifact_sha256") or [])
    print(
        json.dumps(
            {
                "out": str(cert_path.relative_to(ROOT)),
                "certificate_content_sha256": cert["certificate_content_sha256"],
                "research_fork_artifacts": fork_n,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
