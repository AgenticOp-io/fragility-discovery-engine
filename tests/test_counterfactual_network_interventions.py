"""Phase I: network counterfactuals beyond timestep removal."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import (
    counterfactual_network_base_panic_with_rollouts,
    counterfactual_network_contagion_beta_with_rollouts,
)
from fragility_engine.network.contagion_graph import ContagionGraph
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights


def test_counterfactual_base_panic_shift_smoke():
    graph = ContagionGraph.erdos_renyi(16, p=0.15, seed=404)
    n = graph.n_nodes
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=default_whale_weights(n, whale_index=0, whale_frac=0.2),
        contagion_beta=0.34,
        max_steps=22,
    )
    genome = np.random.default_rng(21).uniform(size=(10, 2))
    report, base, var = counterfactual_network_base_panic_with_rollouts(
        genome,
        template,
        baseline_base_panic=0.05,
        variant_base_panic=0.14,
        rollout_seed=909,
    )
    assert report["intervention"] == "network_base_panic_shift"
    assert report["baseline_base_panic"] == 0.05
    assert report["variant_base_panic"] == 0.14
    assert base.simulation_mode == var.simulation_mode == "network"


def test_counterfactual_contagion_beta_shift_smoke():
    nl = [[1], [0]]
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        neighbor_lists=nl,
        node_weights=default_whale_weights(2, whale_index=0, whale_frac=0.3),
        contagion_beta=0.4,
        max_steps=18,
    )
    genome = np.random.default_rng(33).uniform(size=(8, 2))
    report, base, var = counterfactual_network_contagion_beta_with_rollouts(
        genome,
        template,
        baseline_beta=0.4,
        variant_beta=0.08,
        rollout_seed=707,
        base_panic=0.06,
    )
    assert report["intervention"] == "network_contagion_beta_shift"
    assert report["baseline_beta"] == 0.4
    assert report["variant_beta"] == 0.08
