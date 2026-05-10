"""Thread-safe world clones must not reuse template AgentPopulation."""

from __future__ import annotations

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution.defender import clone_resource_cascade, clone_stablecoin_network
from fragility_engine.coevolution.thread_safe_template import (
    thread_safe_network_clone,
    thread_safe_peg_clone,
    thread_safe_resource_cascade_clone,
)
from fragility_engine.network.contagion_graph import ContagionGraph
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def test_thread_safe_peg_clone_fresh_population():
    pop = default_stablecoin_population()
    t = StablecoinPegWorld(population=pop, max_steps=30)
    c = thread_safe_peg_clone(t)
    assert c.population is not t.population


def test_clone_stablecoin_network_respects_population_override():
    graph = ContagionGraph.erdos_renyi(8, p=0.2, seed=1)
    n = graph.n_nodes
    w = default_whale_weights(n, whale_index=0, whale_frac=0.2)
    t = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=w,
        max_steps=20,
    )
    alt = default_stablecoin_population()
    c = clone_stablecoin_network(t, population=alt)
    assert c.population is alt
    assert c.population is not t.population


def test_thread_safe_network_clone_fresh_population():
    graph = ContagionGraph.erdos_renyi(8, p=0.2, seed=2)
    n = graph.n_nodes
    w = default_whale_weights(n, whale_index=0, whale_frac=0.2)
    t = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=w,
        max_steps=20,
    )
    c = thread_safe_network_clone(t)
    assert c.population is not t.population


def test_clone_resource_cascade_respects_population_override():
    t = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=18)
    alt = default_stablecoin_population()
    c = clone_resource_cascade(t, population=alt)
    assert c.population is alt
    assert c.population is not t.population


def test_thread_safe_resource_cascade_clone_fresh_population():
    t = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=18)
    c = thread_safe_resource_cascade_clone(t)
    assert c.population is not t.population
