"""InventoryBufferWorld rollout determinism (Phase O)."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import rollout_inventory_buffer, rollout_to_replay_dict
from fragility_engine.world.inventory_buffer import InventoryBufferWorld


def test_inventory_buffer_rollout_deterministic():
    world = InventoryBufferWorld(population=default_stablecoin_population(), max_steps=14)
    genome = np.random.default_rng(91).uniform(size=(8, 2))
    a = rollout_inventory_buffer(world, genome, seed=7101, initial_stock=0.85)
    b = rollout_inventory_buffer(world, genome, seed=7101, initial_stock=0.85)
    assert a.integral_instability == b.integral_instability
    assert a.collapsed == b.collapsed


def test_inventory_buffer_replay_serializable():
    world = InventoryBufferWorld(population=default_stablecoin_population(), max_steps=10)
    genome = np.random.default_rng(92).uniform(size=(6, 2))
    r = rollout_inventory_buffer(world, genome, seed=7102)
    d = rollout_to_replay_dict(r)
    assert d["simulation_mode"] == "inventory_buffer"
    assert d["trajectory"]
