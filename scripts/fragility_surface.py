"""2D fragility scan (Phase F-lite): classify collapse under zero shocks across parameters."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import rollout_stablecoin
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    ap = argparse.ArgumentParser(description="Grid scan for collapse classification (no adversary shocks).")
    ap.add_argument("--out", type=Path, default=Path("fragility_surface.csv"))
    ap.add_argument("--seed", type=int, default=777)
    ap.add_argument("--steps", type=int, default=64)
    args = ap.parse_args()

    panic_axis = np.linspace(0.02, 0.55, 14)
    depeg_axis = np.linspace(0.88, 0.98, 14)
    genome = np.zeros((args.steps, 2), dtype=np.float64)

    rows: list[dict[str, float | int]] = []
    for pi, ip in enumerate(panic_axis):
        for dj, dt in enumerate(depeg_axis):
            world = StablecoinPegWorld(
                population=default_stablecoin_population(),
                depeg_threshold=float(dt),
                max_steps=args.steps,
            )
            rr = rollout_stablecoin(
                world,
                genome,
                seed=args.seed + pi * 97 + dj,
                initial_panic=float(ip),
            )
            rows.append(
                {
                    "panic0": float(ip),
                    "depeg_threshold": float(dt),
                    "collapsed": int(rr.collapsed),
                    "collapse_t": int(rr.collapse_timestep if rr.collapse_timestep is not None else -1),
                    "peak_instability": float(rr.final_instability),
                }
            )

    with args.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
