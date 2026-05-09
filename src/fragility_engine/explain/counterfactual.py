from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Any

import numpy as np

from fragility_engine.coevolution.defender import clone_stablecoin_network
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


def neighbor_lists_explicit_weights(world: StablecoinNetworkWorld) -> list[list[float]]:
    """Positive weights aligned with ``neighbor_lists``; implicit uniform **1.0** when unweighted."""

    if world.adjacency is not None:
        raise ValueError("edge-weight counterfactuals require list-only topology (neighbor_lists), not dense adjacency")
    nl = world._neighbor_lists
    if world._neighbor_weights is not None:
        return [list(map(float, row)) for row in world._neighbor_weights]
    return [[1.0] * len(row) for row in nl]


def out_edge_index(neighbor_lists: list[list[int]], from_node: int, to_node: int) -> int:
    """Index ``k`` such that ``neighbor_lists[from_node][k] == to_node``."""

    if from_node < 0 or from_node >= len(neighbor_lists):
        raise ValueError("from_node out of range")
    row = neighbor_lists[from_node]
    for k, tgt in enumerate(row):
        if int(tgt) == int(to_node):
            return int(k)
    raise ValueError(f"no directed edge {from_node} -> {to_node} in neighbor_lists")


def parse_neighbor_edges_patch(raw: list[dict[str, Any]]) -> list[tuple[int, int, float]]:
    """Validate ``[{"from": i, "to": j, "weight": w}, ...]`` directed out-edges."""

    if not raw:
        raise ValueError("edges patch must be non-empty")
    out: list[tuple[int, int, float]] = []
    for i, row in enumerate(raw):
        if not isinstance(row, dict):
            raise ValueError(f"edges_patch[{i}] must be an object")
        for key in ("from", "to", "weight"):
            if key not in row:
                raise ValueError(f"edges_patch[{i}] missing {key!r}")
        w = float(row["weight"])
        if w <= 0.0:
            raise ValueError(f"edges_patch[{i}].weight must be positive")
        out.append((int(row["from"]), int(row["to"]), w))
    return out


def neighbor_edges_weight_patch_apply(
    weights: list[list[float]],
    neighbor_lists: list[list[int]],
    patches: list[tuple[int, int, float]],
) -> list[list[float]]:
    """Deep-copy ``weights`` and assign each patch target its new positive weight."""

    w = deepcopy(weights)
    for ef, et, wt in patches:
        k = out_edge_index(neighbor_lists, ef, et)
        w[int(ef)][k] = float(wt)
    return w


def counterfactual_network_neighbor_edges_weight_patch_with_rollouts(
    genome: np.ndarray,
    template: StablecoinNetworkWorld,
    *,
    edges_patch: list[dict[str, Any]],
    rollout_seed: int,
    base_panic: float,
    continue_after_collapse: bool = False,
) -> tuple[dict[str, Any], RolloutResult, RolloutResult]:
    """Replace weights on several directed out-edges at once (list topology only)."""

    if template.adjacency is not None:
        raise ValueError("edges patch requires neighbor_lists topology (not dense adjacency)")
    nl = template._neighbor_lists
    patches = parse_neighbor_edges_patch(edges_patch)
    baseline_w = neighbor_lists_explicit_weights(template)
    variant_w = neighbor_edges_weight_patch_apply(baseline_w, nl, patches)

    tb = clone_stablecoin_network(template, neighbor_weights=baseline_w)
    tv = clone_stablecoin_network(template, neighbor_weights=variant_w)
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
    merged["intervention"] = "network_neighbor_edges_weight_patch"
    merged["edges_patch"] = [{"from": int(a), "to": int(b), "weight": float(c)} for a, b, c in patches]
    merged["delta_attack_cost"] = float(baseline.attack_cost - variant.attack_cost)
    merged["delta_integral_instability"] = float(baseline.integral_instability - variant.integral_instability)
    return merged, baseline, variant


def counterfactual_network_edge_weight_with_rollouts(
    genome: np.ndarray,
    template: StablecoinNetworkWorld,
    *,
    edge_from: int,
    edge_to: int,
    variant_edge_weight: float,
    rollout_seed: int,
    base_panic: float,
    continue_after_collapse: bool = False,
) -> tuple[dict[str, Any], RolloutResult, RolloutResult]:
    """
    Same genome, seed, ``base_panic``, ``contagion_beta``, and topology; only the weight on one out-edge changes.

    Requires **neighbor_lists** storage (JSON list topology). Unweighted templates use implicit **1.0** per edge.
    """

    nl = template._neighbor_lists
    k = out_edge_index(nl, int(edge_from), int(edge_to))
    baseline_w = neighbor_lists_explicit_weights(template)
    bwt = float(baseline_w[int(edge_from)][k])
    vet = float(variant_edge_weight)
    if vet <= 0.0:
        raise ValueError("variant_edge_weight must be positive")

    variant_w = deepcopy(baseline_w)
    variant_w[int(edge_from)][k] = vet

    tb = clone_stablecoin_network(template, neighbor_weights=baseline_w)
    tv = clone_stablecoin_network(template, neighbor_weights=variant_w)
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
    merged["intervention"] = "network_neighbor_edge_weight_shift"
    merged["edge_from"] = int(edge_from)
    merged["edge_to"] = int(edge_to)
    merged["out_edge_index"] = int(k)
    merged["baseline_edge_weight"] = float(bwt)
    merged["variant_edge_weight"] = float(vet)
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
