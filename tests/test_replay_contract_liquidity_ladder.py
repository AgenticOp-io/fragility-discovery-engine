"""Replay JSON contract parity for Phase N liquidity_ladder mode."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_liquidity_ladder, rollout_to_replay_dict
from fragility_engine.world.liquidity_ladder import LiquidityLadderWorld

_REPLAY_TOP_KEYS = frozenset(
    {
        "schema_version",
        "simulation_mode",
        "attack_cost",
        "integral_instability",
        "recovery_timestep",
        "collapsed",
        "collapse_timestep",
        "final_instability",
        "seed",
        "events_lane",
        "trajectory",
        "steps_recorded",
        "mean_instability",
        "recovery_latency_steps",
    }
)


def test_liquidity_ladder_replay_matches_aggregate_contract():
    world = LiquidityLadderWorld(population=default_stablecoin_population(), max_steps=12)
    genome = np.random.default_rng(79).uniform(size=(8, 2))
    r = rollout_liquidity_ladder(world, genome, seed=4406, initial_margin=0.08)
    d = rollout_to_replay_dict(r)
    assert d["schema_version"] == REPLAY_SCHEMA_VERSION
    assert d["simulation_mode"] == "liquidity_ladder"
    assert _REPLAY_TOP_KEYS.issubset(d.keys())
    assert len(d["events_lane"]) == len(d["trajectory"])
