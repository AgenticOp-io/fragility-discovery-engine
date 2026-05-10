"""Moonshot: ensemble fragility over topology RNG seeds (deterministic per seed)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.network.contagion import neighbor_lists_from_adjacency
from fragility_engine.network.contagion_graph import ContagionGraph
from fragility_engine.network.graph_cli import contagion_graph_from_cli
from fragility_engine.network.neighbor_io import load_neighbor_topology
from fragility_engine.runner import rollout_stablecoin_network
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights

_SWEEPS_1D: frozenset[str] = frozenset(
    {"er_p", "ws_p", "ws_k", "base_panic", "contagion_beta", "whale_frac"}
)
_SYNTHETIC_TOPOLOGY_SWEEPS: frozenset[str] = frozenset({"er_p", "ws_p", "ws_k"})


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


def _neighbor_bundle_weights_list(
    neighbor_weights_json_paths: Sequence[Path | str | None] | None,
    n_paths: int,
) -> list[Path | None]:
    if neighbor_weights_json_paths is None:
        return [None] * n_paths
    wseq = list(neighbor_weights_json_paths)
    if len(wseq) != n_paths:
        raise ValueError(
            f"neighbor_weights_json_paths length {len(wseq)} must match neighbor_json_paths {n_paths}"
        )
    out: list[Path | None] = []
    for p in wseq:
        if p is None:
            out.append(None)
        else:
            out.append(Path(p))
    return out


def robustness_rollouts_neighbor_json_bundle(
    genome: np.ndarray,
    *,
    neighbor_json_paths: Sequence[Path | str],
    rollout_seed: int,
    contagion_beta: float = 0.36,
    whale_frac: float = 0.22,
    base_panic: float = 0.05,
    max_steps: int = 26,
    neighbor_weights_json_paths: Sequence[Path | str | None] | None = None,
) -> dict[str, Any]:
    """
    One rollout per JSON topology file (list-only format per :func:`load_neighbor_topology`).
    Dispersion is across **user-supplied graphs**, not ER/WS ``graph_seed``.
    """

    paths = [Path(p) for p in neighbor_json_paths]
    if not paths:
        raise ValueError("neighbor_json_paths must be non-empty")
    weights_paths = _neighbor_bundle_weights_list(neighbor_weights_json_paths, len(paths))

    runs: list[dict[str, Any]] = []
    integrals: list[float] = []
    collapses = 0

    for i, lists_path in enumerate(paths):
        nl, nw = load_neighbor_topology(lists_path, weights_paths[i])
        n_nodes = len(nl)
        template = StablecoinNetworkWorld(
            population=default_stablecoin_population(),
            neighbor_lists=nl,
            neighbor_weights=nw,
            node_weights=default_whale_weights(n_nodes, whale_index=0, whale_frac=float(whale_frac)),
            contagion_beta=float(contagion_beta),
            max_steps=int(max_steps),
        )
        r = rollout_stablecoin_network(template, genome, seed=int(rollout_seed), base_panic=float(base_panic))
        integrals.append(float(r.integral_instability))
        collapses += 1 if r.collapsed else 0
        runs.append(
            {
                "topology_index": int(i),
                "neighbor_json": str(lists_path.as_posix()),
                "n_nodes": int(n_nodes),
                "integral_instability": float(r.integral_instability),
                "collapsed": bool(r.collapsed),
                "attack_cost": float(r.attack_cost),
                "topology_kind": "neighbor_json",
                "topology_representation": "neighbor_lists",
            }
        )

    arr = np.asarray(integrals, dtype=np.float64)
    summary = {
        "count": len(paths),
        "collapse_rate": float(collapses / max(len(paths), 1)),
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
        "topology_mode": "neighbor_json_bundle",
        "topology_representation": "neighbor_lists",
        "neighbor_json_paths": [str(p.as_posix()) for p in paths],
        "graph_kind": None,
        "nodes": None,
        "rollout_seed": int(rollout_seed),
        "runs": runs,
        "summary": summary,
    }


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
        "topology_mode": "synthetic_er_ws",
        "topology_representation": str(topology_representation),
        "neighbor_json_paths": None,
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
    neighbor_json_paths: Sequence[Path | str] | None = None,
    neighbor_weights_json_paths: Sequence[Path | str | None] | None = None,
) -> dict[str, Any]:
    """
    For each scalar in ``sweep_values``, run :func:`robustness_rollouts_over_graph_seeds`
    with that parameter overridden (same genome and ``rollout_seed``).

    Summarizes **how ensemble collapse rate and integral dispersion move** when a single
    physics or topology knob is scanned—not a full factorial design.

    If ``neighbor_json_paths`` is set, sweeps physics knobs over the **fixed** neighbor-json bundle
    (no ER/WS draws).
    """

    key = str(sweep_param)
    if key not in _SWEEPS_1D:
        raise ValueError(f"sweep_param must be one of {sorted(_SWEEPS_1D)}, got {key!r}")
    if neighbor_json_paths is not None and key in _SYNTHETIC_TOPOLOGY_SWEEPS:
        raise ValueError(
            "er_p / ws_p / ws_k sweeps apply only to synthetic ER/WS ensembles; "
            "with neighbor_json_paths use base_panic, contagion_beta, or whale_frac."
        )

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

        if neighbor_json_paths is not None:
            ens = robustness_rollouts_neighbor_json_bundle(
                genome,
                neighbor_json_paths=neighbor_json_paths,
                rollout_seed=int(rollout_seed),
                contagion_beta=float(kwargs["contagion_beta"]),
                whale_frac=float(kwargs["whale_frac"]),
                base_panic=float(kwargs["base_panic"]),
                max_steps=int(kwargs["max_steps"]),
                neighbor_weights_json_paths=neighbor_weights_json_paths,
            )
        else:
            ens = robustness_rollouts_over_graph_seeds(
                genome,
                graph_kind=graph_kind,
                nodes=int(nodes),
                graph_seeds=graph_seeds,
                rollout_seed=int(rollout_seed),
                topology_representation=str(topology_representation),
                er_p=float(kwargs["er_p"]),
                ws_k=int(kwargs["ws_k"]),
                ws_p=float(kwargs["ws_p"]),
                base_panic=float(kwargs["base_panic"]),
                contagion_beta=float(kwargs["contagion_beta"]),
                whale_frac=float(kwargs["whale_frac"]),
                max_steps=int(kwargs["max_steps"]),
            )
        s = ens["summary"]
        collapse_rates.append(float(s["collapse_rate"]))
        p50s.append(float(s["integral_instability_p50"]))
        sv = float(kwargs["ws_k"]) if key == "ws_k" else float(raw)
        points.append({"sweep_value": sv, "ensemble": ens})

    cr = np.asarray(collapse_rates, dtype=np.float64)
    p50a = np.asarray(p50s, dtype=np.float64)
    member_count = (
        len(list(neighbor_json_paths)) if neighbor_json_paths is not None else len(graph_seeds)
    )
    summary = {
        "sweep_steps": len(points),
        "graph_seed_count": member_count,
        "collapse_rate_min": float(cr.min()) if cr.size else 0.0,
        "collapse_rate_max": float(cr.max()) if cr.size else 0.0,
        "collapse_rate_spread": float(cr.max() - cr.min()) if cr.size else 0.0,
        "integral_instability_p50_min": float(p50a.min()) if p50a.size else 0.0,
        "integral_instability_p50_max": float(p50a.max()) if p50a.size else 0.0,
    }

    out: dict[str, Any] = {
        "schema": "fragility-robustness-sensitivity-1d-v1",
        "sweep_param": key,
        "sweep_values": [float(x) for x in sweep_values],
        "rollout_seed": int(rollout_seed),
        "points": points,
        "summary": summary,
    }
    if neighbor_json_paths is not None:
        out["topology_mode"] = "neighbor_json_bundle"
        out["neighbor_json_paths"] = [str(Path(p).as_posix()) for p in neighbor_json_paths]
        out["graph_kind"] = None
        out["nodes"] = None
        out["topology_representation"] = "neighbor_lists"
    else:
        out["topology_mode"] = "synthetic_er_ws"
        out["neighbor_json_paths"] = None
        out["graph_kind"] = graph_kind
        out["nodes"] = int(nodes)
        out["topology_representation"] = str(topology_representation)
    return out


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
    neighbor_json_paths: Sequence[Path | str] | None = None,
    neighbor_weights_json_paths: Sequence[Path | str | None] | None = None,
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
    if neighbor_json_paths is not None and (
        px in _SYNTHETIC_TOPOLOGY_SWEEPS or py in _SYNTHETIC_TOPOLOGY_SWEEPS
    ):
        raise ValueError(
            "er_p / ws_p / ws_k axes apply only to synthetic ER/WS ensembles; "
            "with neighbor_json_paths use base_panic, contagion_beta, and/or whale_frac."
        )

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

            if neighbor_json_paths is not None:
                ens = robustness_rollouts_neighbor_json_bundle(
                    genome,
                    neighbor_json_paths=neighbor_json_paths,
                    rollout_seed=int(rollout_seed),
                    contagion_beta=float(kwargs["contagion_beta"]),
                    whale_frac=float(kwargs["whale_frac"]),
                    base_panic=float(kwargs["base_panic"]),
                    max_steps=int(kwargs["max_steps"]),
                    neighbor_weights_json_paths=neighbor_weights_json_paths,
                )
            else:
                ens = robustness_rollouts_over_graph_seeds(
                    genome,
                    graph_kind=graph_kind,
                    nodes=int(nodes),
                    graph_seeds=graph_seeds,
                    rollout_seed=int(rollout_seed),
                    topology_representation=str(topology_representation),
                    er_p=float(kwargs["er_p"]),
                    ws_k=int(kwargs["ws_k"]),
                    ws_p=float(kwargs["ws_p"]),
                    base_panic=float(kwargs["base_panic"]),
                    contagion_beta=float(kwargs["contagion_beta"]),
                    whale_frac=float(kwargs["whale_frac"]),
                    max_steps=int(kwargs["max_steps"]),
                )
            s = ens["summary"]
            collapse_rates.append(float(s["collapse_rate"]))
            p50s.append(float(s["integral_instability_p50"]))
            sx = float(kwargs["ws_k"]) if px == "ws_k" else float(raw_x)
            sy = float(kwargs["ws_k"]) if py == "ws_k" else float(raw_y)
            points.append({"sweep_x": sx, "sweep_y": sy, "ensemble": ens})

    cr = np.asarray(collapse_rates, dtype=np.float64)
    p50a = np.asarray(p50s, dtype=np.float64)
    member_count = (
        len(list(neighbor_json_paths)) if neighbor_json_paths is not None else len(graph_seeds)
    )
    summary = {
        "grid_cells": len(points),
        "sweep_steps_x": len(list(sweep_values_x)),
        "sweep_steps_y": len(list(sweep_values_y)),
        "graph_seed_count": member_count,
        "collapse_rate_min": float(cr.min()) if cr.size else 0.0,
        "collapse_rate_max": float(cr.max()) if cr.size else 0.0,
        "collapse_rate_spread": float(cr.max() - cr.min()) if cr.size else 0.0,
        "integral_instability_p50_min": float(p50a.min()) if p50a.size else 0.0,
        "integral_instability_p50_max": float(p50a.max()) if p50a.size else 0.0,
    }

    out2: dict[str, Any] = {
        "schema": "fragility-robustness-sensitivity-2d-v1",
        "sweep_param_x": px,
        "sweep_param_y": py,
        "sweep_values_x": [float(x) for x in sweep_values_x],
        "sweep_values_y": [float(y) for y in sweep_values_y],
        "rollout_seed": int(rollout_seed),
        "points": points,
        "summary": summary,
    }
    if neighbor_json_paths is not None:
        out2["topology_mode"] = "neighbor_json_bundle"
        out2["neighbor_json_paths"] = [str(Path(p).as_posix()) for p in neighbor_json_paths]
        out2["graph_kind"] = None
        out2["nodes"] = None
        out2["topology_representation"] = "neighbor_lists"
    else:
        out2["topology_mode"] = "synthetic_er_ws"
        out2["neighbor_json_paths"] = None
        out2["graph_kind"] = graph_kind
        out2["nodes"] = int(nodes)
        out2["topology_representation"] = str(topology_representation)
    return out2
