"""Ensemble robustness over graph seeds (moonshot)."""

from __future__ import annotations

import numpy as np
import pytest

from fragility_engine.benchmarks.ensemble import (
    robustness_ensemble_1d_param_sweep,
    robustness_rollouts_over_graph_seeds,
)


def test_robustness_ensemble_quantiles_ordering():
    genome = np.random.default_rng(9001).uniform(size=(12, 2))
    out = robustness_rollouts_over_graph_seeds(
        genome,
        graph_kind="erdos_renyi",
        nodes=14,
        graph_seeds=[101, 102, 103],
        rollout_seed=5000,
    )
    assert out["schema"] == "fragility-robustness-ensemble-v1"
    assert len(out["runs"]) == 3
    s = out["summary"]
    assert s["count"] == 3
    assert s["integral_instability_min"] <= s["integral_instability_p50"] <= s["integral_instability_max"]
    assert s["collapse_rate"] == 1.0


def test_robustness_1d_param_sweep_er_p_schema():
    genome = np.random.default_rng(9001).uniform(size=(12, 2))
    out = robustness_ensemble_1d_param_sweep(
        genome,
        sweep_param="er_p",
        sweep_values=[0.10, 0.14],
        graph_kind="erdos_renyi",
        nodes=12,
        graph_seeds=[101, 102],
        rollout_seed=5000,
    )
    assert out["schema"] == "fragility-robustness-sensitivity-1d-v1"
    assert out["sweep_param"] == "er_p"
    assert len(out["points"]) == 2
    for pt in out["points"]:
        assert "ensemble" in pt
        assert pt["ensemble"]["schema"] == "fragility-robustness-ensemble-v1"
    sp = out["summary"]
    assert "collapse_rate_spread" in sp
    assert 0.0 <= sp["collapse_rate_min"] <= sp["collapse_rate_max"] <= 1.0


def test_robustness_1d_param_sweep_invalid_param_raises():
    genome = np.random.default_rng(1).uniform(size=(4, 2))
    with pytest.raises(ValueError, match="sweep_param"):
        robustness_ensemble_1d_param_sweep(
            genome,
            sweep_param="not_a_knob",
            sweep_values=[1.0],
            graph_kind="erdos_renyi",
            nodes=10,
            graph_seeds=[1],
            rollout_seed=1,
        )
