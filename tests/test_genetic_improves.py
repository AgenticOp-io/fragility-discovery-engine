from __future__ import annotations

import math

import numpy as np

from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import rollout_stablecoin
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def _eval_factory():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=32)
    horizon = 16

    def evaluator(genome: np.ndarray, seed: int):
        return rollout_stablecoin(template, genome, seed=seed)

    return evaluator, horizon


def test_genetic_search_runs_and_tracks_progress():
    rollout_fn, horizon = _eval_factory()
    ga = genetic_search(
        rollout_fn,
        horizon=horizon,
        generations=8,
        population_size=14,
        seed=202,
    )
    assert ga.best_genome.shape == (horizon, 2)
    assert len(ga.history) == 8
    assert math.isfinite(ga.best_rollout.final_instability)
    assert len(ga.best_rollout.trajectory) >= 1
