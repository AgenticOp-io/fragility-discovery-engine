from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import (
    counterfactual_remove_steps_with_rollouts,
    counterfactual_service_backlog_initial_backlog_shift_with_rollouts,
    counterfactual_service_backlog_process_rate_shift_with_rollouts,
)
from fragility_engine.runner import rollout_service_backlog
from fragility_engine.world.service_backlog import ServiceBacklogWorld


def test_service_backlog_initial_backlog_shift_structure():
    template = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=18)
    genome = np.random.default_rng(801).uniform(size=(9, 2))
    merged, base_rr, var_rr = counterfactual_service_backlog_initial_backlog_shift_with_rollouts(
        genome,
        template,
        baseline_initial_backlog=0.05,
        variant_initial_backlog=0.12,
        rollout_seed=8802,
    )
    assert merged["intervention"] == "service_backlog_initial_backlog_shift"
    assert merged["baseline_initial_backlog"] == 0.05
    assert merged["variant_initial_backlog"] == 0.12
    assert base_rr.simulation_mode == "service_backlog"
    assert var_rr.simulation_mode == "service_backlog"


def test_service_backlog_process_rate_shift_structure():
    template = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=18)
    genome = np.random.default_rng(802).uniform(size=(9, 2))
    merged, _, _ = counterfactual_service_backlog_process_rate_shift_with_rollouts(
        genome,
        template,
        variant_process_rate=0.5,
        rollout_seed=8803,
        initial_backlog=0.06,
    )
    assert merged["intervention"] == "service_backlog_process_rate_shift"
    assert merged["baseline_process_rate"] == float(template.process_rate)
    assert merged["variant_process_rate"] == 0.5


def test_service_backlog_joint_merge_strict_baseline():
    """remove_steps + backlog shift share pinned genome/seed (smoke for merge helper consumers)."""

    template = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=16)
    genome = np.random.default_rng(803).uniform(size=(8, 2))

    def ev(g: np.ndarray, s: int):
        return rollout_service_backlog(template, g, seed=s, initial_backlog=0.07)

    b_remove, _, _ = counterfactual_remove_steps_with_rollouts(genome, ev, remove_timesteps=[0, 1], base_seed=9900)
    b_shift, _, _ = counterfactual_service_backlog_initial_backlog_shift_with_rollouts(
        genome,
        template,
        baseline_initial_backlog=0.07,
        variant_initial_backlog=0.02,
        rollout_seed=9900,
    )
    assert b_remove["baseline"]["seed"] == b_shift["baseline"]["seed"]
