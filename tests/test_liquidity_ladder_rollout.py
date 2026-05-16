"""LiquidityLadderWorld rollout determinism (Phase N)."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import rollout_liquidity_ladder, rollout_to_replay_dict
from fragility_engine.world.liquidity_ladder import LiquidityLadderWorld


def test_liquidity_ladder_rollout_deterministic():
    world = LiquidityLadderWorld(population=default_stablecoin_population(), max_steps=14)
    genome = np.random.default_rng(91).uniform(size=(8, 2))
    a = rollout_liquidity_ladder(world, genome, seed=7001, initial_margin=0.07)
    b = rollout_liquidity_ladder(world, genome, seed=7001, initial_margin=0.07)
    assert a.integral_instability == b.integral_instability
    assert a.collapsed == b.collapsed
    assert len(a.trajectory) == len(b.trajectory)


def test_liquidity_ladder_replay_serializable():
    world = LiquidityLadderWorld(population=default_stablecoin_population(), max_steps=10)
    genome = np.random.default_rng(92).uniform(size=(6, 2))
    r = rollout_liquidity_ladder(world, genome, seed=7002)
    d = rollout_to_replay_dict(r)
    assert d["simulation_mode"] == "liquidity_ladder"
    assert d["trajectory"]
