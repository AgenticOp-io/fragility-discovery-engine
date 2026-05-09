from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import (
    counterfactual_remove_steps,
    counterfactual_remove_steps_with_rollouts,
)
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
    assert "removed_timesteps" in report and "delta_attack_cost" in report
    assert "integral_instability" in report["baseline"]


def test_counterfactual_with_rollouts_matches_remove_steps():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=32)
    rng = np.random.default_rng(2)
    genome = rng.uniform(size=(32, 2))

    def evaluator(g: np.ndarray, seed: int):
        return rollout_stablecoin(template, g, seed=seed)

    plain = counterfactual_remove_steps(genome, evaluator, remove_timesteps=[0, 3], base_seed=707)
    merged, baseline_rr, variant_rr = counterfactual_remove_steps_with_rollouts(
        genome, evaluator, remove_timesteps=[0, 3], base_seed=707
    )
    assert plain == merged
    assert len(baseline_rr.trajectory) >= 1 and len(variant_rr.trajectory) >= 1
