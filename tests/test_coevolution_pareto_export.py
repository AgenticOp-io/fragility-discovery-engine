"""Merge co-evolution attacker Pareto dicts into pareto-front-v1."""

from __future__ import annotations

import pytest

from fragility_engine.coevolution.pareto_export import (
    flatten_coevolution_attacker_pareto,
    pareto_front_payload_from_archive_dicts,
)


def test_flatten_coevolution_attacker_pareto_across_rounds():
    rounds = [
        {"round": 0, "attacker_pareto": [{"severity": 1.0, "attack_cost": 0.5, "collapsed": True}]},
        {"round": 1, "attacker_pareto": [{"severity": 0.8, "attack_cost": 0.3, "collapsed": False}]},
    ]
    flat = flatten_coevolution_attacker_pareto(rounds)
    assert len(flat) == 2


def test_pareto_front_payload_schema_and_merge():
    entries = [
        {"severity": 1.0, "attack_cost": 0.5, "collapsed": True, "integral_instability": 2.0},
        {"severity": 0.5, "attack_cost": 0.8, "collapsed": False, "integral_instability": 1.0},
        {"severity": 0.4, "attack_cost": 0.9, "collapsed": False, "integral_instability": 0.5},
    ]
    payload = pareto_front_payload_from_archive_dicts(entries, source="test")
    assert payload["schema"] == "pareto-front-v1"
    assert payload["source"] == "test"
    assert isinstance(payload["archive"], list)
    assert len(payload["archive"]) >= 1
    for row in payload["archive"]:
        assert "severity" in row and "attack_cost" in row
        assert row["genome"] == []


def test_pareto_front_payload_empty_raises():
    with pytest.raises(ValueError, match="non-empty"):
        pareto_front_payload_from_archive_dicts([])
