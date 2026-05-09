from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.minimal_collapse import minimize_schedule, minimize_schedule_with_rollout
from fragility_engine.runner import rollout_stablecoin
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def test_minimize_schedule_matches_with_rollout_branch():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=36)

    def evaluator(g: np.ndarray, seed: int):
        return rollout_stablecoin(template, g, seed=seed)

    collapsed_seen = False
    for trial in range(80):
        rng = np.random.default_rng(trial)
        genome = rng.uniform(size=(22, 2))
        base_seed = 3000 + trial
        plain = minimize_schedule(genome, evaluator, base_seed=base_seed)
        rich, rr = minimize_schedule_with_rollout(genome, evaluator, base_seed=base_seed)
        assert plain == rich
        if plain["baseline_collapsed"]:
            assert rr is not None
            assert rr.collapsed
            assert isinstance(plain["minimal_genome"], list)
            collapsed_seen = True
        else:
            assert rr is None
    assert collapsed_seen
