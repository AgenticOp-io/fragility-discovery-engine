"""Phase C demo: search for collapse under explicit attack-cost penalty (cheap failures)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from fragility_engine.adversary.fitness import fitness_severity_minus_cost
from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution.thread_safe_template import thread_safe_peg_clone
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_stablecoin, rollout_to_replay_dict
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    p = argparse.ArgumentParser(description="GA with severity − λ·cost fitness + optional replay export.")
    p.add_argument("--export-replay", type=Path, default=None, help="Write best-rollout replay JSON.")
    p.add_argument(
        "--eval-workers",
        type=int,
        default=1,
        help="Thread pool size for GA fitness evaluation (clone per eval when >1).",
    )
    args = p.parse_args()

    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=40)
    ew = max(1, int(args.eval_workers))

    def evaluator(genome: np.ndarray, seed: int):
        world = thread_safe_peg_clone(template) if ew > 1 else template
        return rollout_stablecoin(world, genome, seed=seed)

    weight = 0.85
    search = genetic_search(
        evaluator,
        horizon=22,
        generations=14,
        population_size=26,
        seed=808,
        fitness_fn=fitness_severity_minus_cost(attack_cost_weight=weight),
        collect_pareto=True,
        eval_workers=ew,
    )

    payload = {
        "attack_cost_weight": weight,
        "best_fitness": search.best_fitness,
        "collapsed": search.best_rollout.collapsed,
        "attack_cost": search.best_rollout.attack_cost,
        "severity_proxy": search.best_rollout.final_instability,
        "pareto_archive_size": len(search.pareto_archive),
    }
    print(json.dumps(payload, indent=2))

    if args.export_replay is not None:
        replay = rollout_to_replay_dict(search.best_rollout)
        replay["meta"] = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "find_cheap_collapse",
            "attack_cost_weight": weight,
            "pareto_archive_size": len(search.pareto_archive),
            "eval_workers": ew,
        }
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
