"""Merge multiple counterfactual bundles that share one baseline into one attribution graph JSON."""

from __future__ import annotations

from typing import Any, Sequence

SCHEMA = "attribution-merge-v1"

_BASELINE_KEYS_FROZEN = frozenset({"collapsed", "integral_instability", "attack_cost", "seed", "mode"})


def merge_heterogeneous_counterfactuals(
    bundles: Sequence[dict[str, Any]],
    *,
    strict_baseline: bool = True,
) -> dict[str, Any]:
    """
    Star-shaped merge: one **baseline** snapshot (root) and several **counterfactual** branches.

    Each bundle should match :func:`~fragility_engine.explain.counterfactual.compare_rollouts` export shape
    (``baseline`` / ``counterfactual`` rollout snapshots) plus optional keys such as ``intervention`` or
    ``removed_timesteps``. When ``strict_baseline`` is True, baseline snapshots must agree on
    ``{_BASELINE_KEYS_FROZEN}`` across bundles.
    """

    if not bundles:
        raise ValueError("bundles must be non-empty")
    root = bundles[0]
    b0 = root.get("baseline")
    if not isinstance(b0, dict):
        raise ValueError("each bundle must contain a dict 'baseline'")

    branches: list[dict[str, Any]] = []

    for i, bundle in enumerate(bundles):
        if not isinstance(bundle, dict):
            raise ValueError(f"bundles[{i}] must be a dict")
        bs = bundle.get("baseline")
        cf = bundle.get("counterfactual")
        if not isinstance(bs, dict) or not isinstance(cf, dict):
            raise ValueError(f"bundles[{i}] must have dict baseline and counterfactual")
        if strict_baseline:
            for key in _BASELINE_KEYS_FROZEN:
                if bs.get(key) != b0.get(key):
                    raise ValueError(
                        f"bundles[{i}].baseline[{key!r}] != bundles[0].baseline[{key!r}] under strict_baseline"
                    )

        iv = bundle.get("intervention")
        if iv is None and bundle.get("removed_timesteps") is not None:
            iv = "remove_steps"
        elif iv is None:
            iv = "unknown"

        edge: dict[str, Any] = {
            "from": "baseline",
            "to": f"branch_{i}",
            "intervention": iv,
            "delta_integral_instability": bundle.get("delta_integral_instability"),
            "delta_attack_cost": bundle.get("delta_attack_cost"),
        }
        for optional in (
            "removed_timesteps",
            "baseline_base_panic",
            "variant_base_panic",
            "baseline_beta",
            "variant_beta",
            "edge_from",
            "edge_to",
            "baseline_edge_weight",
            "variant_edge_weight",
            "mutation_steps",
            "edges_patch",
            "baseline_initial_overload",
            "variant_initial_overload",
            "baseline_cascade_coupling",
            "variant_cascade_coupling",
        ):
            if optional in bundle:
                edge[optional] = bundle[optional]

        branches.append(
            {
                "node_id": f"branch_{i}",
                "bundle_index": i,
                "intervention": iv,
                "counterfactual": cf,
                "edge": edge,
            }
        )

    nodes: list[dict[str, Any]] = [{"id": "baseline", "kind": "root", "rollout": b0}]
    nodes.extend(
        {
            "id": b["node_id"],
            "kind": "counterfactual",
            "bundle_index": b["bundle_index"],
            "intervention": b["intervention"],
            "rollout": b["counterfactual"],
        }
        for b in branches
    )
    edges = [b["edge"] for b in branches]

    return {
        "schema": SCHEMA,
        "strict_baseline": bool(strict_baseline),
        "branch_count": len(branches),
        "nodes": nodes,
        "edges": edges,
    }
