"""GA generation budget vs ensemble dispersion (moonshot follow-on)."""

from __future__ import annotations

import json
from pathlib import Path

from fragility_engine.benchmarks.ensemble import (
    robustness_ga_budget_2d_grid,
    robustness_ga_generations_1d_sweep,
    robustness_ga_population_1d_sweep,
)


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


def test_robustness_ga_population_1d_sweep_schema():
    out = robustness_ga_population_1d_sweep(
        ga_population_sizes=[8, 10],
        ga_generations_fixed=2,
        ga_seed=91919,
        horizon=8,
        rollout_seed=82828,
        graph_kind="erdos_renyi",
        nodes=10,
        graph_seeds=[301, 302],
        train_graph_seed=301,
        er_p=0.14,
        max_steps=18,
    )
    assert out["schema"] == "fragility-robustness-ga-population-1d-v1"
    assert len(out["points"]) == 2
    assert out["ga_generations_fixed"] == 2


def test_robustness_ga_budget_2d_grid_schema():
    out = robustness_ga_budget_2d_grid(
        ga_generations_values=[1, 2],
        ga_population_sizes=[8, 10],
        ga_seed=61616,
        horizon=8,
        rollout_seed=71717,
        graph_kind="erdos_renyi",
        nodes=10,
        graph_seeds=[203, 204],
        train_graph_seed=203,
        er_p=0.14,
        max_steps=18,
    )
    assert out["schema"] == "fragility-robustness-ga-budget-2d-v1"
    assert len(out["points"]) == 4
    assert out["summary"]["grid_cells"] == 4
    assert out["points"][0]["population_size"] == 8


def test_robustness_ga_population_1d_neighbor_json_bundle(tmp_path: Path):
    p0 = tmp_path / "c2.json"
    p1 = tmp_path / "c3.json"
    p0.write_text(json.dumps([[1], [0]]), encoding="utf-8")
    p1.write_text(json.dumps([[1], [2], [0]]), encoding="utf-8")
    out = robustness_ga_population_1d_sweep(
        ga_population_sizes=[8, 10],
        ga_generations_fixed=2,
        ga_seed=424242,
        horizon=8,
        rollout_seed=535353,
        graph_kind="erdos_renyi",
        nodes=10,
        neighbor_json_paths=[p0, p1],
        er_p=0.14,
        max_steps=18,
    )
    assert out["schema"] == "fragility-robustness-ga-population-1d-v1"
    assert len(out["points"]) == 2
    assert out["points"][0]["ensemble"]["topology_mode"] == "neighbor_json_bundle"
