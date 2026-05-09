"""Ensemble robustness over graph seeds (moonshot)."""

from __future__ import annotations

import numpy as np

from fragility_engine.benchmarks.ensemble import robustness_rollouts_over_graph_seeds


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
