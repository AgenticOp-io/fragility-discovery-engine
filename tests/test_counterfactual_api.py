from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import counterfactual_remove_steps
from fragility_engine.runner import rollout_stablecoin
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def test_counterfactual_structured_output():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=32)
    rng = np.random.default_rng(1)
    genome = rng.uniform(size=(32, 2))

    def evaluator(g: np.ndarray, seed: int):
        return rollout_stablecoin(template, g, seed=seed)

    report = counterfactual_remove_steps(genome, evaluator, remove_timesteps=[0, 1], base_seed=9090)
    assert "baseline" in report and "counterfactual" in report
    assert "interpretation_hint" in report
