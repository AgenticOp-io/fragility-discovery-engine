"""Determinism checks for custom worlds."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from fragility_engine.types import RolloutResult


def check_rollout_determinism(
    rollout_fn: Callable[[np.ndarray, int], RolloutResult],
    *,
    genome: np.ndarray | None = None,
    seed: int = 9001,
    atol: float = 1e-9,
) -> tuple[bool, str]:
    """
    Run the same (genome, seed) twice and compare integral instability + collapse bit.

    Returns (ok, message).
    """

    if genome is None:
        genome = np.array([[0.5, 0.7], [0.2, 0.0], [0.8, 0.4]], dtype=np.float64)

    a = rollout_fn(genome, seed)
    b = rollout_fn(genome, seed)

    if a.collapsed != b.collapsed:
        return False, f"collapse mismatch: {a.collapsed} vs {b.collapsed}"
    if abs(a.integral_instability - b.integral_instability) > atol:
        return (
            False,
            f"integral_instability mismatch: {a.integral_instability} vs {b.integral_instability}",
        )
    if len(a.trajectory) != len(b.trajectory):
        return False, f"trajectory length mismatch: {len(a.trajectory)} vs {len(b.trajectory)}"
    return True, "deterministic under fixed (genome, seed)"
