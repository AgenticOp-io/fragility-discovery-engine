"""Regression: hypervolume on a pinned pareto-front-v1 fixture file."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fragility_engine.benchmarks.hypervolume import hypervolume_2d_min, nondominated_points_min

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "benchmarks" / "pinned_pareto_front_minimal.json"
_REF = (5.0, 5.0)
_EXPECTED_HV = 11.0


def test_pinned_pareto_fixture_hypervolume_matches_closed_form():
    raw = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    assert raw["schema"] == "pareto-front-v1"
    arch = raw["archive"]
    pts = [(float(e["severity"]), float(e["attack_cost"])) for e in arch]
    nd = nondominated_points_min(pts)
    assert set(nd) == set(pts)
    hv = hypervolume_2d_min(pts, _REF)
    assert hv == pytest.approx(_EXPECTED_HV)
