"""Mechanical explanation traces (DAG-shaped JSON) from sweep artifacts."""

from __future__ import annotations

from typing import Any

from fragility_engine.explain.counterfactual import rollout_snapshot
from fragility_engine.explain.counterfactual_chain import CHAIN_SPEC_SCHEMA
from fragility_engine.explain.sweep import SCHEMA as EPSILON_SWEEP_SCHEMA
from fragility_engine.types import RolloutResult

TRACE_SCHEMA = "explanation-trace-v1"
CHAIN_PATH_TRACE_SCHEMA = "explanation-mutation-chain-path-v1"


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

    nodes: list[dict[str, Any]] = []
    for i, r in enumerate(rollouts):
        snap = rollout_snapshot(r)
        panic_used = float(baseline_base_panic) if i < len(rollouts) - 1 else float(variant_base_panic)
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
    bp = float(baseline_base_panic)
    vbp = float(variant_base_panic)
    for i in range(len(steps)):
        a = rollouts[i]
        b = rollouts[i + 1]
        di = float(b.integral_instability - a.integral_instability)
        dc = float(b.attack_cost - a.attack_cost)
        panic_from = bp
        panic_to = bp if i < len(steps) - 1 else vbp
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
        "variant_base_panic": vbp,
        "nodes": nodes,
        "edges": edges,
    }
