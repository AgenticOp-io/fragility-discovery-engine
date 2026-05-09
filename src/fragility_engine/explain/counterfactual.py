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


def rollout_snapshot(r: RolloutResult) -> dict[str, Any]:
    """JSON-friendly summary for attribution panels."""

    return {
        "collapsed": r.collapsed,
        "collapse_timestep": r.collapse_timestep,
        "peak_instability": r.final_instability,
        "integral_instability": r.integral_instability,
        "recovery_timestep": r.recovery_timestep,
        "attack_cost": r.attack_cost,
        "mode": r.simulation_mode,
        "horizon_steps": len(r.trajectory),
        "seed": r.seed,
    }


def counterfactual_remove_steps(
    genome: np.ndarray,
    rollout_fn: Callable[[np.ndarray, int], RolloutResult],
    *,
    remove_timesteps: list[int],
    base_seed: int,
) -> dict[str, Any]:
    """Structured before/after when dropping shock slots (pinned RNG seeds)."""

    baseline = rollout_fn(genome, base_seed)
    variant_genome = genome_zero_timesteps(genome, remove_timesteps)
    variant = rollout_fn(variant_genome, base_seed)
    merged = compare_rollouts(baseline, variant, label_base="baseline", label_variant="counterfactual")
    merged["removed_timesteps"] = sorted(set(remove_timesteps))
    merged["delta_attack_cost"] = float(baseline.attack_cost - variant.attack_cost)
    merged["delta_integral_instability"] = float(baseline.integral_instability - variant.integral_instability)
    return merged


def compare_rollouts(
    base: RolloutResult,
    variant: RolloutResult,
    *,
    label_base: str = "base",
    label_variant: str = "variant",
) -> dict[str, Any]:
    return {
        label_base: rollout_snapshot(base),
        label_variant: rollout_snapshot(variant),
        "interpretation_hint": _hint(base, variant),
    }


def counterfactual_bundle_to_jsonable(report: dict[str, Any]) -> dict[str, Any]:
    """Already JSON-serializable; placeholder hook for future compression / refs."""

    return dict(report)


def _hint(base: RolloutResult, variant: RolloutResult) -> str:
    if base.collapsed and not variant.collapsed:
        return "Removing/changing this intervention appears necessary for collapse (local sufficiency)."
    if not base.collapsed and variant.collapsed:
        return "Variant collapses while baseline does not — investigate timing or coupling."
    if base.collapsed and variant.collapsed:
        return "Both collapse — compare cost/timing for marginal attribution."
    return "Neither collapses under these pinned seeds."
