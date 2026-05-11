"""Replay JSON contract parity for Phase M service_backlog mode."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_service_backlog, rollout_to_replay_dict
from fragility_engine.world.service_backlog import ServiceBacklogWorld

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


def test_service_backlog_replay_matches_aggregate_contract():
    world = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=12)
    genome = np.random.default_rng(78).uniform(size=(8, 2))
    r = rollout_service_backlog(world, genome, seed=4405, initial_backlog=0.08)
    d = rollout_to_replay_dict(r)
    assert d["schema_version"] == REPLAY_SCHEMA_VERSION
    assert d["simulation_mode"] == "service_backlog"
    assert _REPLAY_TOP_KEYS.issubset(d.keys())
    assert len(d["events_lane"]) == len(d["trajectory"])
    step0 = d["trajectory"][0]
    assert set(step0.keys()) >= {"timestep", "state_vector", "events", "agent_actions_summary", "metrics"}
    assert set(step0["metrics"].keys()) >= {"price", "instability", "backing_ratio"}
