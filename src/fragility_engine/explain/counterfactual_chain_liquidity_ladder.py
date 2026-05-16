"""Ordered cumulative mutations on a :class:`~fragility_engine.world.liquidity_ladder.LiquidityLadderWorld` template."""

from __future__ import annotations

from typing import Any

import numpy as np

from fragility_engine.coevolution.defender import clone_liquidity_ladder
from fragility_engine.explain.counterfactual import compare_rollouts
from fragility_engine.runner import rollout_liquidity_ladder
from fragility_engine.types import RolloutResult
from fragility_engine.world.liquidity_ladder import LiquidityLadderWorld

LIQUIDITY_LADDER_CHAIN_SPEC_SCHEMA = "liquidity-ladder-mutation-chain-spec-v1"

_LIQUIDITY_LADDER_CHAIN_KINDS = frozenset(
    {
        "margin_call_gain",
        "haircut_damage",
        "delever_rate",
        "depth_recovery",
        "margin_collapse",
        "depth_floor_collapse",
        "recovery_depth",
        "max_steps",
    }
)


def parse_liquidity_ladder_chain_spec_payload(obj: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate chain JSON: ``{"schema": ..., "steps": [{"kind": str, "value": number}, ...]}``."""

    sc = obj.get("schema")
    if sc is not None and sc != LIQUIDITY_LADDER_CHAIN_SPEC_SCHEMA:
        raise ValueError(
            f"unsupported chain schema {sc!r}; expected {LIQUIDITY_LADDER_CHAIN_SPEC_SCHEMA!r}"
        )
    raw_steps = obj.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise ValueError("chain spec must contain a non-empty list 'steps'")
    out: list[dict[str, Any]] = []
    for i, raw in enumerate(raw_steps):
        if not isinstance(raw, dict):
            raise ValueError(f"steps[{i}] must be an object")
        kind = raw.get("kind")
        if kind not in _LIQUIDITY_LADDER_CHAIN_KINDS:
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


def apply_liquidity_ladder_mutation_step(world: LiquidityLadderWorld, step: dict[str, Any]) -> LiquidityLadderWorld:
    """Return a clone after one validated physics knob mutation."""

    kind = step["kind"]
    val = step["value"]
    if kind == "max_steps":
        return clone_liquidity_ladder(world, max_steps=int(val))
    return clone_liquidity_ladder(world, **{kind: float(val)})


def counterfactual_liquidity_ladder_mutation_chain_with_rollouts(
    genome: np.ndarray,
    template: LiquidityLadderWorld,
    *,
    steps: list[dict[str, Any]],
    rollout_seed: int,
    initial_margin: float,
    variant_initial_margin: float | None = None,
    continue_after_collapse: bool = False,
    defender_genome: np.ndarray | None = None,
) -> tuple[dict[str, Any], RolloutResult, RolloutResult]:
    """Apply ``steps`` cumulatively; compare baseline template vs final clone (same genome + seed)."""

    if not steps:
        raise ValueError("steps must be non-empty")

    bim = float(initial_margin)
    vim = bim if variant_initial_margin is None else float(variant_initial_margin)

    tv = clone_liquidity_ladder(template)
    applied: list[dict[str, Any]] = []
    for step in steps:
        tv = apply_liquidity_ladder_mutation_step(tv, step)
        applied.append(dict(step))

    baseline = rollout_liquidity_ladder(
        template,
        genome,
        seed=int(rollout_seed),
        initial_margin=bim,
        continue_after_collapse=bool(continue_after_collapse),
        defender_genome=defender_genome,
    )
    variant = rollout_liquidity_ladder(
        tv,
        genome,
        seed=int(rollout_seed),
        initial_margin=vim,
        continue_after_collapse=bool(continue_after_collapse),
        defender_genome=defender_genome,
    )
    merged = compare_rollouts(baseline, variant, label_base="baseline", label_variant="counterfactual")
    merged["intervention"] = "liquidity_ladder_mutation_chain"
    merged["mutation_steps"] = applied
    merged["baseline_initial_margin"] = bim
    merged["variant_initial_margin"] = vim
    merged["delta_attack_cost"] = float(baseline.attack_cost - variant.attack_cost)
    merged["delta_integral_instability"] = float(baseline.integral_instability - variant.integral_instability)
    return merged, baseline, variant


def mutation_chain_path_rollouts_liquidity_ladder(
    genome: np.ndarray,
    template: LiquidityLadderWorld,
    *,
    steps: list[dict[str, Any]],
    rollout_seed: int,
    initial_margin: float,
    variant_initial_margin: float | None = None,
    continue_after_collapse: bool = False,
    defender_genome: np.ndarray | None = None,
) -> list[RolloutResult]:
    """Roll out at each cumulative mutation prefix (path attribution for liquidity ladder)."""

    if not steps:
        raise ValueError("steps must be non-empty")

    bim = float(initial_margin)
    vim = bim if variant_initial_margin is None else float(variant_initial_margin)
    cont = bool(continue_after_collapse)
    seed = int(rollout_seed)

    out: list[RolloutResult] = [
        rollout_liquidity_ladder(
            template,
            genome,
            seed=seed,
            initial_margin=bim,
            continue_after_collapse=cont,
            defender_genome=defender_genome,
        )
    ]
    tv = clone_liquidity_ladder(template)
    for i, step in enumerate(steps):
        tv = apply_liquidity_ladder_mutation_step(tv, step)
        im = bim if i < len(steps) - 1 else vim
        out.append(
            rollout_liquidity_ladder(
                tv,
                genome,
                seed=seed,
                initial_margin=im,
                continue_after_collapse=cont,
                defender_genome=defender_genome,
            )
        )
    return out
