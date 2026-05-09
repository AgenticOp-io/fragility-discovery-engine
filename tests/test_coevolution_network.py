"""Alternating co-evolution on contagion network (Phase G)."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution import alternating_coevolution_network, alternating_coevolution_rollout
from fragility_engine.network.contagion_graph import ContagionGraph
from fragility_engine.runner import rollout_stablecoin_network
from fragility_engine.types import RolloutResult
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights


def test_alternating_coevolution_network_smoke():
    graph = ContagionGraph.erdos_renyi(16, p=0.15, seed=505)
    n = graph.n_nodes
    weights = default_whale_weights(n, whale_index=0, whale_frac=0.22)
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=weights,
        max_steps=24,
    )
    summary = alternating_coevolution_network(
        template,
        rounds=1,
        attacker_horizon=9,
        attacker_generations=2,
        attacker_population=8,
        defender_generations=2,
        defender_population=7,
        seed=7071,
    )
    assert summary.simulation_mode == "network"
    assert summary.last_rollout is not None
    assert summary.last_rollout.simulation_mode == "network"
    assert len(summary.rounds) == 1


def test_alternating_coevolution_rollout_custom_injection():
    """Hook accepts custom deterministic rollouts (extensibility for large / bespoke worlds)."""

    graph = ContagionGraph.erdos_renyi(12, p=0.2, seed=3)
    n = graph.n_nodes
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=default_whale_weights(n, whale_index=0, whale_frac=0.2),
        max_steps=18,
    )

    def rollout_fn(g: np.ndarray, s: int, d: np.ndarray) -> RolloutResult:
        return rollout_stablecoin_network(template, g, seed=s, defender_genome=d)

    summary = alternating_coevolution_rollout(
        rollout_fn,
        rounds=1,
        attacker_horizon=8,
        attacker_generations=2,
        attacker_population=6,
        defender_generations=2,
        defender_population=5,
        seed=1212,
        simulation_mode="custom_probe",
    )
    assert summary.simulation_mode == "custom_probe"
    assert summary.last_rollout is not None


def test_alternating_coevolution_network_collect_attacker_pareto():
    graph = ContagionGraph.erdos_renyi(14, p=0.16, seed=909)
    n = graph.n_nodes
    weights = default_whale_weights(n, whale_index=0, whale_frac=0.22)
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=weights,
        max_steps=20,
    )
    summary = alternating_coevolution_network(
        template,
        rounds=1,
        collect_attacker_pareto=True,
        attacker_horizon=8,
        attacker_generations=2,
        attacker_population=10,
        defender_generations=2,
        defender_population=6,
        seed=424_424,
    )
    assert len(summary.rounds) == 1
    arch = summary.rounds[0].get("attacker_pareto")
    assert isinstance(arch, list)
    assert len(arch) >= 1
    assert "severity" in arch[0] and "attack_cost" in arch[0]
