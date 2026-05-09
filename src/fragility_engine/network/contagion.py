from __future__ import annotations

import numpy as np


def neighbor_lists_from_adjacency(adj: np.ndarray) -> list[list[int]]:
    """Row-wise neighbor indices (nonzero adjacency). Built once; contagion then **O(edges)** per step."""

    adj = np.asarray(adj)
    n = adj.shape[0]
    return [np.flatnonzero(adj[i]).astype(np.int32).tolist() for i in range(n)]


def out_edge_count(neighbors: list[list[int]]) -> int:
    """Sum of out-degree (interpret neighbors as directed out-edges)."""

    return sum(len(row) for row in neighbors)


def neighbor_average_panic_lists(
    panic: np.ndarray,
    neighbors: list[list[int]],
    *,
    weights: list[list[float]] | None = None,
) -> np.ndarray:
    """
    Directed out-neighbor averaging; isolated nodes → 0 (matches dense binary convention).

    ``weights[i][k]`` pairs with ``neighbors[i][k]`` (positive weights; normalized convex combo).
    """

    panic = np.asarray(panic, dtype=np.float64)
    out = np.zeros_like(panic, dtype=np.float64)
    if weights is None:
        for i, nb in enumerate(neighbors):
            if not nb:
                out[i] = 0.0
            else:
                out[i] = float(np.mean(panic[nb]))
        return out

    if len(weights) != len(neighbors):
        raise ValueError("weights must have one row per node")
    for i, nb in enumerate(neighbors):
        if not nb:
            out[i] = 0.0
            continue
        ws = weights[i]
        if len(ws) != len(nb):
            raise ValueError(f"weights[{i}] length must match neighbors[{i}]")
        w_arr = np.asarray(ws, dtype=np.float64)
        if np.any(w_arr <= 0):
            raise ValueError("neighbor weights must be positive")
        idx = np.asarray(nb, dtype=np.int32)
        den = float(np.sum(w_arr))
        out[i] = float(np.dot(w_arr, panic[idx]) / max(den, 1e-18))
    return out


def contagion_step_lists(
    panic: np.ndarray,
    neighbors: list[list[int]],
    beta: float,
    *,
    neighbor_weights: list[list[float]] | None = None,
) -> np.ndarray:
    """Diffusion toward (possibly weighted) out-neighbor averages."""

    neigh = neighbor_average_panic_lists(panic, neighbors, weights=neighbor_weights)
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
