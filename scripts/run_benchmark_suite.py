"""Run frozen Phase H benchmark bundles (deterministic regression harness)."""

from __future__ import annotations

import argparse
import json
import sys

from fragility_engine.benchmarks import BUNDLE_IDS, run_benchmark_suite, validate_benchmark_suite


def main() -> None:
    ap = argparse.ArgumentParser(description="Execute benchmark-bundle suite (see benchmarks/README.md).")
    ap.add_argument(
        "--validate",
        action="store_true",
        help="Exit non-zero if any bundle deviates from golden metrics.",
    )
    ap.add_argument("--json", action="store_true", help="Print results as JSON array.")
    args = ap.parse_args()

    if args.validate:
        try:
            validate_benchmark_suite()
        except AssertionError as e:
            print(str(e), file=sys.stderr)
            raise SystemExit(1) from e
        if not args.json:
            print(f"OK: {len(BUNDLE_IDS)} bundles match golden metrics.")
        return

    results = run_benchmark_suite()
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for row in results:
            print(
                f"{row['bundle_id']}: integral={row['integral_instability']:.6f} "
                f"collapsed={row['collapsed']} mode={row['simulation_mode']}"
            )


if __name__ == "__main__":
    main()
