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
        help="Path for fork replay JSON after GA (coupled-fork-0.4.0 schema).",
    )
    p.add_argument(
        "--export-pareto",
        type=Path,
        default=None,
        help="Write pareto-front-v1 JSON after GA (same search budget as replay).",
    )
    p.add_argument("--generations", type=int, default=8)
    p.add_argument("--population-size", type=int, default=16)
    p.add_argument("--seed", type=int, default=1201)
    p.add_argument("--coupling", type=float, default=0.3)
    p.add_argument("--horizon", type=int, default=14)
    p.add_argument("--contract", choices=("default", "triad", "tetra"), default="default")
    p.add_argument("--method", choices=("ga", "mc"), default="ga")
    p.add_argument("--samples", type=int, default=40)
    args = p.parse_args()

    if not FORK.is_dir():
        print(f"Missing fork package: {FORK}", file=sys.stderr)
        raise SystemExit(1)

    if args.regenerate:
        subprocess.run([sys.executable, str(REGEN)], cwd=FORK, check=True)
        print("OK: regenerated sample_coupled_replay.json (+ tetra)", file=sys.stderr)
        return

    cmd = [
        sys.executable,
        str(GA),
        "--method",
        args.method,
        "--contract",
        args.contract,
        "--generations",
        str(args.generations),
        "--population-size",
        str(args.population_size),
        "--samples",
        str(args.samples),
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
    if args.export_pareto:
        if args.method != "ga":
            print("export-pareto requires --method ga", file=sys.stderr)
            raise SystemExit(2)
        pareto_cmd = [
            sys.executable,
            str(ROOT / "scripts" / "export_coupled_fork_pareto.py"),
            "--out",
            str(args.export_pareto),
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
            "--contract",
            args.contract,
        ]
        subprocess.run(pareto_cmd, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
