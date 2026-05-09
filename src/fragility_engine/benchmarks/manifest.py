"""Portable benchmark bundle manifest (Phase H extension)."""

from __future__ import annotations

from typing import Any

from fragility_engine.benchmarks.suite import BUNDLE_IDS, GOLDEN_METRICS, RESULT_SCHEMA
from fragility_engine.runner import REPLAY_SCHEMA_VERSION

MANIFEST_SCHEMA = "benchmark-manifest-v1"


def build_benchmark_manifest() -> dict[str, Any]:
    """Frozen bundle inventory + schema fingerprints for citations / CI dashboards."""

    gold_keys = sorted(set().union(*(set(v.keys()) for v in GOLDEN_METRICS.values()))) if GOLDEN_METRICS else []
    return {
        "schema": MANIFEST_SCHEMA,
        "bundle_ids": list(BUNDLE_IDS),
        "bundle_result_schema": RESULT_SCHEMA,
        "replay_schema_version": REPLAY_SCHEMA_VERSION,
        "golden_metric_field_union": gold_keys,
        "bundle_count": len(BUNDLE_IDS),
    }
