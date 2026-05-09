from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.network.contagion_graph import ContagionGraph
from fragility_engine.runner import (
    REPLAY_SCHEMA_VERSION,
    build_events_lane,
    rollout_stablecoin,
    rollout_stablecoin_network,
    rollout_to_replay_dict,
)
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def test_replay_schema_version_and_events_lane():
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=14)
    genome = np.random.default_rng(11).uniform(size=(14, 2))
    r = rollout_stablecoin(template, genome, seed=55)
    d = rollout_to_replay_dict(r)
    assert d["schema_version"] == REPLAY_SCHEMA_VERSION
    assert "events_lane" in d
    assert len(d["events_lane"]) == len(d["trajectory"])
    lane = build_events_lane(r.trajectory)
    assert lane == d["events_lane"]
    assert d["steps_recorded"] == len(d["trajectory"])
    assert "mean_instability" in d and d["mean_instability"] >= 0
    assert d["recovery_latency_steps"] is None


def test_replay_schema_network_state_vector_layout():
    """Network worlds expose mean/max/std panic in ``state_vector`` for replay viewers (indices 3–5)."""
    n = 12
    graph = ContagionGraph.erdos_renyi(n, p=0.2, seed=3)
    weights = default_whale_weights(n, whale_index=0, whale_frac=0.2)
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=weights,
        max_steps=16,
    )
    genome = np.random.default_rng(9).uniform(size=(12, 2))
    r = rollout_stablecoin_network(template, genome, seed=21)
    d = rollout_to_replay_dict(r)
    assert d["simulation_mode"] == "network"
    assert d["trajectory"]
    sv = d["trajectory"][0]["state_vector"]
    assert len(sv) >= 7
