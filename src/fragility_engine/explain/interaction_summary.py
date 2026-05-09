"""Additive decomposition hints from merged attribution graphs (no causal identification claims)."""

from __future__ import annotations

from typing import Any

from fragility_engine.explain.merge_attribution import SCHEMA as ATTRIBUTION_MERGE_SCHEMA

INTERACTION_SUMMARY_SCHEMA = "attribution-interaction-summary-v1"


def summarize_attribution_merge(merge: dict[str, Any]) -> dict[str, Any]:
    """
    Summarize branch deltas from :data:`~fragility_engine.explain.merge_attribution.SCHEMA`.

    ``sum_branch_delta_*`` is the **arithmetic sum** of single-intervention deltas measured against the
    shared baseline — **not** the outcome of a joint intervention unless you export that rollout separately.
    """

    if merge.get("schema") != ATTRIBUTION_MERGE_SCHEMA:
        raise ValueError(f"expected merge schema {ATTRIBUTION_MERGE_SCHEMA!r}")
    edges = merge.get("edges")
    if not isinstance(edges, list):
        raise ValueError("merge.edges must be a list")

    branches: list[dict[str, Any]] = []
    sum_di = 0.0
    sum_dc = 0.0
    counted_di = 0
    counted_dc = 0

    for i, e in enumerate(edges):
        if not isinstance(e, dict):
            raise ValueError(f"edges[{i}] must be an object")
        di = e.get("delta_integral_instability")
        dc = e.get("delta_attack_cost")
        row = {
            "intervention": e.get("intervention"),
            "delta_integral_instability": di,
            "delta_attack_cost": dc,
        }
        if di is not None:
            sum_di += float(di)
            counted_di += 1
        if dc is not None:
            sum_dc += float(dc)
            counted_dc += 1
        branches.append(row)

    return {
        "schema": INTERACTION_SUMMARY_SCHEMA,
        "source_merge_schema": ATTRIBUTION_MERGE_SCHEMA,
        "branch_count": len(branches),
        "branches": branches,
        "sum_branch_delta_integral_instability": float(sum_di),
        "sum_branch_delta_attack_cost": float(sum_dc),
        "count_branches_with_integral_delta": counted_di,
        "count_branches_with_cost_delta": counted_dc,
        "interpretation_hint": (
            "Sum of per-branch deltas from one shared baseline; interaction / joint effects are not "
            "identified unless you also export a counterfactual that applies multiple interventions together."
        ),
    }
