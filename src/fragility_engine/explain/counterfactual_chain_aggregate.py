"""Ordered cumulative mutations on a :class:`~fragility_engine.world.stablecoin_peg.StablecoinPegWorld` template."""

from __future__ import annotations

from typing import Any

import numpy as np

from fragility_engine.coevolution.defender import clone_stablecoin_peg
from fragility_engine.explain.counterfactual import compare_rollouts
from fragility_engine.runner import rollout_stablecoin
from fragility_engine.types import RolloutResult
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld

AGGREGATE_CHAIN_SPEC_SCHEMA = "aggregate-mutation-chain-spec-v1"

_AGGREGATE_CHAIN_KINDS = frozenset({"depeg_threshold", "panic_decay", "rumor_panic_gain", "max_steps"})


def parse_aggregate_chain_spec_payload(obj: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate chain JSON: ``{"schema": ..., "steps": [{"kind": str, "value": number}, ...]}``."""

    sc = obj.get("schema")
    if sc is not None and sc != AGGREGATE_CHAIN_SPEC_SCHEMA:
        raise ValueError(f"unsupported chain schema {sc!r}; expected {AGGREGATE_CHAIN_SPEC_SCHEMA!r}")
    raw_steps = obj.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise ValueError("chain spec must contain a non-empty list 'steps'")
    out: list[dict[str, Any]] = []
    for i, raw in enumerate(raw_steps):
        if not isinstance(raw, dict):
            raise ValueError(f"steps[{i}] must be an object")
        kind = raw.get("kind")
        if kind not in _AGGREGATE_CHAIN_KINDS:
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


def apply_aggregate_mutation_step(world: StablecoinPegWorld, step: dict[str, Any]) -> StablecoinPegWorld:
    """Return a clone after one validated physics knob mutation."""

    kind = step["kind"]
    val = step["value"]
    if kind == "max_steps":
        return clone_stablecoin_peg(world, max_steps=int(val))
    return clone_stablecoin_peg(world, **{kind: float(val)})


def counterfactual_aggregate_mutation_chain_with_rollouts(
    genome: np.ndarray,
    template: StablecoinPegWorld,
    *,
    steps: list[dict[str, Any]],
    rollout_seed: int,
    initial_panic: float,
    variant_initial_panic: float | None = None,
    continue_after_collapse: bool = False,
    defender_genome: np.ndarray | None = None,
) -> tuple[dict[str, Any], RolloutResult, RolloutResult]:
    """Apply ``steps`` cumulatively; compare baseline template vs final clone (same genome + seed)."""

    if not steps:
        raise ValueError("steps must be non-empty")

    bip = float(initial_panic)
    vip = bip if variant_initial_panic is None else float(variant_initial_panic)

    tv = clone_stablecoin_peg(template)
    applied: list[dict[str, Any]] = []
    for step in steps:
        tv = apply_aggregate_mutation_step(tv, step)
        applied.append(dict(step))

    baseline = rollout_stablecoin(
        template,
        genome,
        seed=int(rollout_seed),
        initial_panic=bip,
        continue_after_collapse=bool(continue_after_collapse),
        defender_genome=defender_genome,
    )
    variant = rollout_stablecoin(
        tv,
        genome,
        seed=int(rollout_seed),
        initial_panic=vip,
        continue_after_collapse=bool(continue_after_collapse),
        defender_genome=defender_genome,
    )
    merged = compare_rollouts(baseline, variant, label_base="baseline", label_variant="counterfactual")
    merged["intervention"] = "aggregate_mutation_chain"
    merged["mutation_steps"] = applied
    merged["baseline_initial_panic"] = bip
    merged["variant_initial_panic"] = vip
    merged["delta_attack_cost"] = float(baseline.attack_cost - variant.attack_cost)
    merged["delta_integral_instability"] = float(baseline.integral_instability - variant.integral_instability)
    return merged, baseline, variant


def mutation_chain_path_rollouts_aggregate(
    genome: np.ndarray,
    template: StablecoinPegWorld,
    *,
    steps: list[dict[str, Any]],
    rollout_seed: int,
    initial_panic: float,
    variant_initial_panic: float | None = None,
    continue_after_collapse: bool = False,
    defender_genome: np.ndarray | None = None,
) -> list[RolloutResult]:
    """Roll out at each cumulative mutation prefix (path attribution for aggregate peg)."""

    if not steps:
        raise ValueError("steps must be non-empty")

    bip = float(initial_panic)
    vip = bip if variant_initial_panic is None else float(variant_initial_panic)
    cont = bool(continue_after_collapse)
    seed = int(rollout_seed)

    out: list[RolloutResult] = [
        rollout_stablecoin(
            template,
            genome,
            seed=seed,
            initial_panic=bip,
            continue_after_collapse=cont,
            defender_genome=defender_genome,
        )
    ]
    tv = clone_stablecoin_peg(template)
    for i, step in enumerate(steps):
        tv = apply_aggregate_mutation_step(tv, step)
        ip = bip if i < len(steps) - 1 else vip
        out.append(
            rollout_stablecoin(
                tv,
                genome,
                seed=seed,
                initial_panic=ip,
                continue_after_collapse=cont,
                defender_genome=defender_genome,
            )
        )
    return out
