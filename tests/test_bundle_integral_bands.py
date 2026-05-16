"""Loose integral_instability bands on frozen Phase H bundles."""

from __future__ import annotations

import pytest

from fragility_engine.benchmarks import BUNDLE_INTEGRAL_BANDS, validate_benchmark_suite
from fragility_engine.benchmarks.suite import (
    assert_bundle_integral_within_band,
    run_aggregate_rollout_v1,
)


def test_bundle_integral_bands_cover_all_bundle_ids():
    from fragility_engine.benchmarks import BUNDLE_IDS

    assert set(BUNDLE_INTEGRAL_BANDS) == set(BUNDLE_IDS)


def test_validate_benchmark_suite_includes_integral_bands():
    validate_benchmark_suite()


def test_integral_band_rejects_out_of_range():
    snap = run_aggregate_rollout_v1()
    snap["integral_instability"] = 99.0
    with pytest.raises(AssertionError, match="outside documented band"):
        assert_bundle_integral_within_band(snap)
