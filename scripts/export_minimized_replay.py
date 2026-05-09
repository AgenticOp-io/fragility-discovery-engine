"""Export greedy-minimized collapse replay (aggregate world) for the static viewer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.minimal_collapse import minimize_schedule_with_rollout
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_stablecoin, rollout_to_replay_dict
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    p = argparse.ArgumentParser(
        description="Find a collapsing schedule (random search), greedy-minimize shocks, write replay JSON.",
    )
    p.add_argument("--out", type=Path, default=Path("minimized_replay.json"))
    p.add_argument("--horizon", type=int, default=28)
    p.add_argument("--max-tries", type=int, default=256, help="Random genomes to try before giving up.")
    p.add_argument("--base-seed", type=int, default=424242, help="Pinned rollout seed for minimization.")
    p.add_argument("--genome-search-seed", type=int, default=7, help="RNG seed for sampling genomes.")
    args = p.parse_args()

    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=max(args.horizon, 40))

    def evaluator(genome: np.ndarray, seed: int):
        return rollout_stablecoin(template, genome, seed=seed)

    rng = np.random.default_rng(int(args.genome_search_seed))
    chosen = None
    chosen_rr = None
    for _ in range(int(args.max_tries)):
        genome = rng.uniform(size=(int(args.horizon), 2))
        base = evaluator(genome, int(args.base_seed))
        if base.collapsed:
            report, rr = minimize_schedule_with_rollout(genome, evaluator, base_seed=int(args.base_seed))
            if rr is not None:
                chosen = report
                chosen_rr = rr
                break

    if chosen_rr is None:
        print(
            f"No collapsing schedule found in {args.max_tries} tries (raise horizon or max-tries).",
            file=sys.stderr,
        )
        raise SystemExit(2)

    replay = rollout_to_replay_dict(chosen_rr)
    kept = chosen.get("minimal_events_by_timestep") or {}
    replay["meta"] = {
        "replay_schema": REPLAY_SCHEMA_VERSION,
        "cli": "export_minimized_replay",
        "minimize_base_seed": int(args.base_seed),
        "minimal_timesteps_remaining": len(kept),
        "minimized_collapsed": bool(chosen.get("collapsed")),
        "minimized_collapse_timestep": chosen.get("collapse_timestep"),
    }
    args.out.write_text(json.dumps(replay, indent=2), encoding="utf-8")
    print(json.dumps({"wrote": str(args.out), "collapse_timestep": chosen_rr.collapse_timestep}, indent=2))


if __name__ == "__main__":
    main()
