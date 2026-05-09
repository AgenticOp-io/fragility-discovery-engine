from __future__ import annotations

import numpy as np

from fragility_engine.adversary.pareto import pareto_indices


def test_pareto_keeps_tradeoff_points():
    severity = np.array([2.0, 1.0, 1.5])
    cost = np.array([3.0, 1.0, 4.0])
    idx = pareto_indices(severity, cost)
    assert set(idx) == {0, 1}
