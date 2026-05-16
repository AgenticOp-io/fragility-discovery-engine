"""Portable benchmark bundle manifest (Phase H extension)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from typing import Any

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.benchmarks.hypervolume import hypervolume_2d_min
from fragility_engine.benchmarks.suite import (
    BUNDLE_IDS,
    BUNDLE_INTEGRAL_BANDS,
    GOLDEN_METRICS,
    RESULT_SCHEMA,
)
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, resource_cascade_backend_benchmark_meta
from fragility_engine.world.resource_cascade import ResourceCascadeWorld

MANIFEST_SCHEMA = "benchmark-manifest-v2"

# Frozen 2-objective minimization instance for digest drift detection (not golden bundle metrics).
_HV_REGRESSION_POINTS = ((1.0, 4.0), (3.0, 2.0))
_HV_REGRESSION_REF = (5.0, 6.0)

_BUNDLE_TOPOLOGY: dict[str, dict[str, str]] = {
    "aggregate_rollout_v1": {"world": "StablecoinPegWorld", "topology": "scalar"},
    "network_er_rollout_v1": {"world": "StablecoinNetworkWorld", "topology": "erdos_renyi_dense"},
    "network_neighbor_list_rollout_v1": {"world": "StablecoinNetworkWorld", "topology": "neighbor_lists"},
    "resource_cascade_rollout_v1": {"world": "ResourceCascadeWorld", "topology": "scalar"},
    "service_backlog_rollout_v1": {"world": "ServiceBacklogWorld", "topology": "scalar"},
}


def _try_git_head() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def _package_version() -> str:
    try:
        from importlib.metadata import version

        return version("fragility-engine")
    except Exception:
        return "unknown"


def _golden_metrics_digest() -> str:
    blob = json.dumps(GOLDEN_METRICS, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def format_benchmark_manifest_summary(m: dict[str, Any]) -> str:
    """Short, log-friendly excerpt of ``build_benchmark_manifest()`` for CI / paper appendix checks."""

    prov = m.get("provenance") or {}
    gold = str(m.get("golden_metrics_sha256") or "")
    gold_short = gold if len(gold) <= 20 else f"{gold[:16]}..."
    rb = m.get("resource_cascade_backend") or {}
    bids = m.get("bundle_ids") or []
    bundle_line = ", ".join(str(b) for b in bids)
    lines = [
        f"benchmark_manifest_summary schema={m.get('schema')}",
        f"  bundle_count={m.get('bundle_count')} bundles={bundle_line}",
        f"  golden_metrics_sha256={gold_short}",
        f"  git_commit={prov.get('git_commit') or 'unknown'}",
        (
            "  python={python_version} numpy={numpy_version} "
            "fragility_engine={fragility_engine_version}"
        ).format(
            python_version=prov.get("python_version") or "?",
            numpy_version=prov.get("numpy_version") or "?",
            fragility_engine_version=prov.get("fragility_engine_version") or "?",
        ),
        f"  resource_cascade_backend_effective={rb.get('resource_cascade_backend_effective')}",
        f"  replay_schema_version={m.get('replay_schema_version')}",
    ]
    return "\n".join(lines) + "\n"


def build_benchmark_manifest() -> dict[str, Any]:
    """Frozen bundle inventory + provenance for citations / CI dashboards (v2)."""

    gold_keys = sorted(set().union(*(set(v.keys()) for v in GOLDEN_METRICS.values()))) if GOLDEN_METRICS else []
    rc_template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=26)
    bundles = [{**{"bundle_id": bid}, **_BUNDLE_TOPOLOGY[bid]} for bid in BUNDLE_IDS]
    hv_fixture_pts = [(float(a), float(b)) for a, b in _HV_REGRESSION_POINTS]
    hv_fixture_ref = (float(_HV_REGRESSION_REF[0]), float(_HV_REGRESSION_REF[1]))
    hv_expected = hypervolume_2d_min(hv_fixture_pts, hv_fixture_ref)
    return {
        "schema": MANIFEST_SCHEMA,
        "bundle_ids": list(BUNDLE_IDS),
        "bundles": bundles,
        "bundle_result_schema": RESULT_SCHEMA,
        "replay_schema_version": REPLAY_SCHEMA_VERSION,
        "golden_metric_field_union": gold_keys,
        "golden_metrics_sha256": _golden_metrics_digest(),
        "bundle_integral_bands": {
            bid: {"integral_instability_min": lo, "integral_instability_max": hi}
            for bid, (lo, hi) in BUNDLE_INTEGRAL_BANDS.items()
        },
        "bundle_count": len(BUNDLE_IDS),
        "resource_cascade_backend": resource_cascade_backend_benchmark_meta(rc_template),
        "provenance": {
            "python_version": sys.version.split()[0],
            "numpy_version": str(np.__version__),
            "fragility_engine_version": _package_version(),
            "git_commit": _try_git_head(),
        },
        "hypervolume_2d_min": {
            "module": "fragility_engine.benchmarks.hypervolume",
            "symbol": "hypervolume_2d_min",
            "note": "2-objective minimization hypervolume (Pareto tooling); not used on golden bundle scalars.",
            "regression_fixture": {
                "objective_axes": ["axis_a_min", "axis_b_min"],
                "points": [list(p) for p in hv_fixture_pts],
                "reference": list(hv_fixture_ref),
                "expected_hypervolume": float(hv_expected),
                "note": (
                    "If this value changes, hypervolume_2d_min semantics or nondominated filter likely changed—"
                    "update tests and any downstream digests."
                ),
            },
        },
        "explanation_dag": {
            "schema": "explanation-dag-v1",
            "module": "fragility_engine.explain.explanation_dag",
            "cli": "scripts/export_explanation_dag.py",
        },
        "artifact_schemas": {
            "pareto_front": "pareto-front-v1",
            "attribution_merge": "attribution-merge-v1",
            "fragility_certificate": "fragility-certificate-v1",
            "institutional_composite": [
                "fragility-institutional-composite-v1",
                "fragility-institutional-composite-v2",
                "fragility-institutional-composite-v3",
            ],
            "mutation_chain_path_traces": [
                "explanation-mutation-chain-path-v1",
                "explanation-mutation-chain-path-resource-cascade-v1",
                "explanation-mutation-chain-path-service-backlog-v1",
                "explanation-mutation-chain-path-aggregate-v1",
            ],
            "aggregate_mutation_chain_spec": "aggregate-mutation-chain-spec-v1",
            "service_backlog_mutation_chain_spec": "service-backlog-mutation-chain-spec-v1",
            "resource_cascade_mutation_chain_spec": "resource-cascade-mutation-chain-spec-v1",
        },
        "pareto_hypervolume_fixtures": [
            {
                "path": "tests/fixtures/benchmarks/pinned_pareto_front_minimal.json",
                "objectives_minimized": ["severity", "attack_cost"],
                "pytest_module": "tests.test_pareto_front_hypervolume_fixture",
                "case": "three_point_front",
            },
            {
                "path": "tests/fixtures/benchmarks/pinned_pareto_front_two_branch.json",
                "objectives_minimized": ["severity", "attack_cost"],
                "pytest_module": "tests.test_pareto_front_hypervolume_fixture",
                "case": "two_branch_front",
            },
            {
                "path": "artifacts/flagship/bundled/pareto_front.json",
                "objectives_minimized": ["severity", "attack_cost"],
                "pytest_module": "tests.test_flagship_bundled",
                "case": "flagship_bundled_pareto_hypervolume",
            },
        ],
    }
