"""Golden metrics for pinned coupled_institution_rollout_v1 and tetra variant."""

from __future__ import annotations

import pytest

from coupled_institution.golden import (
    BUNDLE_ID,
    BUNDLE_ID_TETRA,
    GOLDEN_METRICS,
    GOLDEN_METRICS_TETRA,
    run_coupled_institution_rollout_v1,
    run_coupled_institution_tetra_rollout_v1,
)


def test_coupled_institution_rollout_v1_golden() -> None:
    result = run_coupled_institution_rollout_v1()
    assert result["bundle_id"] == BUNDLE_ID
    assert result["simulation_mode"] == "coupled_institution_v1"
    for key, expected in GOLDEN_METRICS.items():
        if isinstance(expected, bool):
            assert result[key] is expected
        elif key == "collapse_timestep":
            assert result[key] == int(expected)
        else:
            assert result[key] == pytest.approx(float(expected), rel=1e-9, abs=1e-9)


def test_coupled_institution_tetra_rollout_v1_golden() -> None:
    result = run_coupled_institution_tetra_rollout_v1()
    assert result["bundle_id"] == BUNDLE_ID_TETRA
    assert result["coupling_profile"] == "backlog_tetra"
    for key, expected in GOLDEN_METRICS_TETRA.items():
        if isinstance(expected, bool):
            assert result[key] is expected
        elif key == "collapse_timestep":
            assert result[key] == int(expected)
        else:
            assert result[key] == pytest.approx(float(expected), rel=1e-9, abs=1e-9)
    assert result["integral_instability"] != GOLDEN_METRICS["integral_instability"]
