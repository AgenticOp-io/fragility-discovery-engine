"""Replay contract for inventory_buffer mode."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import rollout_inventory_buffer, rollout_to_replay_dict
from fragility_engine.world.inventory_buffer import InventoryBufferWorld


def test_inventory_buffer_replay_has_events_lane():
    world = InventoryBufferWorld(population=default_stablecoin_population(), max_steps=8)
    genome = np.random.default_rng(3).uniform(size=(6, 2))
    r = rollout_inventory_buffer(world, genome, seed=99)
    d = rollout_to_replay_dict(r)
    assert "events_lane" in d
    assert d["simulation_mode"] == "inventory_buffer"
