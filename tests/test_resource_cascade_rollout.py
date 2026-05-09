"""Phase J scaffold: resource cascade rollouts."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import rollout_resource_cascade, rollout_to_replay_dict
from fragility_engine.world.resource_cascade import ResourceCascadeWorld


def test_rollout_resource_cascade_deterministic():
    world = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=22)
    genome = np.random.default_rng(501).uniform(size=(10, 2))
    a = rollout_resource_cascade(world, genome, seed=9001, initial_overload=0.06)
    b = rollout_resource_cascade(world, genome, seed=9001, initial_overload=0.06)
    assert a.integral_instability == b.integral_instability
    assert a.collapsed == b.collapsed
    assert a.simulation_mode == "resource_cascade"


def test_rollout_resource_cascade_replay_serializable():
    world = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=14)
    genome = np.random.default_rng(502).uniform(size=(8, 2))
    r = rollout_resource_cascade(world, genome, seed=9102, initial_overload=0.07)
    d = rollout_to_replay_dict(r)
    assert d["simulation_mode"] == "resource_cascade"
    assert len(d["trajectory"]) == len(r.trajectory)
