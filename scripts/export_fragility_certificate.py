"""Emit ``fragility-certificate-v1`` JSON for frozen artifacts + environment fingerprints."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fragility_engine.benchmarks.certificate import build_fragility_certificate


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Write fragility-certificate-v1 (citation / reproducibility, not a legal certificate)."
    )
    ap.add_argument("--out", type=Path, required=True, help="Output JSON path.")
    ap.add_argument(
        "--digest-json",
        type=Path,
        nargs="*",
        default=(),
        help="Optional replay / Pareto / merge JSON files to include under artifact_sha256.",
    )
    ap.add_argument(
        "--validate-bundles",
        action="store_true",
        help="Run Phase H validate_benchmark_suite and embed pass/fail under benchmark_validation.",
    )
    ap.add_argument("--git-commit", type=str, default=None, help="Override git SHA (else env or git rev-parse).")
    ap.add_argument("--no-manifest", action="store_true", help="Omit benchmark_manifest block.")
    ap.add_argument("--notes", type=str, default="", help="Free-text disclaimer or run notes.")
    args = ap.parse_args()

    bench: dict | None = None
    if args.validate_bundles:
        from fragility_engine.benchmarks.suite import validate_benchmark_suite

        try:
            validate_benchmark_suite()
            bench = {"status": "passed", "gate": "validate_benchmark_suite"}
        except AssertionError as e:
            print(str(e), file=sys.stderr)
            bench = {"status": "failed", "error": str(e)[:2000]}
            raise SystemExit(1) from e

    cert = build_fragility_certificate(
        artifact_paths=list(args.digest_json) if args.digest_json else None,
        include_benchmark_manifest=not args.no_manifest,
        benchmark_validation=bench,
        git_commit=args.git_commit,
        notes=args.notes,
    )
    args.out.write_text(json.dumps(cert, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
