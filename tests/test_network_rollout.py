from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.network.contagion_graph import ContagionGraph
from fragility_engine.runner import rollout_stablecoin_network
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights


def test_network_rollout_deterministic():
    n = 16
    adj = ContagionGraph.erdos_renyi(n, p=0.25, seed=11)
    w = default_whale_weights(n)
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=adj,
        node_weights=w,
        max_steps=24,
    )
    rng = np.random.default_rng(0)
    genome = rng.uniform(size=(24, 2))
    a = rollout_stablecoin_network(template, genome, seed=555)
    b = rollout_stablecoin_network(template, genome, seed=555)
    assert a.collapsed == b.collapsed
    assert len(a.trajectory) == len(b.trajectory)
    assert a.simulation_mode == "network"


def test_attack_cost_positive_with_shocks():
    n = 12
    adj = ContagionGraph.erdos_renyi(n, p=0.3, seed=3)
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=adj,
        node_weights=default_whale_weights(n),
        max_steps=16,
    )
    genome = np.array([[0.9, 1.0]] + [[0.0, 0.0]] * 15)  # strong non-none shock at t=0
    r = rollout_stablecoin_network(template, genome, seed=1)
    assert r.attack_cost > 0.0
