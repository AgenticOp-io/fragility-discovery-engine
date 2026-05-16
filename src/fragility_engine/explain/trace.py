"""Mechanical explanation traces (DAG-shaped JSON) from sweep artifacts."""

from __future__ import annotations

from typing import Any

from fragility_engine.explain.counterfactual import rollout_snapshot
from fragility_engine.explain.counterfactual_chain import CHAIN_SPEC_SCHEMA, network_reset_panic_after_steps
from fragility_engine.explain.counterfactual_chain_aggregate import AGGREGATE_CHAIN_SPEC_SCHEMA
from fragility_engine.explain.counterfactual_chain_resource_cascade import RESOURCE_CASCADE_CHAIN_SPEC_SCHEMA
from fragility_engine.explain.counterfactual_chain_service_backlog import SERVICE_BACKLOG_CHAIN_SPEC_SCHEMA
from fragility_engine.explain.sweep import SCHEMA as EPSILON_SWEEP_SCHEMA
from fragility_engine.types import RolloutResult

TRACE_SCHEMA = "explanation-trace-v1"
CHAIN_PATH_TRACE_SCHEMA = "explanation-mutation-chain-path-v1"
CHAIN_PATH_TRACE_RESOURCE_CASCADE_SCHEMA = "explanation-mutation-chain-path-resource-cascade-v1"
CHAIN_PATH_TRACE_SERVICE_BACKLOG_SCHEMA = "explanation-mutation-chain-path-service-backlog-v1"
CHAIN_PATH_TRACE_AGGREGATE_SCHEMA = "explanation-mutation-chain-path-aggregate-v1"


def linear_epsilon_sweep_to_trace(sweep: dict[str, Any]) -> dict[str, Any]:
    """
    Turn a :data:`~fragility_engine.explain.sweep.SCHEMA` payload into a **linear** trace.

    Each consecutive pair of runs becomes an edge labeled with the sweep axis and scalar deltas.
    This is a deliberately minimal DAG (a path graph)—not a general causal graph.
    """

    if sweep.get("schema") != EPSILON_SWEEP_SCHEMA:
        raise ValueError(f"expected sweep schema {EPSILON_SWEEP_SCHEMA!r}")
    runs = sweep.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError("sweep must contain non-empty runs")

    axis = str(sweep.get("axis", "?"))
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    for i, row in enumerate(runs):
        if not isinstance(row, dict):
            raise ValueError(f"runs[{i}] must be a dict")
        nodes.append(
            {
                "id": f"run_{i}",
                "index": i,
                "collapsed": row.get("collapsed"),
                "integral_instability": row.get("integral_instability"),
                "attack_cost": row.get("attack_cost"),
            }
        )

    for i in range(len(runs) - 1):
        a = runs[i]
        b = runs[i + 1]
        di = float(b["integral_instability"]) - float(a["integral_instability"])
        dc = float(b["attack_cost"]) - float(a["attack_cost"])
        edges.append(
            {
                "from": f"run_{i}",
                "to": f"run_{i + 1}",
                "kind": "epsilon_sweep_step",
                "axis": axis,
                "delta_integral_instability": di,
                "delta_attack_cost": dc,
            }
        )

    return {
        "schema": TRACE_SCHEMA,
        "source_schema": EPSILON_SWEEP_SCHEMA,
        "axis": axis,
        "rollout_seed": sweep.get("rollout_seed"),
        "nodes": nodes,
        "edges": edges,
    }


def mutation_chain_path_to_trace(
    rollouts: list[RolloutResult],
    steps: list[dict[str, Any]],
    *,
    rollout_seed: int,
    baseline_base_panic: float,
    variant_base_panic: float,
) -> dict[str, Any]:
    """
    Linear path graph over :func:`~fragility_engine.explain.counterfactual_chain.mutation_chain_path_rollouts` outputs.

    Each edge records the mutation step (except the edge incident on the root) and reset-panic used
    on the **target** node's rollout; the final edge may pair the last mutation with a panic jump
    when ``variant_base_panic != baseline_base_panic``.
    """

    if len(rollouts) != len(steps) + 1:
        raise ValueError("expected len(rollouts) == len(steps) + 1")
    if not steps:
        raise ValueError("steps must be non-empty")

    bp = float(baseline_base_panic)
    vbp_opt = float(variant_base_panic)
    nodes: list[dict[str, Any]] = []
    for i, r in enumerate(rollouts):
        snap = rollout_snapshot(r)
        panic_used = network_reset_panic_after_steps(
            steps,
            i,
            bp,
            variant_base_panic=vbp_opt if i == len(rollouts) - 1 else None,
        )
        nodes.append(
            {
                "id": f"chain_{i}",
                "index": i,
                "mutations_applied": i,
                "reset_panic": panic_used,
                **snap,
            }
        )

    edges: list[dict[str, Any]] = []
    vbp_final = network_reset_panic_after_steps(steps, len(steps), bp, variant_base_panic=vbp_opt)
    for i in range(len(steps)):
        a = rollouts[i]
        b = rollouts[i + 1]
        di = float(b.integral_instability - a.integral_instability)
        dc = float(b.attack_cost - a.attack_cost)
        panic_from = network_reset_panic_after_steps(steps, i, bp)
        panic_to = network_reset_panic_after_steps(
            steps,
            i + 1,
            bp,
            variant_base_panic=vbp_opt if i + 1 == len(steps) else None,
        )
        edges.append(
            {
                "from": f"chain_{i}",
                "to": f"chain_{i + 1}",
                "kind": "mutation_chain_step",
                "step_index": i,
                "step": dict(steps[i]),
                "delta_integral_instability": di,
                "delta_attack_cost": dc,
                "reset_panic_from": panic_from,
                "reset_panic_to": panic_to,
            }
        )

    return {
        "schema": CHAIN_PATH_TRACE_SCHEMA,
        "source_chain_schema": CHAIN_SPEC_SCHEMA,
        "rollout_seed": int(rollout_seed),
        "baseline_base_panic": bp,
        "variant_base_panic": vbp_final,
        "nodes": nodes,
        "edges": edges,
    }


def mutation_chain_path_to_trace_resource_cascade(
    rollouts: list[RolloutResult],
    steps: list[dict[str, Any]],
    *,
    rollout_seed: int,
    baseline_initial_overload: float,
    variant_initial_overload: float,
) -> dict[str, Any]:
    """
    Path trace for resource-cascade cumulative mutation prefixes.

    Consumes the rollout list from ``mutation_chain_path_rollouts_resource_cascade``. Mirrors
    :func:`mutation_chain_path_to_trace` but labels reset **initial overload** instead of base panic.
    """

    if len(rollouts) != len(steps) + 1:
        raise ValueError("expected len(rollouts) == len(steps) + 1")
    if not steps:
        raise ValueError("steps must be non-empty")

    bio = float(baseline_initial_overload)
    vio = float(variant_initial_overload)

    nodes: list[dict[str, Any]] = []
    for i, r in enumerate(rollouts):
        snap = rollout_snapshot(r)
        overload_used = bio if i < len(rollouts) - 1 else vio
        nodes.append(
            {
                "id": f"chain_{i}",
                "index": i,
                "mutations_applied": i,
                "reset_initial_overload": overload_used,
                **snap,
            }
        )

    edges: list[dict[str, Any]] = []
    for i in range(len(steps)):
        a = rollouts[i]
        b = rollouts[i + 1]
        di = float(b.integral_instability - a.integral_instability)
        dc = float(b.attack_cost - a.attack_cost)
        overload_from = bio
        overload_to = bio if i < len(steps) - 1 else vio
        edges.append(
            {
                "from": f"chain_{i}",
                "to": f"chain_{i + 1}",
                "kind": "mutation_chain_step",
                "step_index": i,
                "step": dict(steps[i]),
                "delta_integral_instability": di,
                "delta_attack_cost": dc,
                "reset_initial_overload_from": overload_from,
                "reset_initial_overload_to": overload_to,
            }
        )

    return {
        "schema": CHAIN_PATH_TRACE_RESOURCE_CASCADE_SCHEMA,
        "source_chain_schema": RESOURCE_CASCADE_CHAIN_SPEC_SCHEMA,
        "rollout_seed": int(rollout_seed),
        "baseline_initial_overload": bio,
        "variant_initial_overload": vio,
        "nodes": nodes,
        "edges": edges,
    }


def mutation_chain_path_to_trace_service_backlog(
    rollouts: list[RolloutResult],
    steps: list[dict[str, Any]],
    *,
    rollout_seed: int,
    baseline_initial_backlog: float,
    variant_initial_backlog: float,
) -> dict[str, Any]:
    """
    Path trace for service-backlog cumulative mutation prefixes.

    Consumes the rollout list from ``mutation_chain_path_rollouts_service_backlog``.
    """

    if len(rollouts) != len(steps) + 1:
        raise ValueError("expected len(rollouts) == len(steps) + 1")
    if not steps:
        raise ValueError("steps must be non-empty")

    bib = float(baseline_initial_backlog)
    vib = float(variant_initial_backlog)

    nodes: list[dict[str, Any]] = []
    for i, r in enumerate(rollouts):
        snap = rollout_snapshot(r)
        backlog_used = bib if i < len(rollouts) - 1 else vib
        nodes.append(
            {
                "id": f"chain_{i}",
                "index": i,
                "mutations_applied": i,
                "reset_initial_backlog": backlog_used,
                **snap,
            }
        )

    edges: list[dict[str, Any]] = []
    for i in range(len(steps)):
        a = rollouts[i]
        b = rollouts[i + 1]
        di = float(b.integral_instability - a.integral_instability)
        dc = float(b.attack_cost - a.attack_cost)
        backlog_from = bib
        backlog_to = bib if i < len(steps) - 1 else vib
        edges.append(
            {
                "from": f"chain_{i}",
                "to": f"chain_{i + 1}",
                "kind": "mutation_chain_step",
                "step_index": i,
                "step": dict(steps[i]),
                "delta_integral_instability": di,
                "delta_attack_cost": dc,
                "reset_initial_backlog_from": backlog_from,
                "reset_initial_backlog_to": backlog_to,
            }
        )

    return {
        "schema": CHAIN_PATH_TRACE_SERVICE_BACKLOG_SCHEMA,
        "source_chain_schema": SERVICE_BACKLOG_CHAIN_SPEC_SCHEMA,
        "rollout_seed": int(rollout_seed),
        "baseline_initial_backlog": bib,
        "variant_initial_backlog": vib,
        "nodes": nodes,
        "edges": edges,
    }


def mutation_chain_path_to_trace_aggregate(
    rollouts: list[RolloutResult],
    steps: list[dict[str, Any]],
    *,
    rollout_seed: int,
    baseline_initial_panic: float,
    variant_initial_panic: float,
) -> dict[str, Any]:
    """Path trace for aggregate peg cumulative mutation prefixes."""

    if len(rollouts) != len(steps) + 1:
        raise ValueError("expected len(rollouts) == len(steps) + 1")
    if not steps:
        raise ValueError("steps must be non-empty")

    bip = float(baseline_initial_panic)
    vip = float(variant_initial_panic)

    nodes: list[dict[str, Any]] = []
    for i, r in enumerate(rollouts):
        snap = rollout_snapshot(r)
        panic_used = bip if i < len(rollouts) - 1 else vip
        nodes.append(
            {
                "id": f"chain_{i}",
                "index": i,
                "mutations_applied": i,
                "reset_initial_panic": panic_used,
                **snap,
            }
        )

    edges: list[dict[str, Any]] = []
    for i in range(len(steps)):
        a = rollouts[i]
        b = rollouts[i + 1]
        di = float(b.integral_instability - a.integral_instability)
        dc = float(b.attack_cost - a.attack_cost)
        panic_from = bip
        panic_to = bip if i < len(steps) - 1 else vip
        edges.append(
            {
                "from": f"chain_{i}",
                "to": f"chain_{i + 1}",
                "kind": "mutation_chain_step",
                "step_index": i,
                "step": dict(steps[i]),
                "delta_integral_instability": di,
                "delta_attack_cost": dc,
                "reset_initial_panic_from": panic_from,
                "reset_initial_panic_to": panic_to,
            }
        )

    return {
        "schema": CHAIN_PATH_TRACE_AGGREGATE_SCHEMA,
        "source_chain_schema": AGGREGATE_CHAIN_SPEC_SCHEMA,
        "rollout_seed": int(rollout_seed),
        "baseline_initial_panic": bip,
        "variant_initial_panic": vip,
        "nodes": nodes,
        "edges": edges,
    }
