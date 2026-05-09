"""Merged attribution graph from heterogeneous counterfactual bundles."""

from __future__ import annotations

import pytest

from fragility_engine.explain.merge_attribution import SCHEMA, merge_heterogeneous_counterfactuals


def _snap(collapsed: bool, ii: float, cost: float, seed: int = 1):
    return {
        "collapsed": collapsed,
        "integral_instability": ii,
        "attack_cost": cost,
        "seed": seed,
        "mode": "network",
    }


def test_merge_star_graph():
    b0 = _snap(False, 1.0, 2.0)
    bundles = [
        {
            "baseline": b0,
            "counterfactual": _snap(True, 3.0, 2.0),
            "intervention": "network_base_panic_shift",
            "delta_integral_instability": -1.0,
            "delta_attack_cost": 0.0,
        },
        {
            "baseline": b0,
            "counterfactual": _snap(False, 0.5, 1.0),
            "intervention": "network_contagion_beta_shift",
            "delta_integral_instability": 0.5,
            "delta_attack_cost": 1.0,
        },
    ]
    m = merge_heterogeneous_counterfactuals(bundles)
    assert m["schema"] == SCHEMA
    assert m["branch_count"] == 2
    assert len(m["nodes"]) == 3
    assert len(m["edges"]) == 2
    assert m["edges"][0]["intervention"] == "network_base_panic_shift"
    assert m["edges"][1]["intervention"] == "network_contagion_beta_shift"


def test_merge_strict_baseline_rejects_mismatch():
    bundles = [
        {"baseline": _snap(False, 1.0, 2.0), "counterfactual": _snap(True, 2.0, 2.0)},
        {"baseline": _snap(False, 1.1, 2.0), "counterfactual": _snap(False, 1.0, 2.0)},
    ]
    with pytest.raises(ValueError, match="strict_baseline"):
        merge_heterogeneous_counterfactuals(bundles, strict_baseline=True)


def test_merge_carries_edges_patch():
    b0 = _snap(False, 1.0, 2.0)
    patch = [{"from": 0, "to": 1, "weight": 2.0}]
    m = merge_heterogeneous_counterfactuals(
        [
            {
                "baseline": b0,
                "counterfactual": _snap(False, 1.2, 2.0),
                "intervention": "network_neighbor_edges_weight_patch",
                "edges_patch": patch,
                "delta_integral_instability": -0.2,
            },
        ]
    )
    assert m["edges"][0]["edges_patch"] == patch


def test_merge_carries_mutation_steps_from_chain_bundle():
    b0 = _snap(False, 1.0, 2.0)
    steps = [{"kind": "contagion_beta", "value": 0.1}]
    m = merge_heterogeneous_counterfactuals(
        [
            {
                "baseline": b0,
                "counterfactual": _snap(True, 4.0, 2.0),
                "intervention": "network_mutation_chain",
                "mutation_steps": steps,
                "delta_integral_instability": -3.0,
            },
        ]
    )
    assert m["edges"][0]["mutation_steps"] == steps


def test_merge_remove_steps_infers_intervention():
    b0 = _snap(False, 1.0, 2.0)
    m = merge_heterogeneous_counterfactuals(
        [
            {
                "baseline": b0,
                "counterfactual": _snap(False, 0.8, 2.0),
                "removed_timesteps": [0, 2],
            },
        ]
    )
    assert m["edges"][0]["intervention"] == "remove_steps"
    assert m["edges"][0]["removed_timesteps"] == [0, 2]
