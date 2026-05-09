"""Phase C demo: search for collapse under explicit attack-cost penalty (cheap failures)."""

from __future__ import annotations

import json

import numpy as np

from fragility_engine.adversary.fitness import fitness_severity_minus_cost
from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import rollout_stablecoin
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=40)

    def evaluator(genome: np.ndarray, seed: int):
        return rollout_stablecoin(template, genome, seed=seed)

    weight = 0.85
    search = genetic_search(
        evaluator,
        horizon=22,
        generations=14,
        population_size=26,
        seed=808,
        fitness_fn=fitness_severity_minus_cost(attack_cost_weight=weight),
        collect_pareto=True,
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


if __name__ == "__main__":
    main()
