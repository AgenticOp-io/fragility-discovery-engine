"""Twin-domain composite artifact (moonshot — decoupled kernels)."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.benchmarks.institutional_composite import twin_domain_rollout_artifact
from fragility_engine.network.contagion_graph import ContagionGraph
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights


def test_twin_domain_rollout_artifact_schema():
    graph = ContagionGraph.erdos_renyi(9, p=0.2, seed=3)
    n = graph.n_nodes
    net = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=default_whale_weights(n, whale_index=0, whale_frac=0.18),
        contagion_beta=0.33,
        max_steps=18,
    )
    rc = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=16)
    rng = np.random.default_rng(21)
    genome = rng.uniform(size=(8, 2))

    out = twin_domain_rollout_artifact(net, rc, genome, network_seed=100, cascade_seed=101)
    assert out["schema"] == "fragility-institutional-composite-v1"
    assert "network" in out and "resource_cascade" in out
    for key in ("integral_instability", "collapsed", "attack_cost", "simulation_mode"):
        assert key in out["network"]
        assert key in out["resource_cascade"]
