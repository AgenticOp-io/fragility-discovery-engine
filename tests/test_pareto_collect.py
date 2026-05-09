from __future__ import annotations

import numpy as np

from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import rollout_stablecoin
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def test_genetic_search_collect_pareto_populates_archive():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=24)

    def evaluator(genome: np.ndarray, seed: int):
        return rollout_stablecoin(template, genome, seed=seed)

    search = genetic_search(
        evaluator,
        horizon=12,
        generations=3,
        population_size=10,
        seed=321,
        collect_pareto=True,
    )
    assert len(search.pareto_archive) >= 1
