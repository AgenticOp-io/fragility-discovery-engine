"""Phase O — GA adversary on InventoryBufferWorld (sixth reference domain)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution.thread_safe_template import thread_safe_inventory_buffer_clone
from fragility_engine.explain.minimal_collapse import minimize_schedule_with_rollout
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_inventory_buffer, rollout_to_replay_dict
from fragility_engine.world.inventory_buffer import InventoryBufferWorld


def main() -> None:
    p = argparse.ArgumentParser(description="GA adversary on InventoryBufferWorld (Phase O).")
    p.add_argument("--export-replay", type=Path, default=None)
    p.add_argument("--export-minimized-replay", type=Path, default=None)
    p.add_argument("--generations", type=int, default=10)
    p.add_argument("--population-size", type=int, default=20)
    p.add_argument("--seed", type=int, default=909)
    p.add_argument("--initial-stock", type=float, default=0.88)
    p.add_argument("--eval-workers", type=int, default=1)
    args = p.parse_args()

    template = InventoryBufferWorld(population=default_stablecoin_population(), max_steps=36)
    horizon = 18
    ew = max(1, int(args.eval_workers))

    def ga_evaluator(genome, seed: int):
        world = thread_safe_inventory_buffer_clone(template) if ew > 1 else template
        return rollout_inventory_buffer(
            world, genome, seed=seed, initial_stock=float(args.initial_stock)
        )

    def minimize_evaluator(genome, seed: int):
        return rollout_inventory_buffer(
            template, genome, seed=seed, initial_stock=float(args.initial_stock)
        )

    search = genetic_search(
        ga_evaluator,
        horizon=horizon,
        generations=int(args.generations),
        population_size=int(args.population_size),
        seed=int(args.seed),
        eval_workers=ew,
    )
    best = search.best_rollout
    print(
        json.dumps(
            {
                "simulation_mode": "inventory_buffer",
                "best_fitness": float(search.best_fitness),
                "integral_instability": float(best.integral_instability),
                "collapsed": bool(best.collapsed),
                "attack_cost": float(best.attack_cost),
            }
        )
    )

    if args.export_replay:
        payload = rollout_to_replay_dict(best)
        payload["schema_version"] = REPLAY_SCHEMA_VERSION
        args.export_replay.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.export_minimized_replay and best.collapsed:
        min_genome, min_result = minimize_schedule_with_rollout(
            search.best_genome,
            minimize_evaluator,
            seed=int(args.seed) + 1,
            horizon=horizon,
        )
        payload = rollout_to_replay_dict(min_result)
        payload["schema_version"] = REPLAY_SCHEMA_VERSION
        payload["meta"] = {"minimized_from_genome_shape": list(search.best_genome.shape)}
        args.export_minimized_replay.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if best.collapsed and not args.export_replay and not args.export_minimized_replay:
        sys.exit(0)
    if not best.collapsed:
        sys.exit(0)


if __name__ == "__main__":
    main()
