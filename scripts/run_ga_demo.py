"""Week 2 — genetic search demo + greedy minimization sketch."""

from __future__ import annotations

import json

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.adversary.search import genetic_search
from fragility_engine.explain.minimal_collapse import minimize_schedule
from fragility_engine.runner import rollout_stablecoin, rollout_to_replay_dict
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
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


if __name__ == "__main__":
    main()
