"""Fail if benchmark manifest inventory subset drifted without updating the pinned fixture.

Complements ``check_manifest_digest.py`` (golden metrics only). Run in CI after ``--validate``.
"""

from __future__ import annotations

import sys
from pathlib import Path

from fragility_engine.benchmarks.manifest import build_benchmark_manifest
from fragility_engine.benchmarks.manifest_inventory import manifest_inventory_sha256

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "benchmarks" / "manifest_inventory_sha256.txt"


def main() -> None:
    current = manifest_inventory_sha256(build_benchmark_manifest())
    if not FIXTURE.is_file():
        print(f"missing fixture: {FIXTURE}", file=sys.stderr)
        raise SystemExit(1)
    expected = FIXTURE.read_text(encoding="utf-8").strip()
    if current != expected:
        print(
            "manifest_inventory_sha256 mismatch:\n"
            f"  expected (fixture): {expected}\n"
            f"  current (code):     {current}\n"
            "Update tests/fixtures/benchmarks/manifest_inventory_sha256.txt if inventory changed intentionally.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    print(f"OK: manifest_inventory_sha256={current[:16]}...")


if __name__ == "__main__":
    main()
