"""Fail if benchmark manifest log summary text drifted without updating the pinned fixture."""

from __future__ import annotations

import sys
from pathlib import Path

from fragility_engine.benchmarks.manifest import manifest_summary_sha256

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "benchmarks" / "manifest_summary_sha256.txt"


def main() -> None:
    current = manifest_summary_sha256()
    if not FIXTURE.is_file():
        print(f"missing fixture: {FIXTURE}", file=sys.stderr)
        raise SystemExit(1)
    expected = FIXTURE.read_text(encoding="utf-8").strip()
    if current != expected:
        print(
            "manifest_summary_sha256 mismatch:\n"
            f"  expected (fixture): {expected}\n"
            f"  current (code):     {current}\n"
            "Update tests/fixtures/benchmarks/manifest_summary_sha256.txt if pinned summary fields changed.\n"
            "(Pinned digest excludes git_commit and runtime fields; CLI --manifest-summary still prints them.)\n"
            "Re-run: python -c \"from scripts.check_manifest_summary import manifest_summary_sha256; "
            "print(manifest_summary_sha256())\"",
            file=sys.stderr,
        )
        raise SystemExit(1)
    print(f"OK: manifest_summary_sha256={current[:16]}...")


if __name__ == "__main__":
    main()
