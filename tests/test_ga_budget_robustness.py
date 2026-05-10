"""GA generation budget vs ensemble dispersion (moonshot follow-on)."""

from __future__ import annotations

from fragility_engine.benchmarks.ensemble import robustness_ga_generations_1d_sweep


def test_robustness_ga_generations_sweep_schema():
    out = robustness_ga_generations_1d_sweep(
        ga_generations_values=[1, 2],
        population_size=8,
        ga_seed=41414,
        horizon=8,
        rollout_seed=51515,
        graph_kind="erdos_renyi",
        nodes=10,
        graph_seeds=[201, 202],
        train_graph_seed=201,
        er_p=0.14,
        max_steps=18,
    )
    assert out["schema"] == "fragility-robustness-ga-budget-1d-v1"
    assert len(out["points"]) == 2
    assert out["points"][0]["ensemble"]["schema"] == "fragility-robustness-ensemble-v1"
    assert out["summary"]["steps"] == 2
