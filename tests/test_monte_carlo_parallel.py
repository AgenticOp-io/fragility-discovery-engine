"""Monte Carlo eval_workers determinism with isolated worlds."""

from __future__ import annotations

import numpy as np

from fragility_engine.adversary.search import monte_carlo_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution.thread_safe_template import thread_safe_peg_clone
from fragility_engine.runner import rollout_stablecoin
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def test_monte_carlo_eval_workers_matches_sequential():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=28)

    def evaluator(genome: np.ndarray, seed: int):
        world = thread_safe_peg_clone(template)
        return rollout_stablecoin(world, genome, seed=seed)

    kwargs = dict(horizon=10, samples=24, seed=424242)
    s1 = monte_carlo_search(evaluator, eval_workers=1, **kwargs)
    s4 = monte_carlo_search(evaluator, eval_workers=4, **kwargs)
    assert np.allclose(s1.best_genome, s4.best_genome)
    assert s1.best_fitness == s4.best_fitness
    assert s1.best_rollout.collapsed == s4.best_rollout.collapsed
    assert len(s1.history) == len(s4.history)
    for h1, h4 in zip(s1.history, s4.history, strict=True):
        assert h1 == h4


def test_monte_carlo_zero_samples_still_runs_baseline():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=20)

    def evaluator(genome: np.ndarray, seed: int):
        return rollout_stablecoin(template, genome, seed=seed)

    r = monte_carlo_search(evaluator, horizon=6, samples=0, seed=1, eval_workers=2)
    assert r.history == []
    assert r.best_rollout.seed == 2  # seed + 1
