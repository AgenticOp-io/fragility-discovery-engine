from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fragility_engine.network.topology import adjacency_erdos_renyi, adjacency_watts_strogatz


@dataclass(frozen=True)
class ContagionGraph:
    """
    Thin façade over a dense unweighted adjacency matrix (Phase B).

    Use this type at API boundaries; physics still consumes ``adjacency`` as ``ndarray``.
    """

    adjacency: np.ndarray

    def __post_init__(self) -> None:
        adj = np.asarray(self.adjacency, dtype=np.int8)
        if adj.ndim != 2 or adj.shape[0] != adj.shape[1]:
            raise ValueError("adjacency must be square")
        object.__setattr__(self, "adjacency", adj)

    @property
    def n_nodes(self) -> int:
        return int(self.adjacency.shape[0])

    @classmethod
    def erdos_renyi(cls, n: int, p: float, *, seed: int) -> ContagionGraph:
        return cls(adjacency=adjacency_erdos_renyi(n, p, seed=seed))

    @classmethod
    def watts_strogatz(cls, n: int, k: int, p: float, *, seed: int) -> ContagionGraph:
        return cls(adjacency=adjacency_watts_strogatz(n, k, p, seed=seed))

    @classmethod
    def complete(cls, n: int) -> ContagionGraph:
        """Fully connected simple graph (deterministic, no RNG). Requires ``n >= 2``."""

        if n < 2:
            raise ValueError("complete graph requires n >= 2 (use ContagionGraph.self_loop() for n=1)")
        adj = np.ones((n, n), dtype=np.int8) - np.eye(n, dtype=np.int8)
        return cls(adjacency=adj)

    @classmethod
    def self_loop(cls) -> ContagionGraph:
        """Single node with a self-edge so neighbor-average equals self-state."""

        return cls(adjacency=np.ones((1, 1), dtype=np.int8))

    @classmethod
    def from_neighbor_lists(
        cls,
        neighbors: list[list[int]],
        *,
        symmetrize: bool = True,
    ) -> ContagionGraph:
        """Build from per-node neighbor indices (optionally symmetrize for undirected diffusion)."""

        n = len(neighbors)
        adj = np.zeros((n, n), dtype=np.int8)
        for i, nb in enumerate(neighbors):
            for j in nb:
                jj = int(j)
                if 0 <= jj < n:
                    adj[i, jj] = 1
        if symmetrize:
            adj = np.bitwise_or(adj, adj.T).astype(np.int8, copy=False)
        return cls(adjacency=adj)

    def undirected_edge_count(self) -> int:
        """Edges in the upper triangle (expects symmetric simple adjacency)."""

        a = self.adjacency
        return int(np.triu(a, k=1).sum())
