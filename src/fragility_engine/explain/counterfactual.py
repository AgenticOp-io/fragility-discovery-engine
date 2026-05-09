from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

from fragility_engine.types import RolloutResult


def genome_zero_timesteps(genome: np.ndarray, timesteps: list[int]) -> np.ndarray:
    g = genome.copy()
    for t in timesteps:
        if 0 <= t < g.shape[0]:
            g[t, :] = 0.0
    return g


def counterfactual_remove_steps(
    genome: np.ndarray,
    rollout_fn: Callable[[np.ndarray, int], RolloutResult],
    *,
    remove_timesteps: list[int],
    base_seed: int,
) -> dict[str, Any]:
    """Structured before/after when dropping shock slots (Pinned RNG seeds)."""

    baseline = rollout_fn(genome, base_seed)
    variant_genome = genome_zero_timesteps(genome, remove_timesteps)
    variant = rollout_fn(variant_genome, base_seed)
    return compare_rollouts(baseline, variant, label_base="baseline", label_variant="counterfactual")


def compare_rollouts(
    base: RolloutResult,
    variant: RolloutResult,
    *,
    label_base: str = "base",
    label_variant: str = "variant",
) -> dict[str, Any]:
    return {
        label_base: {
            "collapsed": base.collapsed,
            "collapse_timestep": base.collapse_timestep,
            "peak_instability": base.final_instability,
            "attack_cost": base.attack_cost,
            "mode": base.simulation_mode,
        },
        label_variant: {
            "collapsed": variant.collapsed,
            "collapse_timestep": variant.collapse_timestep,
            "peak_instability": variant.final_instability,
            "attack_cost": variant.attack_cost,
            "mode": variant.simulation_mode,
        },
        "interpretation_hint": _hint(base, variant),
    }


def _hint(base: RolloutResult, variant: RolloutResult) -> str:
    if base.collapsed and not variant.collapsed:
        return "Removing/changing this intervention appears necessary for collapse (local sufficiency)."
    if not base.collapsed and variant.collapsed:
        return "Variant collapses while baseline does not — investigate timing or coupling."
    if base.collapsed and variant.collapsed:
        return "Both collapse — compare cost/timing for marginal attribution."
    return "Neither collapses under these pinned seeds."
