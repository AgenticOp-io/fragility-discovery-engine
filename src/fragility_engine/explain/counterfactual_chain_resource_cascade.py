"""Ordered cumulative mutations on a :class:`~fragility_engine.world.resource_cascade.ResourceCascadeWorld` template."""

from __future__ import annotations

from typing import Any

import numpy as np

from fragility_engine.coevolution.defender import clone_resource_cascade
from fragility_engine.explain.counterfactual import compare_rollouts
from fragility_engine.runner import rollout_resource_cascade
from fragility_engine.types import RolloutResult
from fragility_engine.world.resource_cascade import ResourceCascadeWorld

RESOURCE_CASCADE_CHAIN_SPEC_SCHEMA = "resource-cascade-mutation-chain-spec-v1"

_RESOURCE_CASCADE_CHAIN_KINDS = frozenset(
    {
        "cascade_coupling",
        "overload_decay",
        "rumor_gain",
        "reserve_hit_primary",
        "reserve_hit_secondary",
        "redeem_damage_primary",
        "collapse_headroom",
        "recovery_headroom",
        "max_steps",
    }
)


def parse_resource_cascade_chain_spec_payload(obj: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate chain JSON: ``{"schema": ..., "steps": [{"kind": str, "value": number}, ...]}``."""

    sc = obj.get("schema")
    if sc is not None and sc != RESOURCE_CASCADE_CHAIN_SPEC_SCHEMA:
        raise ValueError(f"unsupported chain schema {sc!r}; expected {RESOURCE_CASCADE_CHAIN_SPEC_SCHEMA!r}")
    raw_steps = obj.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise ValueError("chain spec must contain a non-empty list 'steps'")
    out: list[dict[str, Any]] = []
    for i, raw in enumerate(raw_steps):
        if not isinstance(raw, dict):
            raise ValueError(f"steps[{i}] must be an object")
        kind = raw.get("kind")
        if kind not in _RESOURCE_CASCADE_CHAIN_KINDS:
            raise ValueError(f"steps[{i}] unknown kind {kind!r}")
        if "value" not in raw:
            raise ValueError(f"steps[{i}] requires 'value'")
        val = raw["value"]
        if kind == "max_steps":
            iv = int(val)
            if iv < 1:
                raise ValueError(f"steps[{i}] max_steps must be >= 1")
            out.append({"kind": kind, "value": iv})
        else:
            out.append({"kind": kind, "value": float(val)})
    return out


def apply_resource_cascade_mutation_step(world: ResourceCascadeWorld, step: dict[str, Any]) -> ResourceCascadeWorld:
    """Return a clone after one validated physics knob mutation."""

    kind = step["kind"]
    val = step["value"]
    if kind == "max_steps":
        return clone_resource_cascade(world, max_steps=int(val))
    return clone_resource_cascade(world, **{kind: float(val)})


def counterfactual_resource_cascade_mutation_chain_with_rollouts(
    genome: np.ndarray,
    template: ResourceCascadeWorld,
    *,
    steps: list[dict[str, Any]],
    rollout_seed: int,
    initial_overload: float,
    variant_initial_overload: float | None = None,
    continue_after_collapse: bool = False,
    defender_genome: np.ndarray | None = None,
) -> tuple[dict[str, Any], RolloutResult, RolloutResult]:
    """
    Apply ``steps`` cumulatively on a template clone; compare baseline (original template) vs final clone.

    Same genome and rollout seed; optional different reset overload on the variant via
    ``variant_initial_overload``.
    """

    if not steps:
        raise ValueError("steps must be non-empty")

    bio = float(initial_overload)
    vio = bio if variant_initial_overload is None else float(variant_initial_overload)

    tv = clone_resource_cascade(template)
    applied: list[dict[str, Any]] = []
    for step in steps:
        tv = apply_resource_cascade_mutation_step(tv, step)
        applied.append(dict(step))

    baseline = rollout_resource_cascade(
        template,
        genome,
        seed=int(rollout_seed),
        initial_overload=bio,
        continue_after_collapse=bool(continue_after_collapse),
        defender_genome=defender_genome,
    )
    variant = rollout_resource_cascade(
        tv,
        genome,
        seed=int(rollout_seed),
        initial_overload=vio,
        continue_after_collapse=bool(continue_after_collapse),
        defender_genome=defender_genome,
    )
    merged = compare_rollouts(baseline, variant, label_base="baseline", label_variant="counterfactual")
    merged["intervention"] = "resource_cascade_mutation_chain"
    merged["mutation_steps"] = applied
    merged["baseline_initial_overload"] = bio
    merged["variant_initial_overload"] = vio
    merged["delta_attack_cost"] = float(baseline.attack_cost - variant.attack_cost)
    merged["delta_integral_instability"] = float(baseline.integral_instability - variant.integral_instability)
    return merged, baseline, variant


def mutation_chain_path_rollouts_resource_cascade(
    genome: np.ndarray,
    template: ResourceCascadeWorld,
    *,
    steps: list[dict[str, Any]],
    rollout_seed: int,
    initial_overload: float,
    variant_initial_overload: float | None = None,
    continue_after_collapse: bool = False,
    defender_genome: np.ndarray | None = None,
) -> list[RolloutResult]:
    """
    Roll out at each cumulative mutation prefix (path attribution for resource cascade).

    Index ``0`` is the original template with ``initial_overload``. Each later index applies one more
    step from ``steps`` on a clone. Intermediates use ``initial_overload`` at reset; the **final**
    rollout uses ``variant_initial_overload`` when provided.
    """

    if not steps:
        raise ValueError("steps must be non-empty")

    bio = float(initial_overload)
    vio = bio if variant_initial_overload is None else float(variant_initial_overload)
    cont = bool(continue_after_collapse)
    seed = int(rollout_seed)

    out: list[RolloutResult] = [
        rollout_resource_cascade(
            template,
            genome,
            seed=seed,
            initial_overload=bio,
            continue_after_collapse=cont,
            defender_genome=defender_genome,
        )
    ]
    tv = clone_resource_cascade(template)
    for i, step in enumerate(steps):
        tv = apply_resource_cascade_mutation_step(tv, step)
        io = bio if i < len(steps) - 1 else vio
        out.append(
            rollout_resource_cascade(
                tv,
                genome,
                seed=seed,
                initial_overload=io,
                continue_after_collapse=cont,
                defender_genome=defender_genome,
            )
        )
    return out
