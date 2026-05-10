"""Portable benchmark bundle manifest (Phase H extension)."""

from __future__ import annotations

from typing import Any

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.benchmarks.suite import BUNDLE_IDS, GOLDEN_METRICS, RESULT_SCHEMA
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, resource_cascade_backend_benchmark_meta
from fragility_engine.world.resource_cascade import ResourceCascadeWorld

MANIFEST_SCHEMA = "benchmark-manifest-v1"


def build_benchmark_manifest() -> dict[str, Any]:
    """Frozen bundle inventory + schema fingerprints for citations / CI dashboards."""

    gold_keys = sorted(set().union(*(set(v.keys()) for v in GOLDEN_METRICS.values()))) if GOLDEN_METRICS else []
    rc_template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=26)
    return {
        "schema": MANIFEST_SCHEMA,
        "bundle_ids": list(BUNDLE_IDS),
        "bundle_result_schema": RESULT_SCHEMA,
        "replay_schema_version": REPLAY_SCHEMA_VERSION,
        "golden_metric_field_union": gold_keys,
        "bundle_count": len(BUNDLE_IDS),
        "resource_cascade_backend": resource_cascade_backend_benchmark_meta(rc_template),
    }
