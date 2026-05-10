"""Benchmark bundles (Phase H) and experimental ensemble robustness summaries."""

from fragility_engine.benchmarks.ensemble import robustness_rollouts_over_graph_seeds
from fragility_engine.benchmarks.manifest import MANIFEST_SCHEMA, build_benchmark_manifest
from fragility_engine.benchmarks.suite import (
    BUNDLE_IDS,
    GOLDEN_METRICS,
    PINNED_GENOME_SEED,
    PINNED_ROLLOUT_SEED,
    PINNED_SCHEDULE_HORIZON,
    RESULT_SCHEMA,
    assert_bundle_matches_golden,
    bundle_search_evaluator,
    rollout_bundle_with_genome,
    run_benchmark_suite,
    run_bundle_rollout_once,
    run_phase_h_search_microbench,
    validate_benchmark_suite,
)

__all__ = [
    "MANIFEST_SCHEMA",
    "build_benchmark_manifest",
    "BUNDLE_IDS",
    "GOLDEN_METRICS",
    "PINNED_GENOME_SEED",
    "PINNED_ROLLOUT_SEED",
    "PINNED_SCHEDULE_HORIZON",
    "RESULT_SCHEMA",
    "assert_bundle_matches_golden",
    "bundle_search_evaluator",
    "rollout_bundle_with_genome",
    "robustness_rollouts_over_graph_seeds",
    "run_benchmark_suite",
    "run_bundle_rollout_once",
    "run_phase_h_search_microbench",
    "validate_benchmark_suite",
]
