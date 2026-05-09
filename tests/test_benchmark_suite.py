"""Phase H frozen benchmark bundles."""

from __future__ import annotations

from fragility_engine.benchmarks import BUNDLE_IDS, assert_bundle_matches_golden, validate_benchmark_suite
from fragility_engine.benchmarks.suite import run_aggregate_rollout_v1


def test_benchmark_bundle_registry_has_three_ids():
    assert len(BUNDLE_IDS) == 3


def test_validate_benchmark_suite_passes():
    validate_benchmark_suite()


def test_each_bundle_matches_golden_individually():
    assert_bundle_matches_golden(run_aggregate_rollout_v1())
