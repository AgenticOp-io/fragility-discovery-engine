"""Fail if any checked-in bundled demo JSON listed in bundled_artifacts.py is missing."""

from __future__ import annotations

import sys
from pathlib import Path

from fragility_engine.benchmarks.bundled_artifacts import BUNDLED_ARTIFACT_PATHS

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    missing: list[str] = []
    for rel in BUNDLED_ARTIFACT_PATHS:
        p = ROOT / rel
        if not p.is_file():
            missing.append(rel)
    if missing:
        for rel in missing:
            print(f"missing bundled artifact: {rel}", file=sys.stderr)
        print("Run: python scripts/regenerate_bundled_viewer_samples.py", file=sys.stderr)
        raise SystemExit(1)
    print(f"OK: {len(BUNDLED_ARTIFACT_PATHS)} bundled artifact paths exist")


if __name__ == "__main__":
    main()
