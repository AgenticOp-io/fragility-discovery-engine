"""Golden metrics for pinned coupled_institution_rollout_v1."""

from __future__ import annotations

import pytest

from coupled_institution.golden import BUNDLE_ID, GOLDEN_METRICS, run_coupled_institution_rollout_v1


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
