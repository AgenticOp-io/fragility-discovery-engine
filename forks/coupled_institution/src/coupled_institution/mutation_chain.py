"""Cumulative coupling_strength mutation chain on a pinned shock schedule (fork)."""

from __future__ import annotations

from typing import Any

from coupled_institution.rollout import rollout_coupled
from coupled_institution.types import RolloutResult
from coupled_institution.world import CoupledInstitutionWorld

CHAIN_SPEC_SCHEMA = "coupled-institution-mutation-chain-spec-v1"
PATH_TRACE_SCHEMA = "explanation-mutation-chain-path-coupled-institution-v1"


def parse_chain_spec(obj: dict[str, Any]) -> list[dict[str, Any]]:
    sc = obj.get("schema")
    if sc is not None and sc != CHAIN_SPEC_SCHEMA:
        raise ValueError(f"unsupported chain schema {sc!r}; expected {CHAIN_SPEC_SCHEMA!r}")
    raw = obj.get("steps")
    if not isinstance(raw, list) or not raw:
        raise ValueError("chain spec must contain non-empty 'steps'")
    out: list[dict[str, Any]] = []
    for i, step in enumerate(raw):
        if not isinstance(step, dict):
            raise ValueError(f"steps[{i}] must be an object")
        kind = step.get("kind")
        if kind != "coupling_strength":
            raise ValueError(f"steps[{i}] unknown kind {kind!r}")
        out.append({"kind": kind, "value": float(step["value"])})
    return out


def _snapshot(r: RolloutResult) -> dict[str, Any]:
    return {
        "collapsed": bool(r.collapsed),
        "collapse_timestep": r.collapse_timestep,
        "peak_instability": float(r.final_instability),
        "integral_instability": float(r.integral_instability),
        "attack_cost": float(r.attack_cost),
        "mode": r.simulation_mode,
        "horizon_steps": len(r.trajectory),
        "seed": int(r.seed),
    }


def mutation_chain_path_rollouts(
    schedule: list[tuple],
    *,
    base_coupling: float,
    steps: list[dict[str, Any]],
    seed: int,
    max_steps: int = 32,
) -> list[RolloutResult]:
    if not steps:
        raise ValueError("steps must be non-empty")
    out: list[RolloutResult] = [
        rollout_coupled(
            CoupledInstitutionWorld(coupling_strength=float(base_coupling), max_steps=max_steps),
            schedule,
            seed=int(seed),
        )
    ]
    coupling = float(base_coupling)
    for step in steps:
        coupling = float(step["value"])
        out.append(
            rollout_coupled(
                CoupledInstitutionWorld(coupling_strength=coupling, max_steps=max_steps),
                schedule,
                seed=int(seed),
            )
        )
    return out


def mutation_chain_path_to_trace(
    rollouts: list[RolloutResult],
    steps: list[dict[str, Any]],
    *,
    rollout_seed: int,
    baseline_coupling: float,
    variant_coupling: float | None = None,
) -> dict[str, Any]:
    if len(rollouts) != len(steps) + 1:
        raise ValueError("expected len(rollouts) == len(steps) + 1")
    bc = float(baseline_coupling)
    vc = bc if variant_coupling is None else float(variant_coupling)

    nodes: list[dict[str, Any]] = []
    for i, r in enumerate(rollouts):
        c_used = bc if i < len(rollouts) - 1 else vc
        nodes.append(
            {
                "id": f"chain_{i}",
                "index": i,
                "mutations_applied": i,
                "reset_coupling": c_used,
                **_snapshot(r),
            }
        )

    edges: list[dict[str, Any]] = []
    for i in range(len(steps)):
        a, b = rollouts[i], rollouts[i + 1]
        c_from = bc
        c_to = bc if i < len(steps) - 1 else vc
        edges.append(
            {
                "from": f"chain_{i}",
                "to": f"chain_{i + 1}",
                "kind": "mutation_chain_step",
                "step_index": i,
                "step": dict(steps[i]),
                "delta_integral_instability": float(b.integral_instability - a.integral_instability),
                "delta_attack_cost": float(b.attack_cost - a.attack_cost),
                "reset_coupling_from": c_from,
                "reset_coupling_to": c_to,
            }
        )

    return {
        "schema": PATH_TRACE_SCHEMA,
        "source_chain_schema": CHAIN_SPEC_SCHEMA,
        "rollout_seed": int(rollout_seed),
        "baseline_coupling": bc,
        "variant_coupling": vc,
        "nodes": nodes,
        "edges": edges,
    }


def build_chain_attribution_bundle(
    rollouts: list[RolloutResult],
    steps: list[dict[str, Any]],
    *,
    rollout_seed: int,
    baseline_coupling: float,
    variant_coupling: float | None = None,
) -> dict[str, Any]:
    """Attribution-viewer shape: baseline/counterfactual snapshots + path_trace."""

    base = _snapshot(rollouts[0])
    final = _snapshot(rollouts[-1])
    vc = baseline_coupling if variant_coupling is None else float(variant_coupling)
    merged = {
        "schema": "counterfactual-bundle-v1",
        "baseline": base,
        "counterfactual": final,
        "intervention": "coupled_institution_mutation_chain",
        "mutation_steps": [dict(s) for s in steps],
        "baseline_coupling": float(baseline_coupling),
        "variant_coupling": float(vc),
        "delta_attack_cost": float(base["attack_cost"] - final["attack_cost"]),
        "delta_integral_instability": float(base["integral_instability"] - final["integral_instability"]),
        "interpretation_hint": (
            "Pinned schedule; each step raises coupling_strength on the coupled peg and overload world."
        ),
        "path_trace": mutation_chain_path_to_trace(
            rollouts,
            steps,
            rollout_seed=rollout_seed,
            baseline_coupling=baseline_coupling,
            variant_coupling=variant_coupling,
        ),
    }
    return merged
