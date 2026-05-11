"""Library narration over frozen JSON (Phase L)."""

from __future__ import annotations

from pathlib import Path

import pytest

from fragility_engine.explain.narration import load_frozen_json_artifact, narrate_frozen_artifact


def test_narrate_frozen_artifact_replay_keywords(tmp_path: Path) -> None:
    p = tmp_path / "r.json"
    p.write_text(
        '{"schema_version": "0.4.0", "simulation_mode": "aggregate", '
        '"collapsed": false, "collapse_timestep": null, '
        '"integral_instability": 1.2, "attack_cost": 3.4, "trajectory": []}',
        encoding="utf-8",
    )
    data = load_frozen_json_artifact(p)
    text = narrate_frozen_artifact(data, source=str(p))
    assert "replay rollout" in text
    assert "aggregate" in text


def test_narrate_frozen_artifact_pareto() -> None:
    text = narrate_frozen_artifact(
        {"schema": "pareto-front-v1", "best_fitness": 2.0, "archive": [{}]},
        source="inline",
    )
    assert "Pareto" in text
    assert "archive_points: 1" in text


def test_narrate_frozen_artifact_institutional_composite_v1() -> None:
    text = narrate_frozen_artifact(
        {
            "schema": "fragility-institutional-composite-v1",
            "network": {
                "integral_instability": 1.0,
                "collapsed": False,
                "attack_cost": 0.5,
                "collapse_timestep": None,
                "simulation_mode": "network",
            },
            "resource_cascade": {
                "integral_instability": 2.0,
                "collapsed": True,
                "attack_cost": 0.5,
                "collapse_timestep": 3,
                "simulation_mode": "resource_cascade",
            },
            "genome_shape": [4, 2],
        },
        source="inline",
    )
    assert "institutional composite" in text
    assert "network:" in text
    assert "resource_cascade:" in text
    assert "aggregate" not in text


def test_narrate_frozen_artifact_institutional_composite_v2() -> None:
    text = narrate_frozen_artifact(
        {
            "schema": "fragility-institutional-composite-v2",
            "aggregate": {
                "integral_instability": 0.5,
                "collapsed": False,
                "attack_cost": 0.5,
                "collapse_timestep": None,
                "simulation_mode": "aggregate",
            },
            "network": {
                "integral_instability": 1.0,
                "collapsed": False,
                "attack_cost": 0.5,
                "collapse_timestep": None,
                "simulation_mode": "network",
            },
            "resource_cascade": {
                "integral_instability": 2.0,
                "collapsed": False,
                "attack_cost": 0.5,
                "collapse_timestep": None,
                "simulation_mode": "resource_cascade",
            },
            "genome_shape": [4, 2],
        },
        source="inline",
    )
    assert "institutional composite" in text
    assert "aggregate:" in text
    assert "fragility-institutional-composite-v2" in text


def test_narrate_frozen_artifact_counterfactual_bundle() -> None:
    text = narrate_frozen_artifact(
        {
            "intervention": "remove_steps",
            "baseline": {"integral_instability": 5.0, "attack_cost": 3.0},
            "counterfactual": {"integral_instability": 2.0, "attack_cost": 3.1},
            "delta_integral_instability": 3.0,
            "delta_attack_cost": -0.1,
        },
        source="inline",
    )
    assert "counterfactual bundle" in text
    assert "remove_steps" in text


def test_load_frozen_json_artifact_bad(tmp_path: Path) -> None:
    p = tmp_path / "x.json"
    p.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="expected JSON object"):
        load_frozen_json_artifact(p)
