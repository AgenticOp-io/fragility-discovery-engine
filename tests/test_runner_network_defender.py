"""Defender genome path on network rollouts (Phase G)."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.network.contagion_graph import ContagionGraph
from fragility_engine.runner import rollout_stablecoin_network
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights


def test_rollout_stablecoin_network_defender_changes_metrics():
    graph = ContagionGraph.erdos_renyi(14, p=0.18, seed=77)
    n = graph.n_nodes
    weights = default_whale_weights(n, whale_index=0, whale_frac=0.2)
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=weights,
        contagion_beta=0.34,
        max_steps=22,
    )
    genome = np.random.default_rng(404).random(size=(10, 2))

    base = rollout_stablecoin_network(template, genome, seed=8001, defender_genome=None)
    tuned = rollout_stablecoin_network(
        template,
        genome,
        seed=8001,
        defender_genome=np.array([0.9, 0.9, 0.85, 0.2], dtype=np.float64),
    )
    assert base.simulation_mode == tuned.simulation_mode == "network"
    assert base.attack_cost == tuned.attack_cost
    assert base.integral_instability != tuned.integral_instability
