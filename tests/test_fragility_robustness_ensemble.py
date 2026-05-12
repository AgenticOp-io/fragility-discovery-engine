"""Ensemble robustness over graph seeds (Phase H)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from fragility_engine.benchmarks.ensemble import (
    robustness_ensemble_1d_param_sweep,
    robustness_ensemble_2d_param_grid,
    robustness_rollouts_neighbor_json_bundle,
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
    assert out["topology_mode"] == "synthetic_er_ws"
    assert out["neighbor_json_paths"] is None
    assert out["topology_representation"] == "dense"
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


def test_robustness_neighbor_json_bundle_two_topologies(tmp_path: Path):
    p0 = tmp_path / "c2.json"
    p1 = tmp_path / "c3.json"
    p0.write_text(json.dumps([[1], [0]]), encoding="utf-8")
    p1.write_text(json.dumps([[1], [2], [0]]), encoding="utf-8")
    genome = np.random.default_rng(42).uniform(size=(8, 2))
    out = robustness_rollouts_neighbor_json_bundle(
        genome,
        neighbor_json_paths=[p0, p1],
        rollout_seed=77,
        contagion_beta=0.35,
        whale_frac=0.2,
        base_panic=0.05,
        max_steps=20,
    )
    assert out["topology_mode"] == "neighbor_json_bundle"
    assert out["summary"]["count"] == 2
    assert out["runs"][0]["topology_index"] == 0
    assert out["runs"][1]["n_nodes"] == 3
    assert "graph_seed" not in out["runs"][0]


def test_neighbor_bundle_rejects_synthetic_topology_sweep(tmp_path: Path):
    p0 = tmp_path / "t.json"
    p0.write_text(json.dumps([[1], [0]]), encoding="utf-8")
    genome = np.random.default_rng(7).uniform(size=(6, 2))
    with pytest.raises(ValueError, match="er_p"):
        robustness_ensemble_1d_param_sweep(
            genome,
            sweep_param="er_p",
            sweep_values=[0.1, 0.2],
            graph_kind="erdos_renyi",
            nodes=10,
            graph_seeds=[1],
            rollout_seed=8,
            neighbor_json_paths=[p0],
        )


def test_robustness_1d_neighbor_bundle_sweep(tmp_path: Path):
    p0 = tmp_path / "t.json"
    p0.write_text(json.dumps([[1], [0]]), encoding="utf-8")
    genome = np.random.default_rng(7).uniform(size=(6, 2))
    out = robustness_ensemble_1d_param_sweep(
        genome,
        sweep_param="contagion_beta",
        sweep_values=[0.3, 0.4],
        graph_kind="erdos_renyi",
        nodes=10,
        graph_seeds=[1],
        rollout_seed=8,
        neighbor_json_paths=[p0],
    )
    assert out["topology_mode"] == "neighbor_json_bundle"
    assert len(out["points"]) == 2


def test_dense_and_neighbor_lists_parity_per_graph_seed():
    """List topology path matches dense adjacency for identical ER draws."""

    genome = np.random.default_rng(9002).uniform(size=(10, 2))
    seeds = [201, 202]
    dense = robustness_rollouts_over_graph_seeds(
        genome,
        graph_kind="erdos_renyi",
        nodes=11,
        graph_seeds=seeds,
        rollout_seed=555,
        topology_representation="dense",
    )
    nl = robustness_rollouts_over_graph_seeds(
        genome,
        graph_kind="erdos_renyi",
        nodes=11,
        graph_seeds=seeds,
        rollout_seed=555,
        topology_representation="neighbor_lists",
    )
    assert nl["topology_representation"] == "neighbor_lists"
    for a, b in zip(dense["runs"], nl["runs"], strict=True):
        assert a["graph_seed"] == b["graph_seed"]
        assert a["integral_instability"] == b["integral_instability"]
        assert a["collapsed"] == b["collapsed"]


def test_robustness_2d_param_grid_schema():
    genome = np.random.default_rng(9003).uniform(size=(8, 2))
    out = robustness_ensemble_2d_param_grid(
        genome,
        sweep_param_x="base_panic",
        sweep_values_x=[0.04, 0.06],
        sweep_param_y="contagion_beta",
        sweep_values_y=[0.30, 0.38],
        graph_kind="erdos_renyi",
        nodes=10,
        graph_seeds=[301],
        rollout_seed=6000,
    )
    assert out["schema"] == "fragility-robustness-sensitivity-2d-v1"
    assert out["summary"]["grid_cells"] == 4
    assert len(out["points"]) == 4


def test_robustness_2d_same_axis_raises():
    genome = np.random.default_rng(1).uniform(size=(4, 2))
    with pytest.raises(ValueError, match="differ"):
        robustness_ensemble_2d_param_grid(
            genome,
            sweep_param_x="er_p",
            sweep_values_x=[0.1],
            sweep_param_y="er_p",
            sweep_values_y=[0.2],
            graph_kind="erdos_renyi",
            nodes=8,
            graph_seeds=[1],
            rollout_seed=1,
        )


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
