"""Counterfactual API on network rollouts (pinned seeds)."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import counterfactual_remove_steps
from fragility_engine.network.contagion_graph import ContagionGraph
from fragility_engine.runner import rollout_stablecoin_network
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights


def test_counterfactual_remove_steps_network_smoke():
    graph = ContagionGraph.erdos_renyi(18, p=0.14, seed=44)
    n = graph.n_nodes
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=default_whale_weights(n, whale_index=0, whale_frac=0.2),
        contagion_beta=0.33,
        max_steps=28,
    )
    rng = np.random.default_rng(9)
    genome = rng.uniform(size=(14, 2))

    def evaluator(g: np.ndarray, seed: int):
        return rollout_stablecoin_network(template, g, seed=seed, base_panic=0.05)

    report = counterfactual_remove_steps(genome, evaluator, remove_timesteps=[0, 2], base_seed=50505)
    assert report["baseline"]["mode"] == "network"
    assert report["counterfactual"]["mode"] == "network"
    assert set(report["removed_timesteps"]) == {0, 2}


def test_counterfactual_neighbor_list_topology_smoke():
    nl = [[1], [0]]
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        neighbor_lists=nl,
        node_weights=default_whale_weights(2, whale_index=0, whale_frac=0.35),
        max_steps=20,
    )
    genome = np.random.default_rng(3).uniform(size=(10, 2))

    def evaluator(g: np.ndarray, seed: int):
        return rollout_stablecoin_network(template, g, seed=seed)

    report = counterfactual_remove_steps(genome, evaluator, remove_timesteps=[1], base_seed=707)
    assert report["baseline"]["mode"] == report["counterfactual"]["mode"] == "network"
