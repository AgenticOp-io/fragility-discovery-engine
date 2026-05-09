from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

from fragility_engine.runner import rollout_stablecoin_network
from fragility_engine.types import RolloutResult
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld


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


def counterfactual_remove_steps_with_rollouts(
    genome: np.ndarray,
    rollout_fn: Callable[[np.ndarray, int], RolloutResult],
    *,
    remove_timesteps: list[int],
    base_seed: int,
) -> tuple[dict[str, Any], RolloutResult, RolloutResult]:
    """Like :func:`counterfactual_remove_steps` but returns rollout objects for replay export."""

    baseline = rollout_fn(genome, base_seed)
    variant_genome = genome_zero_timesteps(genome, remove_timesteps)
    variant = rollout_fn(variant_genome, base_seed)
    merged = compare_rollouts(baseline, variant, label_base="baseline", label_variant="counterfactual")
    merged["removed_timesteps"] = sorted(set(remove_timesteps))
    merged["delta_attack_cost"] = float(baseline.attack_cost - variant.attack_cost)
    merged["delta_integral_instability"] = float(baseline.integral_instability - variant.integral_instability)
    return merged, baseline, variant


def counterfactual_remove_steps(
    genome: np.ndarray,
    rollout_fn: Callable[[np.ndarray, int], RolloutResult],
    *,
    remove_timesteps: list[int],
    base_seed: int,
) -> dict[str, Any]:
    """Structured before/after when dropping shock slots (pinned RNG seeds)."""

    merged, _, _ = counterfactual_remove_steps_with_rollouts(
        genome, rollout_fn, remove_timesteps=remove_timesteps, base_seed=base_seed
    )
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


def counterfactual_network_base_panic_with_rollouts(
    genome: np.ndarray,
    template: StablecoinNetworkWorld,
    *,
    baseline_base_panic: float,
    variant_base_panic: float,
    rollout_seed: int,
    continue_after_collapse: bool = False,
) -> tuple[dict[str, Any], RolloutResult, RolloutResult]:
    """Same genome and RNG seed; counterfactual changes uniform **base_panic** at network reset."""

    baseline = rollout_stablecoin_network(
        template,
        genome,
        seed=int(rollout_seed),
        base_panic=float(baseline_base_panic),
        continue_after_collapse=bool(continue_after_collapse),
    )
    variant = rollout_stablecoin_network(
        template,
        genome,
        seed=int(rollout_seed),
        base_panic=float(variant_base_panic),
        continue_after_collapse=bool(continue_after_collapse),
    )
    merged = compare_rollouts(baseline, variant, label_base="baseline", label_variant="counterfactual")
    merged["intervention"] = "network_base_panic_shift"
    merged["baseline_base_panic"] = float(baseline_base_panic)
    merged["variant_base_panic"] = float(variant_base_panic)
    merged["delta_attack_cost"] = float(baseline.attack_cost - variant.attack_cost)
    merged["delta_integral_instability"] = float(baseline.integral_instability - variant.integral_instability)
    return merged, baseline, variant


def counterfactual_network_contagion_beta_with_rollouts(
    genome: np.ndarray,
    template: StablecoinNetworkWorld,
    *,
    baseline_beta: float,
    variant_beta: float,
    rollout_seed: int,
    base_panic: float,
    continue_after_collapse: bool = False,
) -> tuple[dict[str, Any], RolloutResult, RolloutResult]:
    """Same genome, seed, and base_panic; counterfactual swaps **contagion_beta** via topology-preserving clone."""

    from fragility_engine.coevolution.defender import clone_stablecoin_network

    tb = clone_stablecoin_network(template, contagion_beta=float(baseline_beta))
    tv = clone_stablecoin_network(template, contagion_beta=float(variant_beta))
    baseline = rollout_stablecoin_network(
        tb,
        genome,
        seed=int(rollout_seed),
        base_panic=float(base_panic),
        continue_after_collapse=bool(continue_after_collapse),
    )
    variant = rollout_stablecoin_network(
        tv,
        genome,
        seed=int(rollout_seed),
        base_panic=float(base_panic),
        continue_after_collapse=bool(continue_after_collapse),
    )
    merged = compare_rollouts(baseline, variant, label_base="baseline", label_variant="counterfactual")
    merged["intervention"] = "network_contagion_beta_shift"
    merged["baseline_beta"] = float(baseline_beta)
    merged["variant_beta"] = float(variant_beta)
    merged["delta_attack_cost"] = float(baseline.attack_cost - variant.attack_cost)
    merged["delta_integral_instability"] = float(baseline.integral_instability - variant.integral_instability)
    return merged, baseline, variant


def _hint(base: RolloutResult, variant: RolloutResult) -> str:
    if base.collapsed and not variant.collapsed:
        return "Removing/changing this intervention appears necessary for collapse (local sufficiency)."
    if not base.collapsed and variant.collapsed:
        return "Variant collapses while baseline does not — investigate timing or coupling."
    if base.collapsed and variant.collapsed:
        return "Both collapse — compare cost/timing for marginal attribution."
    return "Neither collapses under these pinned seeds."
