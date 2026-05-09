"""Counterfactual helpers for Phase J resource cascade."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import (
    counterfactual_remove_steps_with_rollouts,
    counterfactual_resource_cascade_cascade_coupling_shift_with_rollouts,
    counterfactual_resource_cascade_initial_overload_shift_with_rollouts,
)
from fragility_engine.explain.merge_attribution import merge_heterogeneous_counterfactuals
from fragility_engine.runner import rollout_resource_cascade
from fragility_engine.world.resource_cascade import ResourceCascadeWorld


def test_resource_cascade_initial_overload_shift_structure():
    template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=24)
    genome = np.random.default_rng(601).uniform(size=(14, 2))
    merged, base_rr, var_rr = counterfactual_resource_cascade_initial_overload_shift_with_rollouts(
        genome,
        template,
        baseline_initial_overload=0.06,
        variant_initial_overload=0.14,
        rollout_seed=90999,
    )
    assert merged["intervention"] == "resource_cascade_initial_overload_shift"
    assert merged["baseline_initial_overload"] == 0.06
    assert merged["variant_initial_overload"] == 0.14
    assert "delta_integral_instability" in merged
    assert base_rr.simulation_mode == "resource_cascade"
    assert var_rr.simulation_mode == "resource_cascade"


def test_resource_cascade_cascade_coupling_shift_structure():
    template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=20)
    genome = np.random.default_rng(603).uniform(size=(11, 2))
    merged, _, _ = counterfactual_resource_cascade_cascade_coupling_shift_with_rollouts(
        genome,
        template,
        variant_cascade_coupling=0.35,
        rollout_seed=771077,
        initial_overload=0.06,
    )
    assert merged["intervention"] == "resource_cascade_cascade_coupling_shift"
    assert merged["baseline_cascade_coupling"] == float(template.cascade_coupling)
    assert merged["variant_cascade_coupling"] == 0.35


def test_resource_cascade_joint_merge_strict_baseline():
    template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=22)
    genome = np.random.default_rng(602).uniform(size=(12, 2))
    io = 0.065

    def evaluator(g: np.ndarray, s: int):
        return rollout_resource_cascade(template, g, seed=s, initial_overload=io)

    b_remove, _, _ = counterfactual_remove_steps_with_rollouts(
        genome, evaluator, remove_timesteps=[0], base_seed=770077
    )
    b_shift, _, _ = counterfactual_resource_cascade_initial_overload_shift_with_rollouts(
        genome,
        template,
        baseline_initial_overload=io,
        variant_initial_overload=0.11,
        rollout_seed=770077,
    )
    merged = merge_heterogeneous_counterfactuals([b_remove, b_shift], strict_baseline=True)
    assert merged["schema"] == "attribution-merge-v1"
    assert merged["branch_count"] == 2
