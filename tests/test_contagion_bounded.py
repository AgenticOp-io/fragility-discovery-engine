from __future__ import annotations

import numpy as np

from fragility_engine.network.contagion import contagion_step
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


def test_contagion_graph_complete_has_expected_degree():
    g = ContagionGraph.complete(5)
    deg = g.adjacency.sum(axis=1)
    assert np.all(deg == 4)
