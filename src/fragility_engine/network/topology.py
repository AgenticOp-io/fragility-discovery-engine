from __future__ import annotations

import numpy as np

try:
    import networkx as nx
except ImportError as e:  # pragma: no cover
    raise ImportError("fragility_engine.network requires the `networkx` package.") from e


def adjacency_erdos_renyi(n: int, p: float, *, seed: int) -> np.ndarray:
    """Undirected ER graph as dense {0,1} adjacency (deterministic via NetworkX seed)."""

    g = nx.erdos_renyi_graph(n, p, seed=seed)
    return nx.to_numpy_array(g, dtype=np.int8)


def adjacency_watts_strogatz(n: int, k: int, p: float, *, seed: int) -> np.ndarray:
    """Watts–Strogatz small-world (ring + random rewires)."""

    g = nx.watts_strogatz_graph(n, k, p, seed=seed)
    return nx.to_numpy_array(g, dtype=np.int8)
