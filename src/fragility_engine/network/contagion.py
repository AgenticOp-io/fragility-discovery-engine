from __future__ import annotations

import numpy as np


def neighbor_lists_from_adjacency(adj: np.ndarray) -> list[list[int]]:
    """Row-wise neighbor indices (nonzero adjacency). Built once; contagion then **O(edges)** per step."""

    adj = np.asarray(adj)
    n = adj.shape[0]
    return [np.flatnonzero(adj[i]).astype(np.int32).tolist() for i in range(n)]


def neighbor_average_panic_lists(panic: np.ndarray, neighbors: list[list[int]]) -> np.ndarray:
    """Same semantics as :func:`neighbor_average_panic` for binary graphs (isolated nodes → 0)."""

    panic = np.asarray(panic, dtype=np.float64)
    out = np.zeros_like(panic, dtype=np.float64)
    for i, nb in enumerate(neighbors):
        if not nb:
            out[i] = 0.0
        else:
            out[i] = float(np.sum(panic[nb])) / len(nb)
    return out


def contagion_step_lists(panic: np.ndarray, neighbors: list[list[int]], beta: float) -> np.ndarray:
    """Diffusion step using precomputed neighbor lists (avoids dense ``adj @ panic`` each timestep)."""

    neigh = neighbor_average_panic_lists(panic, neighbors)
    beta = float(np.clip(beta, 0.0, 1.0))
    out = (1.0 - beta) * panic + beta * neigh
    return np.clip(out, 0.0, 1.0)


def neighbor_average_panic(panic: np.ndarray, adj: np.ndarray) -> np.ndarray:
    """Row-normalized neighbor mean; isolated nodes fall back to self-average."""

    adj = np.asarray(adj, dtype=np.float64)
    panic = np.asarray(panic, dtype=np.float64)
    deg = np.maximum(adj.sum(axis=1), 1.0)
    return (adj @ panic) / deg


def contagion_step(panic: np.ndarray, adj: np.ndarray, beta: float) -> np.ndarray:
    """Convex blend toward neighbor-average panic (diffusion on the graph)."""

    neigh = neighbor_average_panic(panic, adj)
    beta = float(np.clip(beta, 0.0, 1.0))
    out = (1.0 - beta) * panic + beta * neigh
    return np.clip(out, 0.0, 1.0)
