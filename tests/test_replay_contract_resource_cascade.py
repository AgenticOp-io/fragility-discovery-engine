"""Replay JSON contract parity for Phase J resource_cascade mode."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_resource_cascade, rollout_to_replay_dict
from fragility_engine.world.resource_cascade import ResourceCascadeWorld

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


def test_resource_cascade_replay_matches_aggregate_contract():
    world = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=12)
    genome = np.random.default_rng(77).uniform(size=(8, 2))
    r = rollout_resource_cascade(world, genome, seed=4404, initial_overload=0.08)
    d = rollout_to_replay_dict(r)
    assert d["schema_version"] == REPLAY_SCHEMA_VERSION
    assert d["simulation_mode"] == "resource_cascade"
    assert _REPLAY_TOP_KEYS.issubset(d.keys())
    assert len(d["events_lane"]) == len(d["trajectory"])
    step0 = d["trajectory"][0]
    assert set(step0.keys()) >= {"timestep", "state_vector", "events", "agent_actions_summary", "metrics"}
    assert set(step0["metrics"].keys()) >= {"price", "instability", "backing_ratio"}
