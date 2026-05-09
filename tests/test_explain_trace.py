"""Linear explanation traces from epsilon sweeps."""

from __future__ import annotations

import pytest

from fragility_engine.explain.sweep import SCHEMA as SWEEP_SCHEMA
from fragility_engine.explain.trace import TRACE_SCHEMA, linear_epsilon_sweep_to_trace


def test_linear_trace_requires_epsilon_sweep_schema():
    with pytest.raises(ValueError, match="schema"):
        linear_epsilon_sweep_to_trace({"schema": "wrong", "runs": [{}]})


def test_linear_trace_path_edges():
    sweep = {
        "schema": SWEEP_SCHEMA,
        "axis": "base_panic",
        "rollout_seed": 1,
        "runs": [
            {"collapsed": False, "integral_instability": 1.0, "attack_cost": 2.0},
            {"collapsed": True, "integral_instability": 3.0, "attack_cost": 2.0},
        ],
    }
    tr = linear_epsilon_sweep_to_trace(sweep)
    assert tr["schema"] == TRACE_SCHEMA
    assert len(tr["nodes"]) == 2
    assert len(tr["edges"]) == 1
    assert tr["edges"][0]["delta_integral_instability"] == 2.0
