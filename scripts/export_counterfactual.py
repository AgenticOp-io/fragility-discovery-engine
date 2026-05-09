"""Export a counterfactual attribution bundle as JSON (pinned seeds)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import counterfactual_bundle_to_jsonable, counterfactual_remove_steps
from fragility_engine.runner import rollout_stablecoin
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    ap = argparse.ArgumentParser(description="Export counterfactual JSON (drop shock timesteps, same seed).")
    ap.add_argument("--out", type=Path, default=Path("counterfactual.json"))
    ap.add_argument("--seed", type=int, default=424242)
    ap.add_argument("--horizon", type=int, default=28)
    ap.add_argument("--remove", type=str, default="0,1,2", help="Comma-separated timestep indices to zero out.")
    ap.add_argument("--genome-seed", type=int, default=7, help="RNG seed for random attacker genome.")
    args = ap.parse_args()

    remove_ts = [int(x.strip()) for x in args.remove.split(",") if x.strip() != ""]
    rng = np.random.default_rng(args.genome_seed)
    genome = rng.uniform(size=(args.horizon, 2))

    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=max(args.horizon, 32))

    def evaluator(g: np.ndarray, s: int):
        return rollout_stablecoin(template, g, seed=s)

    report = counterfactual_remove_steps(genome, evaluator, remove_timesteps=remove_ts, base_seed=args.seed)
    payload = counterfactual_bundle_to_jsonable(report)
    payload["meta"] = {"cli": "export_counterfactual", "base_seed": args.seed}
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
