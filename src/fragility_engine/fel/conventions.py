"""
Fragility Evidence Language (FEL) v0.1 — reference implementation of naming and conventions.

The normative specification lives in ``docs/FRAGILITY_EVIDENCE_LANGUAGE.md``.
This module does not parse surface syntax; it centralizes operators and schema IDs
so Python exports, tests, and documentation stay aligned.
"""

from __future__ import annotations

from typing import Any, Mapping

from fragility_engine.adversary.fitness import severity_score
from fragility_engine.adversary.pareto import pareto_indices
from fragility_engine.types import RolloutResult

FEL_VERSION = "fel-v0.1"

# Attribution delta kinds (see FEL §6)
DELTA_COUNTERFACTUAL = "delta_minus"  # φ(R₀) − φ(R₁)
DELTA_PATH_FORWARD = "delta_plus"  # φ(R₁) − φ(R₀) along a path edge

# Evidence artifact schemas registered by FEL (subset — see spec §8)
SCHEMA_REGISTRY: dict[str, str] = {
    "rollout": "replay schema via rollout_to_replay_dict (schema_version field)",
    "counterfactual_bundle": "counterfactual-bundle-v1",
    "pareto_front": "pareto-front-v1",
    "attribution_merge": "attribution-merge-v1",
    "explanation_dag": "explanation-dag-v1",
    "explanation_trace": "explanation-trace-v1",
    "mutation_chain_path": "explanation-mutation-chain-path-v1",
    "fragility_certificate": "fragility-certificate-v1",
    "institutional_composite": "fragility-institutional-composite-v4",
    "benchmark_manifest": "benchmark-manifest-v2",
    "falsification_replay": "falsification-replay-v1 (meta.harness_kind=falsification_v1)",
}


def metrics_from_rollout(r: RolloutResult) -> dict[str, float | bool | int | None]:
    """Extract FEL metric tuple φ(R) from a rollout."""

    return {
        "integral_instability": float(r.integral_instability),
        "attack_cost": float(r.attack_cost),
        "final_instability": float(r.final_instability),
        "collapsed": bool(r.collapsed),
        "collapse_timestep": r.collapse_timestep,
        "severity": float(severity_score(r)),
    }


def severity_functional(r: RolloutResult) -> float:
    """FEL severity functional S(R) — same as search layer."""

    return float(severity_score(r))


def to_min_objectives(severity: float, attack_cost: float) -> tuple[float, float]:
    """
    Map attack Pareto objectives to 2-D minimization coordinates for hypervolume.

    (maximize severity, minimize cost) → (-severity, attack_cost)
    """

    return (-float(severity), float(attack_cost))


def attack_pareto_dominates(
    severity_a: float,
    cost_a: float,
    severity_b: float,
    cost_b: float,
) -> bool:
    """True if A dominates B under attack Pareto partial order (max severity, min cost)."""

    better_or_equal = severity_a >= severity_b and cost_a <= cost_b
    strictly = severity_a > severity_b or cost_a < cost_b
    return bool(better_or_equal and strictly)


def pareto_indices_attack(severity: list[float], attack_cost: list[float]) -> list[int]:
    """Non-dominated index set — delegates to ``pareto_indices``."""

    import numpy as np

    return pareto_indices(np.asarray(severity, dtype=np.float64), np.asarray(attack_cost, dtype=np.float64))


def delta_counterfactual(baseline: float, variant: float) -> float:
    """
    Δ⁻ counterfactual attribution: baseline − variant.

    Positive ⇒ the variant **lowered** this metric relative to baseline
    (e.g. removed shocks reduced integral instability).
    """

    return float(baseline) - float(variant)


def delta_path_forward(predecessor: float, successor: float) -> float:
    """
    Δ⁺ path/sweep step: successor − predecessor.

    Positive ⇒ the metric **increased** along the forward path
    (e.g. cumulative mutation added instability).
    """

    return float(successor) - float(predecessor)


def apply_delta_counterfactual_to_rollouts(
    baseline: RolloutResult,
    variant: RolloutResult,
) -> dict[str, float]:
    """Standard counterfactual bundle deltas on integral and attack cost."""

    return {
        "delta_integral_instability": delta_counterfactual(
            baseline.integral_instability, variant.integral_instability
        ),
        "delta_attack_cost": delta_counterfactual(baseline.attack_cost, variant.attack_cost),
    }


def apply_delta_path_to_rollouts(
    predecessor: RolloutResult,
    successor: RolloutResult,
) -> dict[str, float]:
    """Standard mutation-chain / sweep edge deltas."""

    return {
        "delta_integral_instability": delta_path_forward(
            predecessor.integral_instability, successor.integral_instability
        ),
        "delta_attack_cost": delta_path_forward(predecessor.attack_cost, successor.attack_cost),
    }


def fel_laws_summary() -> dict[str, str]:
    """Machine-readable summary of FEL axioms (for manifests and tooling)."""

    return {
        "determinism": "Same (W, G, σ) ⇒ same R on charter worlds (fixed seeds, no fork noise unless pinned).",
        "schedule_domain": "G ∈ [0,1]^{H×2} decoded to exogenous events per timestep.",
        "attack_pareto": "Dominate iff severity ≥ and cost ≤ with strict on one axis.",
        "hypervolume_transform": "HV uses (-severity, attack_cost) minimization coordinates.",
        "delta_counterfactual": "baseline − variant on bundle exports.",
        "delta_path_forward": "successor − predecessor on path/sweep edges.",
        "composite_semantics": "Same G evaluated on multiple Wᵢ; not coupled physics.",
    }
