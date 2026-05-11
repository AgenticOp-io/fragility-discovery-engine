"""Phase M — service backlog rollouts."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import rollout_service_backlog, rollout_to_replay_dict
from fragility_engine.world.service_backlog import ServiceBacklogWorld


def test_rollout_service_backlog_deterministic():
    world = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=22)
    genome = np.random.default_rng(601).uniform(size=(10, 2))
    a = rollout_service_backlog(world, genome, seed=9001, initial_backlog=0.06)
    b = rollout_service_backlog(world, genome, seed=9001, initial_backlog=0.06)
    assert a.integral_instability == b.integral_instability
    assert a.collapsed == b.collapsed
    assert a.simulation_mode == "service_backlog"


def test_rollout_service_backlog_replay_serializable():
    world = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=14)
    genome = np.random.default_rng(602).uniform(size=(8, 2))
    r = rollout_service_backlog(world, genome, seed=9102, initial_backlog=0.07)
    d = rollout_to_replay_dict(r)
    assert d["simulation_mode"] == "service_backlog"
    assert len(d["trajectory"]) == len(r.trajectory)


def test_rollout_service_backlog_identity_defender_matches_none():
    world = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=20)
    genome = np.random.default_rng(603).uniform(size=(10, 2))
    identity = np.array([0.5, 0.5, 0.0, 0.0], dtype=np.float64)
    a = rollout_service_backlog(world, genome, seed=9201, initial_backlog=0.06)
    b = rollout_service_backlog(world, genome, seed=9201, initial_backlog=0.06, defender_genome=identity)
    assert a.integral_instability == b.integral_instability
    assert a.attack_cost == b.attack_cost
    assert a.collapsed == b.collapsed


def test_rollout_service_backlog_defender_changes_metrics():
    world = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=20)
    genome = np.random.default_rng(604).uniform(size=(10, 2))
    strong = np.ones(4, dtype=np.float64)
    base = rollout_service_backlog(world, genome, seed=9301, initial_backlog=0.08, defender_genome=None)
    defended = rollout_service_backlog(world, genome, seed=9301, initial_backlog=0.08, defender_genome=strong)
    assert (
        defended.integral_instability != base.integral_instability
        or defended.collapsed != base.collapsed
        or defended.collapse_timestep != base.collapse_timestep
    )
