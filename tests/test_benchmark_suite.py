"""Phase H frozen benchmark bundles."""

from __future__ import annotations

import numpy as np

from fragility_engine.benchmarks import BUNDLE_IDS, assert_bundle_matches_golden, validate_benchmark_suite
from fragility_engine.benchmarks.suite import (
    run_aggregate_rollout_v1,
    run_bundle_rollout_once,
    run_network_er_rollout_v1,
    run_network_neighbor_list_rollout_v1,
    run_resource_cascade_rollout_v1,
    run_service_backlog_rollout_v1,
)


def test_benchmark_bundle_registry_has_expected_ids():
    assert len(BUNDLE_IDS) == 7
    assert "resource_cascade_rollout_v1" in BUNDLE_IDS
    assert "service_backlog_rollout_v1" in BUNDLE_IDS
    assert "inventory_buffer_rollout_v1" in BUNDLE_IDS


def test_validate_benchmark_suite_passes():
    validate_benchmark_suite()


def test_each_bundle_matches_golden_individually():
    assert_bundle_matches_golden(run_aggregate_rollout_v1())


def test_run_bundle_rollout_once_matches_snapshot_helpers():
    pairs = (
        ("aggregate_rollout_v1", run_aggregate_rollout_v1),
        ("network_er_rollout_v1", run_network_er_rollout_v1),
        ("network_neighbor_list_rollout_v1", run_network_neighbor_list_rollout_v1),
        ("resource_cascade_rollout_v1", run_resource_cascade_rollout_v1),
        ("service_backlog_rollout_v1", run_service_backlog_rollout_v1),
    )
    for bid, snap_fn in pairs:
        snap = snap_fn()
        r = run_bundle_rollout_once(bid)
        assert snap["bundle_id"] == bid
        np.testing.assert_allclose(snap["integral_instability"], r.integral_instability, rtol=0, atol=0)
        np.testing.assert_allclose(snap["attack_cost"], r.attack_cost, rtol=0, atol=0)
        assert snap["collapsed"] is r.collapsed
