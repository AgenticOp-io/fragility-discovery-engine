"""Week 2 — genetic search demo + greedy minimization sketch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.minimal_collapse import minimize_schedule
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
    args = p.parse_args()

    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=48)
    horizon = 24

    def evaluator(genome, seed: int):
        return rollout_stablecoin(template, genome, seed=seed)

    search = genetic_search(
        evaluator,
        horizon=horizon,
        generations=12,
        population_size=24,
        seed=999,
    )

    print("best_fitness=", round(search.best_fitness, 5))
    print("attack_cost=", round(search.best_rollout.attack_cost, 5))
    print("collapsed=", search.best_rollout.collapsed, "at", search.best_rollout.collapse_timestep)

    minimized = minimize_schedule(search.best_genome, evaluator, base_seed=424242)
    print("minimization=", json.dumps(minimized, indent=2)[:1200])

    replay = rollout_to_replay_dict(search.best_rollout)
    print("replay_steps=", len(replay["trajectory"]))

    if args.export_replay is not None:
        replay["meta"] = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "run_ga_demo",
            "generations": 12,
            "population_size": 24,
            "horizon": horizon,
        }
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
