"""2D fragility scan (Phase F-lite): classify collapse under zero shocks across parameters."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import rollout_stablecoin
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def run_fragility_surface_grid(
    *,
    seed: int,
    steps: int,
    panic_axis: np.ndarray,
    depeg_axis: np.ndarray,
) -> list[dict[str, float | int]]:
    """Deterministic grid: zero adversary genome, vary initial panic and depeg threshold."""
    rows: list[dict[str, float | int]] = []
    genome = np.zeros((steps, 2), dtype=np.float64)

    for pi, ip in enumerate(panic_axis):
        for dj, dt in enumerate(depeg_axis):
            world = StablecoinPegWorld(
                population=default_stablecoin_population(),
                depeg_threshold=float(dt),
                max_steps=steps,
            )
            rr = rollout_stablecoin(
                world,
                genome,
                seed=seed + pi * 97 + dj,
                initial_panic=float(ip),
            )
            rows.append(
                {
                    "panic0": float(ip),
                    "depeg_threshold": float(dt),
                    "collapsed": int(rr.collapsed),
                    "collapse_t": int(rr.collapse_timestep if rr.collapse_timestep is not None else -1),
                    "peak_instability": float(rr.final_instability),
                    "integral_instability": float(rr.integral_instability),
                }
            )
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description="Grid scan for collapse classification (no adversary shocks).")
    ap.add_argument("--out", type=Path, default=Path("fragility_surface.csv"))
    ap.add_argument("--seed", type=int, default=777)
    ap.add_argument("--steps", type=int, default=64)
    ap.add_argument("--panic-min", type=float, default=0.02)
    ap.add_argument("--panic-max", type=float, default=0.55)
    ap.add_argument("--panic-points", type=int, default=14, help="Linspace resolution for initial panic axis.")
    ap.add_argument("--depeg-min", type=float, default=0.88)
    ap.add_argument("--depeg-max", type=float, default=0.98)
    ap.add_argument("--depeg-points", type=int, default=14, help="Linspace resolution for depeg threshold axis.")
    args = ap.parse_args()

    if args.panic_points < 2 or args.depeg_points < 2:
        raise SystemExit("--panic-points and --depeg-points must be >= 2.")
    if args.panic_min >= args.panic_max or args.depeg_min >= args.depeg_max:
        raise SystemExit("Axis min must be < max for both panic and depeg ranges.")

    panic_axis = np.linspace(float(args.panic_min), float(args.panic_max), int(args.panic_points))
    depeg_axis = np.linspace(float(args.depeg_min), float(args.depeg_max), int(args.depeg_points))
    rows = run_fragility_surface_grid(seed=args.seed, steps=args.steps, panic_axis=panic_axis, depeg_axis=depeg_axis)

    with args.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
