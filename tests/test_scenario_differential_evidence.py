"""Unit tests for QD archive, differential stress, and evidence packs."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from fragility_engine.adversary.differential import (
    DIFFERENTIAL_STRESS_SCHEMA,
    differential_fitness,
    differential_search,
    differential_stress_payload,
)
from fragility_engine.adversary.scenario_archive import (
    SCENARIO_ARCHIVE_SCHEMA,
    behavior_descriptor,
    quality_diversity_search,
    scenario_archive_payload,
)
from fragility_engine.benchmarks.evidence_pack import EVIDENCE_PACK_SCHEMA, build_evidence_pack
from fragility_engine.byow.examples import get_example
from fragility_engine.fel.conventions import SCHEMA_REGISTRY
from fragility_engine.types import RolloutResult


def _toy_rollout(collapsed: bool, severity_proxy: float, cost: float) -> RolloutResult:
    return RolloutResult(
        trajectory=[],
        collapsed=collapsed,
        collapse_timestep=3 if collapsed else None,
        final_instability=severity_proxy,
        seed=1,
        attack_cost=cost,
        integral_instability=severity_proxy,
    )


def test_schema_registry_includes_new_artifacts() -> None:
    assert SCHEMA_REGISTRY["scenario_archive"] == SCENARIO_ARCHIVE_SCHEMA
    assert SCHEMA_REGISTRY["differential_stress"] == DIFFERENTIAL_STRESS_SCHEMA
    assert SCHEMA_REGISTRY["evidence_pack"] == EVIDENCE_PACK_SCHEMA
    assert SCHEMA_REGISTRY["plausibility_search"] == "plausibility-search-v1"
    assert SCHEMA_REGISTRY["stl_robustness"] == "stl-robustness-v1"


def test_behavior_descriptor_bins() -> None:
    r = _toy_rollout(True, 8.0, 2.0)
    bd = behavior_descriptor(r, horizon=12)
    assert len(bd) == 3
    assert bd[0] in (1, 2, 3)


def test_differential_fitness_prefers_a_only_collapse() -> None:
    a = _toy_rollout(True, 5.0, 1.0)
    b_ok = _toy_rollout(False, 1.0, 1.0)
    b_bad = _toy_rollout(True, 5.0, 1.0)
    assert differential_fitness(a, b_ok) > differential_fitness(a, b_bad)


def test_quality_diversity_search_smoke() -> None:
    spec = get_example("capacity-pool")
    world = spec.make_world()

    def evaluator(genome: np.ndarray, seed: int):
        return spec.rollout(world, genome, seed)

    qd = quality_diversity_search(
        evaluator,
        horizon=spec.default_horizon,
        generations=2,
        population_size=8,
        seed=42,
    )
    payload = scenario_archive_payload(qd)
    assert payload["schema"] == SCENARIO_ARCHIVE_SCHEMA
    assert payload["niche_count"] >= 1
    assert payload["niches"]


def test_differential_search_smoke() -> None:
    sa = get_example("capacity-pool")
    sb = get_example("token-bucket")
    wa, wb = sa.make_world(), sb.make_world()

    def ea(g: np.ndarray, s: int):
        return sa.rollout(wa, g, s)

    def eb(g: np.ndarray, s: int):
        return sb.rollout(wb, g, s)

    _result, diff = differential_search(
        ea,
        eb,
        horizon=max(sa.default_horizon, sb.default_horizon),
        seed=101,
        method="ga",
        generations=2,
        population_size=8,
    )
    payload = differential_stress_payload(diff, world_a=sa.name, world_b=sb.name)
    assert payload["schema"] == DIFFERENTIAL_STRESS_SCHEMA
    assert "delta_severity" in payload


def test_evidence_pack_roundtrip(tmp_path: Path) -> None:
    art = tmp_path / "sample.json"
    art.write_text(json.dumps({"schema": "pareto-front-v1", "archive": []}), encoding="utf-8")
    pack = build_evidence_pack(
        artifact_paths=[art],
        include_benchmark_manifest=False,
        notes="test pack",
        repo_root=tmp_path,
    )
    assert pack["schema"] == EVIDENCE_PACK_SCHEMA
    assert pack["pack_content_sha256"]
    assert any(e.get("schema") == "fragility-certificate-v1" for e in pack["entities"])
