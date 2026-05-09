"""Epsilon sweeps over scalar network physics."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.sweep import SCHEMA, sweep_network_scalar_axis
from fragility_engine.network.contagion_graph import ContagionGraph
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights


def test_sweep_base_panic_axis():
    graph = ContagionGraph.erdos_renyi(14, p=0.14, seed=55)
    n = graph.n_nodes
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=default_whale_weights(n, whale_index=0, whale_frac=0.21),
        contagion_beta=0.33,
        max_steps=20,
    )
    genome = np.random.default_rng(4).uniform(size=(9, 2))
    out = sweep_network_scalar_axis(
        genome,
        template,
        axis="base_panic",
        values=[0.05, 0.12, 0.2],
        rollout_seed=7070,
    )
    assert out["schema"] == SCHEMA
    assert out["axis"] == "base_panic"
    assert len(out["runs"]) == 3
    assert out["summary"]["count"] == 3


def test_sweep_contagion_beta_requires_fixed_panic():
    graph = ContagionGraph.erdos_renyi(12, p=0.16, seed=56)
    n = graph.n_nodes
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=default_whale_weights(n, whale_index=0, whale_frac=0.2),
        contagion_beta=0.4,
        max_steps=18,
    )
    genome = np.random.default_rng(5).uniform(size=(8, 2))
    try:
        sweep_network_scalar_axis(
            genome,
            template,
            axis="contagion_beta",
            values=[0.1, 0.35],
            rollout_seed=8080,
            fixed_base_panic=None,
        )
    except ValueError as e:
        assert "fixed_base_panic" in str(e).lower()
    else:
        raise AssertionError("expected ValueError")

    out = sweep_network_scalar_axis(
        genome,
        template,
        axis="contagion_beta",
        values=[0.1, 0.35],
        rollout_seed=8080,
        fixed_base_panic=0.07,
    )
    assert len(out["runs"]) == 2
    assert "contagion_beta" in out["runs"][0]
