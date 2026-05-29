#!/usr/bin/env python3
"""Run the coupled_institution research fork from the repo root (GA or regenerate sample)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORK = ROOT / "forks" / "coupled_institution"
GA = FORK / "scripts" / "run_coupled_ga_demo.py"
REGEN = FORK / "scripts" / "regenerate_golden.py"


def main() -> None:
    p = argparse.ArgumentParser(
        description="Coupled peg and overload fork (not main charter). Regenerate sample or run GA."
    )
    p.add_argument(
        "--regenerate",
        action="store_true",
        help="Write forks/coupled_institution/artifacts/sample_coupled_replay.json from pinned fixture.",
    )
    p.add_argument(
        "--export-replay",
        type=Path,
        default=None,
        help="Path for fork replay JSON after GA (coupled-fork-0.1.0 schema).",
    )
    p.add_argument("--generations", type=int, default=8)
    p.add_argument("--population-size", type=int, default=16)
    p.add_argument("--seed", type=int, default=1201)
    p.add_argument("--coupling", type=float, default=0.3)
    p.add_argument("--horizon", type=int, default=14)
    args = p.parse_args()

    if not FORK.is_dir():
        print(f"Missing fork package: {FORK}", file=sys.stderr)
        raise SystemExit(1)

    if args.regenerate:
        subprocess.run([sys.executable, str(REGEN)], cwd=FORK, check=True)
        print("OK: regenerated sample_coupled_replay.json", file=sys.stderr)
        return

    cmd = [
        sys.executable,
        str(GA),
        "--generations",
        str(args.generations),
        "--population-size",
        str(args.population_size),
        "--seed",
        str(args.seed),
        "--coupling",
        str(args.coupling),
        "--horizon",
        str(args.horizon),
    ]
    if args.export_replay:
        cmd.extend(["--export-replay", str(args.export_replay)])
    subprocess.run(cmd, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
