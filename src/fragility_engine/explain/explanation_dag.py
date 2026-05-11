"""Mechanical explanation DAG over minimization reports and counterfactual bundles (Phase I optional)."""

from __future__ import annotations

from typing import Any

EXPLANATION_DAG_SCHEMA = "explanation-dag-v1"


def minimization_report_to_dag(report: dict[str, Any], *, source: str = "") -> dict[str, Any]:
    """
    Build a tiny DAG from :func:`~fragility_engine.explain.minimal_collapse.minimize_schedule_with_rollout`
    JSON-able report (``baseline_collapsed``, ``minimal_events_by_timestep``, …).
    """

    if not isinstance(report, dict):
        raise TypeError("report must be a dict")
    collapsed = bool(report.get("baseline_collapsed"))
    nodes: list[dict[str, Any]] = [
        {
            "id": "baseline",
            "label": "baseline_schedule",
            "collapsed": collapsed,
        }
    ]
    edges: list[dict[str, Any]] = []
    if collapsed:
        kept = report.get("minimal_events_by_timestep") or {}
        n_kept = len(kept) if isinstance(kept, dict) else 0
        nodes.append(
            {
                "id": "minimized",
                "label": "after_greedy_event_removal",
                "minimal_event_timesteps": sorted(int(k) for k in kept.keys()) if isinstance(kept, dict) else [],
                "collapsed": bool(report.get("collapsed")),
                "collapse_timestep": report.get("collapse_timestep"),
            }
        )
        edges.append(
            {
                "from": "baseline",
                "to": "minimized",
                "kind": "greedy_remove_shocks_while_collapsed",
                "meta": {"minimal_timestep_count": n_kept},
            }
        )
    else:
        nodes[0]["message"] = report.get("message") or "minimization undefined"

    out: dict[str, Any] = {
        "schema": EXPLANATION_DAG_SCHEMA,
        "kind": "schedule_minimization",
        "nodes": nodes,
        "edges": edges,
    }
    if source:
        out["source"] = source
    return out


def counterfactual_bundle_to_dag(bundle: dict[str, Any], *, source: str = "") -> dict[str, Any]:
    """Single-intervention edge between baseline and counterfactual rollout snapshots."""

    bs = bundle.get("baseline")
    cf = bundle.get("counterfactual")
    if not isinstance(bs, dict) or not isinstance(cf, dict):
        raise ValueError("bundle must contain baseline and counterfactual dicts")
    intervention = bundle.get("intervention", "unknown")
    nodes = [
        {
            "id": "baseline",
            "label": "baseline_rollout",
            "integral_instability": bs.get("integral_instability"),
            "attack_cost": bs.get("attack_cost"),
            "collapsed": bs.get("collapsed"),
        },
        {
            "id": "counterfactual",
            "label": "counterfactual_rollout",
            "integral_instability": cf.get("integral_instability"),
            "attack_cost": cf.get("attack_cost"),
            "collapsed": cf.get("collapsed"),
        },
    ]
    edges = [
        {
            "from": "baseline",
            "to": "counterfactual",
            "kind": "counterfactual_intervention",
            "intervention": intervention,
        }
    ]
    out: dict[str, Any] = {
        "schema": EXPLANATION_DAG_SCHEMA,
        "kind": "counterfactual_pair",
        "nodes": nodes,
        "edges": edges,
    }
    if source:
        out["source"] = source
    return out
