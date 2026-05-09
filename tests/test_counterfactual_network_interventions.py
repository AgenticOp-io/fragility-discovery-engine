"""Phase I: network counterfactuals beyond timestep removal."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import (
    counterfactual_network_base_panic_with_rollouts,
    counterfactual_network_contagion_beta_with_rollouts,
    counterfactual_network_edge_weight_with_rollouts,
    counterfactual_network_neighbor_edges_weight_patch_with_rollouts,
    neighbor_lists_explicit_weights,
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


def test_counterfactual_edge_weight_shift_smoke():
    nl = [[1, 2], [0], [0]]
    nw = [[1.0, 2.0], [1.0], [1.0]]
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        neighbor_lists=nl,
        neighbor_weights=nw,
        node_weights=default_whale_weights(3, whale_index=0, whale_frac=0.25),
        contagion_beta=0.38,
        max_steps=16,
    )
    genome = np.random.default_rng(44).uniform(size=(7, 2))
    report, base, var = counterfactual_network_edge_weight_with_rollouts(
        genome,
        template,
        edge_from=0,
        edge_to=1,
        variant_edge_weight=5.0,
        rollout_seed=6161,
        base_panic=0.07,
    )
    assert report["intervention"] == "network_neighbor_edge_weight_shift"
    assert report["baseline_edge_weight"] == 1.0
    assert report["variant_edge_weight"] == 5.0
    assert base.simulation_mode == var.simulation_mode == "network"


def test_neighbor_lists_explicit_weights_uniform_when_missing():
    nl = [[1], [0]]
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        neighbor_lists=nl,
        node_weights=default_whale_weights(2, whale_index=0, whale_frac=0.3),
        contagion_beta=0.35,
        max_steps=12,
    )
    assert neighbor_lists_explicit_weights(template) == [[1.0], [1.0]]


def test_neighbor_edges_weight_patch_smoke():
    nl = [[1, 2], [0], [0]]
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        neighbor_lists=nl,
        node_weights=default_whale_weights(3, whale_index=0, whale_frac=0.25),
        contagion_beta=0.37,
        max_steps=15,
    )
    genome = np.random.default_rng(55).uniform(size=(7, 2))
    patch = [{"from": 0, "to": 1, "weight": 5.0}, {"from": 0, "to": 2, "weight": 0.5}]
    report, _, _ = counterfactual_network_neighbor_edges_weight_patch_with_rollouts(
        genome,
        template,
        edges_patch=patch,
        rollout_seed=2323,
        base_panic=0.07,
    )
    assert report["intervention"] == "network_neighbor_edges_weight_patch"
    assert len(report["edges_patch"]) == 2


def test_edge_weight_requires_neighbor_lists_not_adjacency():
    graph = ContagionGraph.erdos_renyi(8, p=0.2, seed=1)
    n = graph.n_nodes
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=default_whale_weights(n, whale_index=0, whale_frac=0.2),
        contagion_beta=0.3,
        max_steps=10,
    )
    genome = np.random.default_rng(1).uniform(size=(5, 2))
    try:
        counterfactual_network_edge_weight_with_rollouts(
            genome,
            template,
            edge_from=0,
            edge_to=1,
            variant_edge_weight=2.0,
            rollout_seed=1,
            base_panic=0.05,
        )
    except ValueError as e:
        assert "neighbor_lists" in str(e).lower() or "list-only" in str(e).lower()
    else:
        raise AssertionError("expected ValueError")
