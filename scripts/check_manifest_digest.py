"""Fail if benchmark golden-metrics digest drifted without updating the pinned fixture.

Run in CI after ``run_benchmark_suite.py --validate``. When ``GOLDEN_METRICS`` changes intentionally,
refresh ``tests/fixtures/benchmarks/golden_metrics_sha256.txt`` from the printed digest.
"""

from __future__ import annotations

import sys
from pathlib import Path

from fragility_engine.benchmarks.manifest import build_benchmark_manifest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "benchmarks" / "golden_metrics_sha256.txt"


def main() -> None:
    current = build_benchmark_manifest()["golden_metrics_sha256"]
    if not FIXTURE.is_file():
        print(f"missing fixture: {FIXTURE}", file=sys.stderr)
        raise SystemExit(1)
    expected = FIXTURE.read_text(encoding="utf-8").strip()
    if current != expected:
        print(
            "golden_metrics_sha256 mismatch:\n"
            f"  expected (fixture): {expected}\n"
            f"  current (code):     {current}\n"
            "Update tests/fixtures/benchmarks/golden_metrics_sha256.txt if GOLDEN_METRICS changed intentionally.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    print(f"OK: golden_metrics_sha256={current[:16]}...")


if __name__ == "__main__":
    main()
