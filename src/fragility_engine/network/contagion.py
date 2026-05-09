from __future__ import annotations

import numpy as np


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
