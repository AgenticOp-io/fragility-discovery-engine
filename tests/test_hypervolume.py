"""2-D minimization hypervolume helper."""

from __future__ import annotations

import pytest

from fragility_engine.benchmarks.hypervolume import hypervolume_2d_min, nondominated_points_min


def test_nondominated_points_min_filters_dominated():
    pts = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]
    nd = nondominated_points_min(pts)
    assert set(nd) == {(0.0, 0.0)}


def test_hypervolume_2d_min_single_point():
    assert hypervolume_2d_min([(0.2, 0.3)], ref=(1.0, 1.0)) == pytest.approx(0.56)


def test_hypervolume_2d_min_two_points():
    assert hypervolume_2d_min([(0.2, 0.8), (0.8, 0.2)], ref=(1.0, 1.0)) == pytest.approx(0.28)


def test_hypervolume_2d_min_three_point_front():
    hv = hypervolume_2d_min([(1.0, 4.0), (2.0, 2.0), (4.0, 1.0)], ref=(5.0, 5.0))
    assert hv == pytest.approx(11.0)


def test_hypervolume_2d_min_rejects_non_dominated_ref():
    with pytest.raises(ValueError, match="strictly dominate"):
        hypervolume_2d_min([(2.0, 2.0)], ref=(1.0, 5.0))
