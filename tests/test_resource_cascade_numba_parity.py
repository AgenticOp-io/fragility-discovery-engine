"""Parity: Numba resource-cascade rollout vs NumPy reference (optional ``numba`` extra)."""

from __future__ import annotations

import numpy as np
import pytest

from fragility_engine.agents.stablecoin_agents import AgentPopulation, RationalArchetype, default_stablecoin_population
from fragility_engine.runner import rollout_resource_cascade
from fragility_engine.world.resource_cascade import ResourceCascadeWorld


def _assert_rollouts_close(a, b) -> None:
    assert a.collapsed == b.collapsed
    assert a.collapse_timestep == b.collapse_timestep
    assert a.simulation_mode == b.simulation_mode
    assert a.seed == b.seed
    assert a.attack_cost == b.attack_cost
    assert np.isclose(a.integral_instability, b.integral_instability, rtol=0.0, atol=1e-12)
    assert np.isclose(a.final_instability, b.final_instability, rtol=0.0, atol=1e-12)
    assert a.recovery_timestep == b.recovery_timestep
    assert len(a.trajectory) == len(b.trajectory)
    for sa, sb in zip(a.trajectory, b.trajectory, strict=True):
        assert sa.timestep == sb.timestep
        np.testing.assert_allclose(sa.state_vector, sb.state_vector, rtol=0.0, atol=1e-14)
        assert sa.events == sb.events
        assert np.isclose(
            sa.agent_actions_summary["aggregate_redeem_fraction"],
            sb.agent_actions_summary["aggregate_redeem_fraction"],
            rtol=0.0,
            atol=1e-14,
        )
        for k in sa.metrics:
            assert np.isclose(float(sa.metrics[k]), float(sb.metrics[k]), rtol=0.0, atol=1e-12), k


def test_rollout_resource_cascade_numba_matches_numpy_default_population(monkeypatch):
    pytest.importorskip("numba")
    monkeypatch.delenv("FRAGILITY_RESOURCE_CASCADE_BACKEND", raising=False)
    world = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=26)
    genome = np.random.default_rng(701).uniform(size=(14, 2))
    ref = rollout_resource_cascade(world, genome, seed=12001, initial_overload=0.055)

    monkeypatch.setenv("FRAGILITY_RESOURCE_CASCADE_BACKEND", "numba")
    fast = rollout_resource_cascade(world, genome, seed=12001, initial_overload=0.055)
    _assert_rollouts_close(ref, fast)


def test_rollout_resource_cascade_numba_matches_numpy_continue_after_collapse(monkeypatch):
    pytest.importorskip("numba")
    monkeypatch.delenv("FRAGILITY_RESOURCE_CASCADE_BACKEND", raising=False)
    world = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=30)
    genome = np.random.default_rng(702).uniform(size=(16, 2))
    ref = rollout_resource_cascade(
        world, genome, seed=12002, initial_overload=0.09, continue_after_collapse=True
    )

    monkeypatch.setenv("FRAGILITY_RESOURCE_CASCADE_BACKEND", "numba")
    fast = rollout_resource_cascade(
        world, genome, seed=12002, initial_overload=0.09, continue_after_collapse=True
    )
    _assert_rollouts_close(ref, fast)


def test_rollout_resource_cascade_numba_matches_numpy_defender_genome(monkeypatch):
    pytest.importorskip("numba")
    monkeypatch.delenv("FRAGILITY_RESOURCE_CASCADE_BACKEND", raising=False)
    world = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=22)
    genome = np.random.default_rng(703).uniform(size=(12, 2))
    defender = np.array([0.2, 0.85, 0.15, 0.9], dtype=np.float64)
    ref = rollout_resource_cascade(
        world, genome, seed=12003, initial_overload=0.07, defender_genome=defender
    )

    monkeypatch.setenv("FRAGILITY_RESOURCE_CASCADE_BACKEND", "numba")
    fast = rollout_resource_cascade(
        world, genome, seed=12003, initial_overload=0.07, defender_genome=defender
    )
    _assert_rollouts_close(ref, fast)


def test_rollout_resource_cascade_custom_population_falls_back_to_numpy(monkeypatch):
    monkeypatch.setenv("FRAGILITY_RESOURCE_CASCADE_BACKEND", "auto")
    pop = AgentPopulation(archetypes=[(1.0, RationalArchetype(backing_trigger=0.95))])
    world = ResourceCascadeWorld(population=pop, max_steps=18)
    genome = np.random.default_rng(704).uniform(size=(10, 2))
    r = rollout_resource_cascade(world, genome, seed=12004, initial_overload=0.06)
    assert r.simulation_mode == "resource_cascade"
    assert len(r.trajectory) >= 1
