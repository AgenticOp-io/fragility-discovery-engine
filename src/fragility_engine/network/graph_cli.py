"""Construct :class:`~fragility_engine.network.contagion_graph.ContagionGraph` from CLI-style flags."""

from __future__ import annotations

from typing import Any

from fragility_engine.network.contagion_graph import ContagionGraph


def contagion_graph_from_cli(
    *,
    graph_kind: str,
    nodes: int,
    graph_seed: int,
    er_p: float,
    ws_k: int,
    ws_p: float,
) -> tuple[ContagionGraph, dict[str, Any]]:
    """
    Deterministic topology for scripts.

    ``watts_strogatz`` requires even ``ws_k`` and ``nodes > ws_k`` (NetworkX layout).
    """

    n = int(nodes)
    seed = int(graph_seed)
    if graph_kind == "erdos_renyi":
        g = ContagionGraph.erdos_renyi(n, p=float(er_p), seed=seed)
        return g, {"kind": "erdos_renyi", "nodes": n, "p": float(er_p), "seed": seed}
    if graph_kind != "watts_strogatz":
        raise ValueError(f"unknown graph_kind {graph_kind!r}")
    k = int(ws_k)
    if k % 2 != 0 or k >= n:
        raise ValueError("watts_strogatz requires even ws_k and nodes > ws_k")
    g = ContagionGraph.watts_strogatz(n, k, float(ws_p), seed=seed)
    return g, {"kind": "watts_strogatz", "nodes": n, "k": k, "p": float(ws_p), "seed": seed}
