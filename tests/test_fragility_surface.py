from __future__ import annotations

import numpy as np
from scripts.fragility_surface import run_fragility_surface_grid


def test_fragility_surface_grid_small_deterministic():
    panic_axis = np.linspace(0.05, 0.2, 3)
    depeg_axis = np.linspace(0.9, 0.96, 3)
    rows = run_fragility_surface_grid(seed=100, steps=12, panic_axis=panic_axis, depeg_axis=depeg_axis)
    assert len(rows) == 9
    keys = {"panic0", "depeg_threshold", "collapsed", "collapse_t", "peak_instability"}
    assert keys == set(rows[0].keys())
    rows2 = run_fragility_surface_grid(seed=100, steps=12, panic_axis=panic_axis, depeg_axis=depeg_axis)
    assert rows == rows2
