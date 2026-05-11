"""Mechanical explanation-dag-v1 builders."""

from __future__ import annotations

from fragility_engine.explain.explanation_dag import (
    EXPLANATION_DAG_SCHEMA,
    counterfactual_bundle_to_dag,
    minimization_report_to_dag,
)
from fragility_engine.explain.narration import narrate_frozen_artifact


def test_minimization_report_collapsed_to_dag():
    report = {
        "baseline_collapsed": True,
        "minimal_events_by_timestep": {"0": [{"kind": "shock", "magnitude": 0.1}]},
        "collapsed": True,
        "collapse_timestep": 2,
    }
    dag = minimization_report_to_dag(report, source="inline")
    assert dag["schema"] == EXPLANATION_DAG_SCHEMA
    assert dag["kind"] == "schedule_minimization"
    assert len(dag["nodes"]) == 2
    assert dag["edges"][0]["kind"] == "greedy_remove_shocks_while_collapsed"


def test_minimization_report_not_collapsed():
    report = {
        "baseline_collapsed": False,
        "message": "no collapse",
    }
    dag = minimization_report_to_dag(report)
    assert len(dag["nodes"]) == 1
    assert dag["edges"] == []


def test_counterfactual_bundle_to_dag():
    bundle = {
        "intervention": "remove_steps",
        "baseline": {"integral_instability": 5.0, "attack_cost": 1.0, "collapsed": True},
        "counterfactual": {"integral_instability": 2.0, "attack_cost": 1.0, "collapsed": False},
    }
    dag = counterfactual_bundle_to_dag(bundle)
    assert dag["schema"] == EXPLANATION_DAG_SCHEMA
    assert dag["kind"] == "counterfactual_pair"
    assert dag["edges"][0]["intervention"] == "remove_steps"


def test_explanation_dag_narration():
    dag = counterfactual_bundle_to_dag(
        {
            "intervention": "x",
            "baseline": {"integral_instability": 1.0, "attack_cost": 1.0, "collapsed": False},
            "counterfactual": {"integral_instability": 2.0, "attack_cost": 1.0, "collapsed": True},
        }
    )
    text = narrate_frozen_artifact(dag, source="inline")
    assert "explanation DAG" in text
    assert "counterfactual_pair" in text
