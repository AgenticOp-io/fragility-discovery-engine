"""GA eval_workers determinism when rollout uses isolated worlds."""

from __future__ import annotations

import numpy as np

from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution.thread_safe_template import thread_safe_peg_clone
from fragility_engine.runner import rollout_stablecoin
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def test_genetic_search_eval_workers_matches_sequential():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=24)

    def evaluator(genome: np.ndarray, seed: int):
        world = thread_safe_peg_clone(template)
        return rollout_stablecoin(world, genome, seed=seed)

    kwargs = dict(
        horizon=10,
        generations=3,
        population_size=8,
        seed=14141,
    )
    s1 = genetic_search(evaluator, eval_workers=1, **kwargs)
    s4 = genetic_search(evaluator, eval_workers=4, **kwargs)
    assert np.allclose(s1.best_genome, s4.best_genome)
    assert s1.best_fitness == s4.best_fitness
    assert s1.best_rollout.collapsed == s4.best_rollout.collapsed
    assert len(s1.history) == len(s4.history)
    for h1, h4 in zip(s1.history, s4.history, strict=True):
        assert h1["generation"] == h4["generation"]
        assert abs(float(h1["mean_fitness"]) - float(h4["mean_fitness"])) < 1e-9
        assert abs(float(h1["max_fitness"]) - float(h4["max_fitness"])) < 1e-9
