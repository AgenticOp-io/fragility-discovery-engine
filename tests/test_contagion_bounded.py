from __future__ import annotations

import numpy as np

from fragility_engine.network.contagion import contagion_step, contagion_step_lists, neighbor_lists_from_adjacency
from fragility_engine.network.contagion_graph import ContagionGraph


def test_contagion_step_keeps_panic_in_unit_interval():
    rng = np.random.default_rng(99)
    graph = ContagionGraph.erdos_renyi(32, p=0.18, seed=7)
    panic = rng.uniform(size=(graph.n_nodes,))
    adj = graph.adjacency
    for _ in range(200):
        panic = contagion_step(panic, adj, beta=0.41)
        assert np.all(panic >= -1e-9)
        assert np.all(panic <= 1.0 + 1e-9)


def test_contagion_lists_matches_dense_matmul():
    rng = np.random.default_rng(101)
    graph = ContagionGraph.erdos_renyi(48, p=0.14, seed=11)
    adj = graph.adjacency.astype(np.float64)
    nbl = neighbor_lists_from_adjacency(adj)
    panic = rng.uniform(size=(graph.n_nodes,))
    beta = 0.39
    d = contagion_step(panic.copy(), adj, beta)
    ell = contagion_step_lists(panic.copy(), nbl, beta)
    np.testing.assert_allclose(d, ell, rtol=1e-14, atol=1e-14)


def test_contagion_graph_complete_has_expected_degree():
    g = ContagionGraph.complete(5)
    deg = g.adjacency.sum(axis=1)
    assert np.all(deg == 4)
