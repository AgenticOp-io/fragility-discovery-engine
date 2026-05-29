#!/usr/bin/env python3
"""Regenerate coupled fork golden replay and copy into replay_viewer for site builds."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORK = ROOT / "forks" / "coupled_institution"
SAMPLE = FORK / "artifacts" / "sample_coupled_replay.json"
VIEWER_COPY = ROOT / "artifacts" / "replay_viewer" / "sample_coupled_institution_replay.json"
ATTR_COPY = ROOT / "artifacts" / "attribution_viewer" / "sample_coupled_mutation_chain.json"


def main() -> None:
    regen = FORK / "scripts" / "regenerate_golden.py"
    subprocess.run([sys.executable, str(regen)], cwd=FORK, check=True)
    subprocess.run(
        [sys.executable, str(FORK / "scripts" / "coupling_strength_sweep.py")],
        cwd=FORK,
        check=True,
    )
    subprocess.run(
        [sys.executable, str(FORK / "scripts" / "export_coupling_comparison.py")],
        cwd=FORK,
        check=True,
    )
    subprocess.run(
        [sys.executable, str(FORK / "scripts" / "export_coupled_mutation_chain.py")],
        cwd=FORK,
        check=True,
    )
    if not SAMPLE.is_file():
        raise SystemExit(f"Expected {SAMPLE} after regenerate")
    VIEWER_COPY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SAMPLE, VIEWER_COPY)
    chain = FORK / "artifacts" / "sample_coupled_mutation_chain.json"
    if chain.is_file():
        ATTR_COPY.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(chain, ATTR_COPY)
    print(f"OK: {SAMPLE.relative_to(ROOT)}")
    print(f"OK: {VIEWER_COPY.relative_to(ROOT)}")
    if ATTR_COPY.is_file():
        print(f"OK: {ATTR_COPY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
