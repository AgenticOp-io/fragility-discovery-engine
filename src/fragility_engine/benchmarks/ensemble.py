"""Moonshot: ensemble fragility over topology RNG seeds (deterministic per seed)."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.network.contagion import neighbor_lists_from_adjacency
from fragility_engine.network.contagion_graph import ContagionGraph
from fragility_engine.network.graph_cli import contagion_graph_from_cli
from fragility_engine.runner import rollout_stablecoin_network
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights

_SWEEPS_1D: frozenset[str] = frozenset(
    {"er_p", "ws_p", "ws_k", "base_panic", "contagion_beta", "whale_frac"}
)


def _kw_override(kwargs: dict[str, Any], param: str, raw: float) -> None:
    if param == "ws_k":
        kwargs["ws_k"] = max(2, int(round(float(raw))))
    else:
        kwargs[param] = float(raw)


def _stablecoin_network_from_graph(
    graph: ContagionGraph,
    *,
    nodes: int,
    whale_frac: float,
    contagion_beta: float,
    max_steps: int,
    topology_representation: str,
) -> StablecoinNetworkWorld:
    """Build template from ER/WS ``ContagionGraph`` — dense adjacency or explicit neighbor lists."""

    rep = str(topology_representation)
    if rep == "dense":
        return StablecoinNetworkWorld(
            population=default_stablecoin_population(),
            adjacency=graph,
            node_weights=default_whale_weights(nodes, whale_index=0, whale_frac=float(whale_frac)),
            contagion_beta=float(contagion_beta),
            max_steps=int(max_steps),
        )
    if rep == "neighbor_lists":
        nl = neighbor_lists_from_adjacency(graph.adjacency)
        return StablecoinNetworkWorld(
            population=default_stablecoin_population(),
            neighbor_lists=nl,
            node_weights=default_whale_weights(nodes, whale_index=0, whale_frac=float(whale_frac)),
            contagion_beta=float(contagion_beta),
            max_steps=int(max_steps),
        )
    raise ValueError(f"topology_representation must be 'dense' or 'neighbor_lists', got {rep!r}")


def robustness_rollouts_over_graph_seeds(
    genome: np.ndarray,
    *,
    graph_kind: str,
    nodes: int,
    graph_seeds: list[int],
    rollout_seed: int,
    er_p: float = 0.12,
    ws_k: int = 4,
    ws_p: float = 0.15,
    base_panic: float = 0.05,
    contagion_beta: float = 0.36,
    whale_frac: float = 0.22,
    max_steps: int = 26,
    topology_representation: str = "dense",
) -> dict[str, Any]:
    """
    Same attacker genome and rollout RNG seed; only **topology** changes with ``graph_seed``.

    Each member is bitwise deterministic. Summary quantiles describe **ensemble dispersion**
    across graph draws—not stochasticity inside a single rollout.

    ``topology_representation``:
      - ``dense`` — pass ``ContagionGraph`` as ``adjacency`` (default Phase B path).
      - ``neighbor_lists`` — same ER/WS draw, but worlds use **list** topology only (**O(edges)** RAM).
    """

    runs: list[dict[str, Any]] = []
    integrals: list[float] = []
    collapses = 0

    for gs in graph_seeds:
        graph, topo_meta = contagion_graph_from_cli(
            graph_kind=graph_kind,
            nodes=nodes,
            graph_seed=int(gs),
            er_p=float(er_p),
            ws_k=int(ws_k),
            ws_p=float(ws_p),
        )
        template = _stablecoin_network_from_graph(
            graph,
            nodes=int(nodes),
            whale_frac=float(whale_frac),
            contagion_beta=float(contagion_beta),
            max_steps=int(max_steps),
            topology_representation=str(topology_representation),
        )
        r = rollout_stablecoin_network(template, genome, seed=int(rollout_seed), base_panic=float(base_panic))
        integrals.append(float(r.integral_instability))
        collapses += 1 if r.collapsed else 0
        runs.append(
            {
                "graph_seed": int(gs),
                "integral_instability": float(r.integral_instability),
                "collapsed": bool(r.collapsed),
                "attack_cost": float(r.attack_cost),
                "topology_kind": topo_meta.get("kind"),
                "topology_representation": str(topology_representation),
            }
        )

    arr = np.asarray(integrals, dtype=np.float64)
    summary = {
        "count": len(graph_seeds),
        "collapse_rate": float(collapses / max(len(graph_seeds), 1)),
        "integral_instability_mean": float(arr.mean()) if arr.size else 0.0,
        "integral_instability_std": float(arr.std(ddof=0)) if arr.size else 0.0,
        "integral_instability_p25": float(np.percentile(arr, 25)) if arr.size else 0.0,
        "integral_instability_p50": float(np.percentile(arr, 50)) if arr.size else 0.0,
        "integral_instability_p75": float(np.percentile(arr, 75)) if arr.size else 0.0,
        "integral_instability_min": float(arr.min()) if arr.size else 0.0,
        "integral_instability_max": float(arr.max()) if arr.size else 0.0,
    }

    return {
        "schema": "fragility-robustness-ensemble-v1",
        "topology_representation": str(topology_representation),
        "graph_kind": graph_kind,
        "nodes": int(nodes),
        "rollout_seed": int(rollout_seed),
        "runs": runs,
        "summary": summary,
    }


def robustness_ensemble_1d_param_sweep(
    genome: np.ndarray,
    *,
    sweep_param: str,
    sweep_values: Sequence[float],
    graph_kind: str,
    nodes: int,
    graph_seeds: list[int],
    rollout_seed: int,
    er_p: float = 0.12,
    ws_k: int = 4,
    ws_p: float = 0.15,
    base_panic: float = 0.05,
    contagion_beta: float = 0.36,
    whale_frac: float = 0.22,
    max_steps: int = 26,
    topology_representation: str = "dense",
) -> dict[str, Any]:
    """
    For each scalar in ``sweep_values``, run :func:`robustness_rollouts_over_graph_seeds`
    with that parameter overridden (same genome and ``rollout_seed``).

    Summarizes **how ensemble collapse rate and integral dispersion move** when a single
    physics or topology knob is scanned—not a full factorial design.
    """

    key = str(sweep_param)
    if key not in _SWEEPS_1D:
        raise ValueError(f"sweep_param must be one of {sorted(_SWEEPS_1D)}, got {key!r}")

    points: list[dict[str, Any]] = []
    collapse_rates: list[float] = []
    p50s: list[float] = []

    for raw in sweep_values:
        kwargs: dict[str, Any] = {
            "er_p": float(er_p),
            "ws_k": int(ws_k),
            "ws_p": float(ws_p),
            "base_panic": float(base_panic),
            "contagion_beta": float(contagion_beta),
            "whale_frac": float(whale_frac),
            "max_steps": int(max_steps),
        }
        _kw_override(kwargs, key, float(raw))

        ens = robustness_rollouts_over_graph_seeds(
            genome,
            graph_kind=graph_kind,
            nodes=int(nodes),
            graph_seeds=graph_seeds,
            rollout_seed=int(rollout_seed),
            topology_representation=str(topology_representation),
            **kwargs,
        )
        s = ens["summary"]
        collapse_rates.append(float(s["collapse_rate"]))
        p50s.append(float(s["integral_instability_p50"]))
        sv = float(kwargs["ws_k"]) if key == "ws_k" else float(raw)
        points.append({"sweep_value": sv, "ensemble": ens})

    cr = np.asarray(collapse_rates, dtype=np.float64)
    p50a = np.asarray(p50s, dtype=np.float64)
    summary = {
        "sweep_steps": len(points),
        "graph_seed_count": len(graph_seeds),
        "collapse_rate_min": float(cr.min()) if cr.size else 0.0,
        "collapse_rate_max": float(cr.max()) if cr.size else 0.0,
        "collapse_rate_spread": float(cr.max() - cr.min()) if cr.size else 0.0,
        "integral_instability_p50_min": float(p50a.min()) if p50a.size else 0.0,
        "integral_instability_p50_max": float(p50a.max()) if p50a.size else 0.0,
    }

    return {
        "schema": "fragility-robustness-sensitivity-1d-v1",
        "sweep_param": key,
        "sweep_values": [float(x) for x in sweep_values],
        "graph_kind": graph_kind,
        "nodes": int(nodes),
        "rollout_seed": int(rollout_seed),
        "topology_representation": str(topology_representation),
        "points": points,
        "summary": summary,
    }


def robustness_ensemble_2d_param_grid(
    genome: np.ndarray,
    *,
    sweep_param_x: str,
    sweep_values_x: Sequence[float],
    sweep_param_y: str,
    sweep_values_y: Sequence[float],
    graph_kind: str,
    nodes: int,
    graph_seeds: list[int],
    rollout_seed: int,
    er_p: float = 0.12,
    ws_k: int = 4,
    ws_p: float = 0.15,
    base_panic: float = 0.05,
    contagion_beta: float = 0.36,
    whale_frac: float = 0.22,
    max_steps: int = 26,
    topology_representation: str = "dense",
) -> dict[str, Any]:
    """
    Cartesian product of two 1D sweeps; each grid cell is a full
    :func:`robustness_rollouts_over_graph_seeds` (same ``graph_seeds``).
    """

    px, py = str(sweep_param_x), str(sweep_param_y)
    if px not in _SWEEPS_1D or py not in _SWEEPS_1D:
        raise ValueError(f"sweep params must be in {sorted(_SWEEPS_1D)}")
    if px == py:
        raise ValueError("sweep_param_x and sweep_param_y must differ")

    points: list[dict[str, Any]] = []
    collapse_rates: list[float] = []
    p50s: list[float] = []

    for raw_x in sweep_values_x:
        for raw_y in sweep_values_y:
            kwargs: dict[str, Any] = {
                "er_p": float(er_p),
                "ws_k": int(ws_k),
                "ws_p": float(ws_p),
                "base_panic": float(base_panic),
                "contagion_beta": float(contagion_beta),
                "whale_frac": float(whale_frac),
                "max_steps": int(max_steps),
            }
            _kw_override(kwargs, px, float(raw_x))
            _kw_override(kwargs, py, float(raw_y))

            ens = robustness_rollouts_over_graph_seeds(
                genome,
                graph_kind=graph_kind,
                nodes=int(nodes),
                graph_seeds=graph_seeds,
                rollout_seed=int(rollout_seed),
                topology_representation=str(topology_representation),
                **kwargs,
            )
            s = ens["summary"]
            collapse_rates.append(float(s["collapse_rate"]))
            p50s.append(float(s["integral_instability_p50"]))
            sx = float(kwargs["ws_k"]) if px == "ws_k" else float(raw_x)
            sy = float(kwargs["ws_k"]) if py == "ws_k" else float(raw_y)
            points.append({"sweep_x": sx, "sweep_y": sy, "ensemble": ens})

    cr = np.asarray(collapse_rates, dtype=np.float64)
    p50a = np.asarray(p50s, dtype=np.float64)
    summary = {
        "grid_cells": len(points),
        "sweep_steps_x": len(list(sweep_values_x)),
        "sweep_steps_y": len(list(sweep_values_y)),
        "graph_seed_count": len(graph_seeds),
        "collapse_rate_min": float(cr.min()) if cr.size else 0.0,
        "collapse_rate_max": float(cr.max()) if cr.size else 0.0,
        "collapse_rate_spread": float(cr.max() - cr.min()) if cr.size else 0.0,
        "integral_instability_p50_min": float(p50a.min()) if p50a.size else 0.0,
        "integral_instability_p50_max": float(p50a.max()) if p50a.size else 0.0,
    }

    return {
        "schema": "fragility-robustness-sensitivity-2d-v1",
        "sweep_param_x": px,
        "sweep_param_y": py,
        "sweep_values_x": [float(x) for x in sweep_values_x],
        "sweep_values_y": [float(y) for y in sweep_values_y],
        "graph_kind": graph_kind,
        "nodes": int(nodes),
        "rollout_seed": int(rollout_seed),
        "topology_representation": str(topology_representation),
        "points": points,
        "summary": summary,
    }
