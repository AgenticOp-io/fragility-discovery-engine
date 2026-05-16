"""Deterministic ε-style sweeps over scalar network physics (Phase I backlog)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal

import numpy as np

from fragility_engine.coevolution.defender import (
    clone_liquidity_ladder,
    clone_service_backlog,
    clone_stablecoin_network,
)
from fragility_engine.explain.counterfactual import neighbor_lists_explicit_weights, out_edge_index, rollout_snapshot
from fragility_engine.runner import (
    rollout_liquidity_ladder,
    rollout_resource_cascade,
    rollout_service_backlog,
    rollout_stablecoin,
    rollout_stablecoin_network,
)
from fragility_engine.world.liquidity_ladder import LiquidityLadderWorld
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.service_backlog import ServiceBacklogWorld
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld

SweepAxis = Literal["base_panic", "contagion_beta"]

SCHEMA = "counterfactual-epsilon-sweep-v1"


def sweep_network_scalar_axis(
    genome: np.ndarray,
    template: StablecoinNetworkWorld,
    *,
    axis: SweepAxis,
    values: list[float],
    rollout_seed: int,
    fixed_base_panic: float | None = None,
    continue_after_collapse: bool = False,
) -> dict[str, Any]:
    """
    Same genome and rollout seed; vary one scalar axis holding topology fixed.

    For ``contagion_beta``, ``fixed_base_panic`` must be set (panic at reset).
    For ``base_panic``, ``fixed_base_panic`` is ignored.
    """

    if not values:
        raise ValueError("values must be non-empty")

    runs: list[dict[str, Any]] = []
    integrals: list[float] = []

    if axis == "base_panic":
        for v in values:
            bp = float(v)
            r = rollout_stablecoin_network(
                template,
                genome,
                seed=int(rollout_seed),
                base_panic=bp,
                continue_after_collapse=bool(continue_after_collapse),
            )
            integrals.append(float(r.integral_instability))
            row = {"base_panic": bp, **rollout_snapshot(r)}
            runs.append(row)
    else:
        if fixed_base_panic is None:
            raise ValueError("fixed_base_panic required for contagion_beta sweep")
        bp = float(fixed_base_panic)
        for v in values:
            b = float(v)
            tw = clone_stablecoin_network(template, contagion_beta=b)
            r = rollout_stablecoin_network(
                tw,
                genome,
                seed=int(rollout_seed),
                base_panic=bp,
                continue_after_collapse=bool(continue_after_collapse),
            )
            integrals.append(float(r.integral_instability))
            row = {"contagion_beta": b, **rollout_snapshot(r)}
            runs.append(row)

    arr = np.asarray(integrals, dtype=np.float64)
    collapses = sum(1 for row in runs if row["collapsed"])

    summary = {
        "count": len(values),
        "collapse_count": int(collapses),
        "integral_instability_min": float(arr.min()),
        "integral_instability_max": float(arr.max()),
        "integral_instability_mean": float(arr.mean()),
    }

    return {
        "schema": SCHEMA,
        "axis": axis,
        "mode": "network",
        "rollout_seed": int(rollout_seed),
        "runs": runs,
        "summary": summary,
    }


def sweep_network_edge_weight(
    genome: np.ndarray,
    template: StablecoinNetworkWorld,
    *,
    edge_from: int,
    edge_to: int,
    values: list[float],
    rollout_seed: int,
    fixed_base_panic: float,
    continue_after_collapse: bool = False,
) -> dict[str, Any]:
    """
    List-only topology: vary the weight on a single directed out-edge (``edge_from`` → ``edge_to``).

    Unweighted templates use implicit **1.0** per edge for the baseline row shape.
    """

    if template.adjacency is not None:
        raise ValueError("edge_weight sweep requires neighbor_lists topology (not dense adjacency)")
    if not values:
        raise ValueError("values must be non-empty")

    nl = template._neighbor_lists
    k = out_edge_index(nl, int(edge_from), int(edge_to))
    base_w = neighbor_lists_explicit_weights(template)
    bp = float(fixed_base_panic)

    runs: list[dict[str, Any]] = []
    integrals: list[float] = []

    for v in values:
        ew = float(v)
        if ew <= 0.0:
            raise ValueError("edge weights must be positive")
        wvar = deepcopy(base_w)
        wvar[int(edge_from)][k] = ew
        tw = clone_stablecoin_network(template, neighbor_weights=wvar)
        r = rollout_stablecoin_network(
            tw,
            genome,
            seed=int(rollout_seed),
            base_panic=bp,
            continue_after_collapse=bool(continue_after_collapse),
        )
        integrals.append(float(r.integral_instability))
        runs.append(
            {
                "edge_from": int(edge_from),
                "edge_to": int(edge_to),
                "edge_weight": ew,
                **rollout_snapshot(r),
            }
        )

    arr = np.asarray(integrals, dtype=np.float64)
    collapses = sum(1 for row in runs if row["collapsed"])

    summary = {
        "count": len(values),
        "collapse_count": int(collapses),
        "integral_instability_min": float(arr.min()),
        "integral_instability_max": float(arr.max()),
        "integral_instability_mean": float(arr.mean()),
    }

    return {
        "schema": SCHEMA,
        "axis": "edge_weight",
        "mode": "network",
        "edge_from": int(edge_from),
        "edge_to": int(edge_to),
        "rollout_seed": int(rollout_seed),
        "fixed_base_panic": bp,
        "runs": runs,
        "summary": summary,
    }


def sweep_aggregate_initial_panic(
    genome: np.ndarray,
    template: StablecoinPegWorld,
    *,
    values: list[float],
    rollout_seed: int,
    continue_after_collapse: bool = False,
) -> dict[str, Any]:
    """Aggregate peg world: vary ``initial_panic`` at reset; same genome and rollout seed."""

    if not values:
        raise ValueError("values must be non-empty")

    runs: list[dict[str, Any]] = []
    integrals: list[float] = []

    for v in values:
        ip = float(v)
        r = rollout_stablecoin(
            template,
            genome,
            seed=int(rollout_seed),
            initial_panic=ip,
            continue_after_collapse=bool(continue_after_collapse),
        )
        integrals.append(float(r.integral_instability))
        runs.append({"initial_panic": ip, **rollout_snapshot(r)})

    arr = np.asarray(integrals, dtype=np.float64)
    collapses = sum(1 for row in runs if row["collapsed"])

    summary = {
        "count": len(values),
        "collapse_count": int(collapses),
        "integral_instability_min": float(arr.min()),
        "integral_instability_max": float(arr.max()),
        "integral_instability_mean": float(arr.mean()),
    }

    return {
        "schema": SCHEMA,
        "axis": "initial_panic",
        "mode": "aggregate",
        "rollout_seed": int(rollout_seed),
        "runs": runs,
        "summary": summary,
    }


def sweep_resource_cascade_initial_overload(
    genome: np.ndarray,
    template: ResourceCascadeWorld,
    *,
    values: list[float],
    rollout_seed: int,
    continue_after_collapse: bool = False,
) -> dict[str, Any]:
    """Phase J: vary ``initial_overload`` at reset; same genome and rollout seed."""

    if not values:
        raise ValueError("values must be non-empty")

    runs: list[dict[str, Any]] = []
    integrals: list[float] = []

    for v in values:
        io = float(np.clip(v, 0.0, 1.0))
        r = rollout_resource_cascade(
            template,
            genome,
            seed=int(rollout_seed),
            initial_overload=io,
            continue_after_collapse=bool(continue_after_collapse),
        )
        integrals.append(float(r.integral_instability))
        runs.append({"initial_overload": io, **rollout_snapshot(r)})

    arr = np.asarray(integrals, dtype=np.float64)
    collapses = sum(1 for row in runs if row["collapsed"])

    summary = {
        "count": len(values),
        "collapse_count": int(collapses),
        "integral_instability_min": float(arr.min()),
        "integral_instability_max": float(arr.max()),
        "integral_instability_mean": float(arr.mean()),
    }

    return {
        "schema": SCHEMA,
        "axis": "initial_overload",
        "mode": "resource_cascade",
        "rollout_seed": int(rollout_seed),
        "runs": runs,
        "summary": summary,
    }


def sweep_service_backlog_initial_backlog(
    genome: np.ndarray,
    template: ServiceBacklogWorld,
    *,
    values: list[float],
    rollout_seed: int,
    continue_after_collapse: bool = False,
) -> dict[str, Any]:
    """Phase M: vary ``initial_backlog`` at reset; same genome and rollout seed."""

    if not values:
        raise ValueError("values must be non-empty")

    runs: list[dict[str, Any]] = []
    integrals: list[float] = []

    for v in values:
        ib = float(max(0.0, float(v)))
        r = rollout_service_backlog(
            template,
            genome,
            seed=int(rollout_seed),
            initial_backlog=ib,
            continue_after_collapse=bool(continue_after_collapse),
        )
        integrals.append(float(r.integral_instability))
        runs.append({"initial_backlog": ib, **rollout_snapshot(r)})

    arr = np.asarray(integrals, dtype=np.float64)
    collapses = sum(1 for row in runs if row["collapsed"])

    summary = {
        "count": len(values),
        "collapse_count": int(collapses),
        "integral_instability_min": float(arr.min()),
        "integral_instability_max": float(arr.max()),
        "integral_instability_mean": float(arr.mean()),
    }

    return {
        "schema": SCHEMA,
        "axis": "initial_backlog",
        "mode": "service_backlog",
        "rollout_seed": int(rollout_seed),
        "runs": runs,
        "summary": summary,
    }


def sweep_service_backlog_process_rate(
    genome: np.ndarray,
    template: ServiceBacklogWorld,
    *,
    values: list[float],
    rollout_seed: int,
    initial_backlog: float,
    continue_after_collapse: bool = False,
) -> dict[str, Any]:
    """Phase M: vary ``process_rate`` via topology-preserving clone; same genome, seed, backlog."""

    if not values:
        raise ValueError("values must be non-empty")

    runs: list[dict[str, Any]] = []
    integrals: list[float] = []

    for v in values:
        pr = float(max(0.0, float(v)))
        tw = clone_service_backlog(template, process_rate=pr)
        r = rollout_service_backlog(
            tw,
            genome,
            seed=int(rollout_seed),
            initial_backlog=float(initial_backlog),
            continue_after_collapse=bool(continue_after_collapse),
        )
        integrals.append(float(r.integral_instability))
        runs.append({"process_rate": pr, **rollout_snapshot(r)})

    arr = np.asarray(integrals, dtype=np.float64)
    collapses = sum(1 for row in runs if row["collapsed"])

    summary = {
        "count": len(values),
        "collapse_count": int(collapses),
        "integral_instability_min": float(arr.min()),
        "integral_instability_max": float(arr.max()),
        "integral_instability_mean": float(arr.mean()),
    }

    return {
        "schema": SCHEMA,
        "axis": "process_rate",
        "mode": "service_backlog",
        "rollout_seed": int(rollout_seed),
        "fixed_initial_backlog": float(initial_backlog),
        "runs": runs,
        "summary": summary,
    }


def sweep_liquidity_ladder_initial_margin(
    genome: np.ndarray,
    template: LiquidityLadderWorld,
    *,
    values: list[float],
    rollout_seed: int,
    continue_after_collapse: bool = False,
) -> dict[str, Any]:
    """Phase N: vary ``initial_margin`` at reset; same genome and rollout seed."""

    if not values:
        raise ValueError("values must be non-empty")

    runs: list[dict[str, Any]] = []
    integrals: list[float] = []

    for v in values:
        im = float(max(0.0, float(v)))
        r = rollout_liquidity_ladder(
            template,
            genome,
            seed=int(rollout_seed),
            initial_margin=im,
            continue_after_collapse=bool(continue_after_collapse),
        )
        integrals.append(float(r.integral_instability))
        runs.append({"initial_margin": im, **rollout_snapshot(r)})

    arr = np.asarray(integrals, dtype=np.float64)
    collapses = sum(1 for row in runs if row["collapsed"])

    summary = {
        "count": len(values),
        "collapse_count": int(collapses),
        "integral_instability_min": float(arr.min()),
        "integral_instability_max": float(arr.max()),
        "integral_instability_mean": float(arr.mean()),
    }

    return {
        "schema": SCHEMA,
        "axis": "initial_margin",
        "mode": "liquidity_ladder",
        "rollout_seed": int(rollout_seed),
        "runs": runs,
        "summary": summary,
    }


def sweep_liquidity_ladder_delever_rate(
    genome: np.ndarray,
    template: LiquidityLadderWorld,
    *,
    values: list[float],
    rollout_seed: int,
    initial_margin: float,
    continue_after_collapse: bool = False,
) -> dict[str, Any]:
    """Phase N: vary ``delever_rate`` via template clone; same genome, seed, margin."""

    if not values:
        raise ValueError("values must be non-empty")

    runs: list[dict[str, Any]] = []
    integrals: list[float] = []

    for v in values:
        dr = float(max(0.0, float(v)))
        tw = clone_liquidity_ladder(template, delever_rate=dr)
        r = rollout_liquidity_ladder(
            tw,
            genome,
            seed=int(rollout_seed),
            initial_margin=float(initial_margin),
            continue_after_collapse=bool(continue_after_collapse),
        )
        integrals.append(float(r.integral_instability))
        runs.append({"delever_rate": dr, **rollout_snapshot(r)})

    arr = np.asarray(integrals, dtype=np.float64)
    collapses = sum(1 for row in runs if row["collapsed"])

    summary = {
        "count": len(values),
        "collapse_count": int(collapses),
        "integral_instability_min": float(arr.min()),
        "integral_instability_max": float(arr.max()),
        "integral_instability_mean": float(arr.mean()),
    }

    return {
        "schema": SCHEMA,
        "axis": "delever_rate",
        "mode": "liquidity_ladder",
        "rollout_seed": int(rollout_seed),
        "fixed_initial_margin": float(initial_margin),
        "runs": runs,
        "summary": summary,
    }
