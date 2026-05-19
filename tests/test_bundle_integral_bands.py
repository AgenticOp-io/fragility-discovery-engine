"""Loose integral_instability bands on frozen Phase H bundles."""

from __future__ import annotations

import pytest

from fragility_engine.benchmarks import (
    BUNDLE_ATTACK_COST_BANDS,
    BUNDLE_COLLAPSED_EXPECT,
    BUNDLE_IDS,
    BUNDLE_INTEGRAL_BANDS,
    validate_benchmark_suite,
)
from fragility_engine.benchmarks.suite import (
    assert_bundle_attack_cost_within_band,
    assert_bundle_collapsed_matches_expect,
    assert_bundle_integral_within_band,
    run_aggregate_rollout_v1,
)


def test_bundle_integral_bands_cover_all_bundle_ids():
    assert set(BUNDLE_INTEGRAL_BANDS) == set(BUNDLE_IDS)


def test_bundle_attack_cost_bands_cover_all_bundle_ids():
    assert set(BUNDLE_ATTACK_COST_BANDS) == set(BUNDLE_IDS)


def test_bundle_collapsed_expect_cover_all_bundle_ids():
    assert set(BUNDLE_COLLAPSED_EXPECT) == set(BUNDLE_IDS)


def test_validate_benchmark_suite_includes_integral_bands():
    validate_benchmark_suite()


def test_integral_band_rejects_out_of_range():
    snap = run_aggregate_rollout_v1()
    snap["integral_instability"] = 99.0
    with pytest.raises(AssertionError, match="outside documented band"):
        assert_bundle_integral_within_band(snap)


def test_attack_cost_band_rejects_out_of_range():
    snap = run_aggregate_rollout_v1()
    snap["attack_cost"] = 99.0
    with pytest.raises(AssertionError, match="attack_cost"):
        assert_bundle_attack_cost_within_band(snap)


def test_collapsed_expect_rejects_mismatch():
    snap = run_aggregate_rollout_v1()
    snap["collapsed"] = not snap["collapsed"]
    with pytest.raises(AssertionError, match="collapsed="):
        assert_bundle_collapsed_matches_expect(snap)
