"""Ordered cumulative network mutation chains."""

from __future__ import annotations

import numpy as np
import pytest

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual_chain import (
    CHAIN_SPEC_SCHEMA,
    counterfactual_network_mutation_chain_with_rollouts,
    mutation_chain_path_rollouts,
    parse_chain_spec_payload,
)
from fragility_engine.explain.trace import CHAIN_PATH_TRACE_SCHEMA, mutation_chain_path_to_trace
from fragility_engine.network.contagion_graph import ContagionGraph
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights


def test_parse_chain_edge_weights_patch():
    steps = parse_chain_spec_payload(
        {
            "schema": CHAIN_SPEC_SCHEMA,
            "steps": [
                {
                    "kind": "edge_weights_patch",
                    "edges": [
                        {"from": 0, "to": 1, "weight": 2.0},
                        {"from": 1, "to": 0, "weight": 3.0},
                    ],
                }
            ],
        }
    )
    assert steps[0]["kind"] == "edge_weights_patch"
    assert len(steps[0]["edges"]) == 2


def test_parse_chain_spec_payload_smoke():
    steps = parse_chain_spec_payload(
        {
            "schema": CHAIN_SPEC_SCHEMA,
            "steps": [
                {"kind": "contagion_beta", "value": 0.11},
                {"kind": "edge_weight", "from": 0, "to": 1, "weight": 2.5},
            ],
        }
    )
    assert len(steps) == 2
    assert steps[0]["kind"] == "contagion_beta"
    assert steps[1]["weight"] == 2.5


def test_mutation_chain_empty_steps_raises():
    nl = [[1], [0]]
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        neighbor_lists=nl,
        node_weights=default_whale_weights(2, whale_index=0, whale_frac=0.25),
        contagion_beta=0.35,
        max_steps=10,
    )
    genome = np.random.default_rng(1).uniform(size=(4, 2))
    with pytest.raises(ValueError, match="non-empty"):
        counterfactual_network_mutation_chain_with_rollouts(
            genome, template, steps=[], rollout_seed=1, base_panic=0.05
        )


def test_parse_chain_spec_rejects_bad_schema():
    with pytest.raises(ValueError, match="schema"):
        parse_chain_spec_payload({"schema": "wrong", "steps": [{"kind": "contagion_beta", "value": 0.1}]})


def test_mutation_chain_beta_only_dense_smoke():
    graph = ContagionGraph.erdos_renyi(12, p=0.14, seed=88)
    n = graph.n_nodes
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=default_whale_weights(n, whale_index=0, whale_frac=0.2),
        contagion_beta=0.4,
        max_steps=18,
    )
    genome = np.random.default_rng(5).uniform(size=(8, 2))
    report, base, var = counterfactual_network_mutation_chain_with_rollouts(
        genome,
        template,
        steps=[
            {"kind": "contagion_beta", "value": 0.35},
            {"kind": "contagion_beta", "value": 0.08},
        ],
        rollout_seed=505,
        base_panic=0.06,
    )
    assert report["intervention"] == "network_mutation_chain"
    assert len(report["mutation_steps"]) == 2
    assert base.simulation_mode == var.simulation_mode == "network"


def test_mutation_chain_edge_weight_on_dense_raises():
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
    with pytest.raises(ValueError, match="neighbor_lists"):
        counterfactual_network_mutation_chain_with_rollouts(
            genome,
            template,
            steps=[{"kind": "edge_weight", "from": 0, "to": 1, "weight": 2.0}],
            rollout_seed=1,
            base_panic=0.05,
        )


def test_mutation_chain_path_rollouts_match_bundle_endpoints():
    nl = [[1], [0]]
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        neighbor_lists=nl,
        node_weights=default_whale_weights(2, whale_index=0, whale_frac=0.25),
        contagion_beta=0.4,
        max_steps=15,
    )
    genome = np.random.default_rng(12).uniform(size=(7, 2))
    steps = [{"kind": "contagion_beta", "value": 0.22}]
    _, base, var = counterfactual_network_mutation_chain_with_rollouts(
        genome,
        template,
        steps=steps,
        rollout_seed=707,
        base_panic=0.06,
        variant_base_panic=0.11,
    )
    path = mutation_chain_path_rollouts(
        genome,
        template,
        steps=steps,
        rollout_seed=707,
        base_panic=0.06,
        variant_base_panic=0.11,
    )
    assert len(path) == 2
    assert path[0].integral_instability == base.integral_instability
    assert path[-1].integral_instability == var.integral_instability


def test_mutation_chain_path_to_trace_smoke():
    nl = [[1], [0]]
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        neighbor_lists=nl,
        node_weights=default_whale_weights(2, whale_index=0, whale_frac=0.25),
        contagion_beta=0.38,
        max_steps=12,
    )
    genome = np.random.default_rng(3).uniform(size=(5, 2))
    steps = [
        {"kind": "contagion_beta", "value": 0.25},
        {"kind": "edge_weight", "from": 0, "to": 1, "weight": 2.0},
    ]
    path = mutation_chain_path_rollouts(
        genome,
        template,
        steps=steps,
        rollout_seed=808,
        base_panic=0.07,
        variant_base_panic=0.07,
    )
    tr = mutation_chain_path_to_trace(
        path,
        steps,
        rollout_seed=808,
        baseline_base_panic=0.07,
        variant_base_panic=0.07,
    )
    assert tr["schema"] == CHAIN_PATH_TRACE_SCHEMA
    assert len(tr["nodes"]) == 3
    assert len(tr["edges"]) == 2
    assert tr["edges"][0]["step"]["kind"] == "contagion_beta"
    assert tr["edges"][1]["step"]["kind"] == "edge_weight"


def test_mutation_chain_beta_then_edge_list_topology():
    nl = [[1], [0]]
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        neighbor_lists=nl,
        node_weights=default_whale_weights(2, whale_index=0, whale_frac=0.25),
        contagion_beta=0.42,
        max_steps=14,
    )
    genome = np.random.default_rng(9).uniform(size=(6, 2))
    report, _, _ = counterfactual_network_mutation_chain_with_rollouts(
        genome,
        template,
        steps=[
            {"kind": "contagion_beta", "value": 0.2},
            {"kind": "edge_weight", "from": 0, "to": 1, "weight": 4.0},
        ],
        rollout_seed=606,
        base_panic=0.07,
        variant_base_panic=0.09,
    )
    assert report["variant_base_panic"] == 0.09
    assert report["baseline_base_panic"] == 0.07
