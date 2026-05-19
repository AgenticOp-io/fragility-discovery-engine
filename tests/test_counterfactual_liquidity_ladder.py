from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import (
    counterfactual_liquidity_ladder_delever_rate_shift_with_rollouts,
    counterfactual_liquidity_ladder_initial_margin_shift_with_rollouts,
    counterfactual_remove_steps_with_rollouts,
)
from fragility_engine.explain.merge_attribution import merge_heterogeneous_counterfactuals
from fragility_engine.runner import rollout_liquidity_ladder
from fragility_engine.world.liquidity_ladder import LiquidityLadderWorld


def test_liquidity_ladder_initial_margin_shift_structure():
    template = LiquidityLadderWorld(population=default_stablecoin_population(), max_steps=18)
    genome = np.random.default_rng(901).uniform(size=(9, 2))
    merged, base_rr, var_rr = counterfactual_liquidity_ladder_initial_margin_shift_with_rollouts(
        genome,
        template,
        baseline_initial_margin=0.06,
        variant_initial_margin=0.12,
        rollout_seed=9902,
    )
    assert merged["intervention"] == "liquidity_ladder_initial_margin_shift"
    assert merged["baseline_initial_margin"] == 0.06
    assert merged["variant_initial_margin"] == 0.12
    assert base_rr.simulation_mode == "liquidity_ladder"
    assert var_rr.simulation_mode == "liquidity_ladder"


def test_liquidity_ladder_delever_rate_shift_structure():
    template = LiquidityLadderWorld(population=default_stablecoin_population(), max_steps=18)
    genome = np.random.default_rng(902).uniform(size=(9, 2))
    merged, _, _ = counterfactual_liquidity_ladder_delever_rate_shift_with_rollouts(
        genome,
        template,
        variant_delever_rate=0.5,
        rollout_seed=9903,
        initial_margin=0.07,
    )
    assert merged["intervention"] == "liquidity_ladder_delever_rate_shift"
    assert merged["baseline_delever_rate"] == float(template.delever_rate)
    assert merged["variant_delever_rate"] == 0.5


def test_liquidity_ladder_joint_merge_strict_baseline():
    template = LiquidityLadderWorld(population=default_stablecoin_population(), max_steps=16)
    genome = np.random.default_rng(903).uniform(size=(8, 2))

    def ev(g: np.ndarray, s: int):
        return rollout_liquidity_ladder(template, g, seed=s, initial_margin=0.07)

    b_remove, _, _ = counterfactual_remove_steps_with_rollouts(genome, ev, remove_timesteps=[0], base_seed=9910)
    b_shift, _, _ = counterfactual_liquidity_ladder_initial_margin_shift_with_rollouts(
        genome,
        template,
        baseline_initial_margin=0.07,
        variant_initial_margin=0.02,
        rollout_seed=9910,
    )
    merged = merge_heterogeneous_counterfactuals([b_remove, b_shift], strict_baseline=True)
    assert merged["schema"] == "attribution-merge-v1"
    assert merged["branch_count"] == 2
    assert b_remove["baseline"]["seed"] == b_shift["baseline"]["seed"]
