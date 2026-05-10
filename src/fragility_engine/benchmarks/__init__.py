"""Benchmark bundles (Phase H) and experimental ensemble robustness summaries."""

from fragility_engine.benchmarks.certificate import FRAGILITY_CERTIFICATE_SCHEMA, build_fragility_certificate
from fragility_engine.benchmarks.ensemble import (
    robustness_ensemble_1d_param_sweep,
    robustness_ensemble_2d_param_grid,
    robustness_ga_budget_2d_grid,
    robustness_ga_generations_1d_sweep,
    robustness_ga_population_1d_sweep,
    robustness_rollouts_neighbor_json_bundle,
    robustness_rollouts_over_graph_seeds,
)
from fragility_engine.benchmarks.flagship import run_flagship_demo
from fragility_engine.benchmarks.institutional_composite import (
    triple_domain_rollout_artifact,
    twin_domain_rollout_artifact,
)
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
    "FRAGILITY_CERTIFICATE_SCHEMA",
    "MANIFEST_SCHEMA",
    "build_benchmark_manifest",
    "build_fragility_certificate",
    "BUNDLE_IDS",
    "GOLDEN_METRICS",
    "PINNED_GENOME_SEED",
    "PINNED_ROLLOUT_SEED",
    "PINNED_SCHEDULE_HORIZON",
    "RESULT_SCHEMA",
    "assert_bundle_matches_golden",
    "bundle_search_evaluator",
    "rollout_bundle_with_genome",
    "robustness_ensemble_1d_param_sweep",
    "robustness_ensemble_2d_param_grid",
    "robustness_ga_budget_2d_grid",
    "robustness_ga_generations_1d_sweep",
    "robustness_ga_population_1d_sweep",
    "robustness_rollouts_neighbor_json_bundle",
    "robustness_rollouts_over_graph_seeds",
    "triple_domain_rollout_artifact",
    "twin_domain_rollout_artifact",
    "run_benchmark_suite",
    "run_bundle_rollout_once",
    "run_flagship_demo",
    "run_phase_h_search_microbench",
    "validate_benchmark_suite",
]
