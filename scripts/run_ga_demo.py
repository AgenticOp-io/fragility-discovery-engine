"""Week 2 — genetic search demo + greedy minimization sketch."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.minimal_collapse import minimize_schedule_with_rollout
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_stablecoin, rollout_to_replay_dict
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    p = argparse.ArgumentParser(description="GA adversary demo + optional replay export.")
    p.add_argument(
        "--export-replay",
        type=Path,
        default=None,
        help="Write best-rollout replay JSON for the static viewer.",
    )
    p.add_argument(
        "--export-minimized-replay",
        type=Path,
        default=None,
        help="Write greedy-minimized schedule replay (only if GA best baseline collapses).",
    )
    p.add_argument("--generations", type=int, default=12)
    p.add_argument("--population-size", type=int, default=24)
    p.add_argument("--seed", type=int, default=999)
    args = p.parse_args()

    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=48)
    horizon = 24

    def evaluator(genome, seed: int):
        return rollout_stablecoin(template, genome, seed=seed)

    search = genetic_search(
        evaluator,
        horizon=horizon,
        generations=int(args.generations),
        population_size=int(args.population_size),
        seed=int(args.seed),
    )

    print("best_fitness=", round(search.best_fitness, 5))
    print("attack_cost=", round(search.best_rollout.attack_cost, 5))
    print("collapsed=", search.best_rollout.collapsed, "at", search.best_rollout.collapse_timestep)

    min_seed = 424242
    minimized, min_rollout = minimize_schedule_with_rollout(search.best_genome, evaluator, base_seed=min_seed)
    print("minimization=", json.dumps(minimized, indent=2)[:1200])

    replay = rollout_to_replay_dict(search.best_rollout)
    print("replay_steps=", len(replay["trajectory"]))

    common_meta = {
        "replay_schema": REPLAY_SCHEMA_VERSION,
        "cli": "run_ga_demo",
        "generations": int(args.generations),
        "population_size": int(args.population_size),
        "horizon": horizon,
        "ga_seed": int(args.seed),
    }

    if args.export_replay is not None:
        replay["meta"] = {**common_meta, "variant": "best_ga"}
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")

    if args.export_minimized_replay is not None:
        if min_rollout is None:
            print(
                "Skipping --export-minimized-replay: baseline did not collapse.",
                file=sys.stderr,
            )
        else:
            mr = rollout_to_replay_dict(min_rollout)
            mr["meta"] = {
                **common_meta,
                "variant": "greedy_minimized_schedule",
                "minimize_base_seed": min_seed,
            }
            args.export_minimized_replay.write_text(json.dumps(mr, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
