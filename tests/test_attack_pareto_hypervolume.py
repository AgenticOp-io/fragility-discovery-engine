"""Attack-Pareto hypervolume aligns with pareto_indices dominance."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from fragility_engine.adversary.pareto import pareto_indices
from fragility_engine.benchmarks.hypervolume import (
    attack_archive_to_min_points,
    attack_pareto_to_min_points,
    default_attack_hypervolume_reference,
    hypervolume_2d_attack_pareto,
    nondominated_points_min,
)

ROOT = Path(__file__).resolve().parents[1]


def test_attack_min_nd_matches_pareto_indices_on_bundled_sample() -> None:
    obj = json.loads((ROOT / "artifacts/pareto_viewer/sample_pareto_front.json").read_text(encoding="utf-8"))
    sev = np.array([float(e["severity"]) for e in obj["archive"]], dtype=np.float64)
    cost = np.array([float(e["attack_cost"]) for e in obj["archive"]], dtype=np.float64)
    idx = set(pareto_indices(sev, cost))
    min_pts = attack_pareto_to_min_points(sev.tolist(), cost.tolist())
    nd = set(nondominated_points_min(min_pts))
    assert len(idx) == len(nd)
    for i in idx:
        assert (-float(sev[i]), float(cost[i])) in nd


def test_default_attack_reference_dominates_front() -> None:
    obj = json.loads((ROOT / "artifacts/pareto_viewer/sample_pareto_network.json").read_text(encoding="utf-8"))
    min_pts = attack_archive_to_min_points(obj["archive"])
    ref = default_attack_hypervolume_reference(min_pts)
    for x, y in nondominated_points_min(min_pts):
        assert ref[0] > x and ref[1] > y


def test_hypervolume_2d_attack_pareto_returns_nd_set() -> None:
    obj = json.loads((ROOT / "artifacts/pareto_viewer/sample_pareto_front.json").read_text(encoding="utf-8"))
    hv, ref, nd = hypervolume_2d_attack_pareto(obj["archive"])
    assert hv > 0
    assert ref[0] > max(p[0] for p in nd)
    assert ref[1] > max(p[1] for p in nd)
