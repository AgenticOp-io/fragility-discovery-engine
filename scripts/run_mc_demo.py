"""Monte Carlo random shock schedules — fast baseline vs GA (Week 1.5 style)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from fragility_engine.adversary.search import monte_carlo_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution.thread_safe_template import thread_safe_peg_clone
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_stablecoin, rollout_to_replay_dict
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    p = argparse.ArgumentParser(description="Monte Carlo search over random genomes (aggregate world).")
    p.add_argument("--samples", type=int, default=48)
    p.add_argument("--horizon", type=int, default=20)
    p.add_argument("--seed", type=int, default=303)
    p.add_argument("--export-replay", type=Path, default=None, help="Write best-sample rollout JSON.")
    p.add_argument(
        "--continue-after-collapse",
        action="store_true",
        help="Forward past collapse for recovery fields (slower trajectories).",
    )
    p.add_argument(
        "--eval-workers",
        type=int,
        default=1,
        help="Thread pool size for MC rollout evaluation (clone per eval when >1).",
    )
    args = p.parse_args()
    ew = max(1, int(args.eval_workers))

    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=max(args.horizon, 40))

    def evaluator(genome: np.ndarray, seed: int):
        world = thread_safe_peg_clone(template) if ew > 1 else template
        return rollout_stablecoin(
            world,
            genome,
            seed=seed,
            continue_after_collapse=bool(args.continue_after_collapse),
        )

    search = monte_carlo_search(
        evaluator,
        horizon=int(args.horizon),
        samples=int(args.samples),
        seed=int(args.seed),
        eval_workers=ew,
    )

    print(
        json.dumps(
            {
                "best_fitness": search.best_fitness,
                "collapsed": search.best_rollout.collapsed,
                "collapse_timestep": search.best_rollout.collapse_timestep,
                "attack_cost": search.best_rollout.attack_cost,
            },
            indent=2,
        )
    )

    if args.export_replay is not None:
        replay = rollout_to_replay_dict(search.best_rollout)
        replay["meta"] = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "run_mc_demo",
            "samples": int(args.samples),
            "horizon": int(args.horizon),
            "mc_seed": int(args.seed),
            "eval_workers": ew,
        }
        if args.continue_after_collapse:
            replay["meta"]["continue_after_collapse"] = True
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
