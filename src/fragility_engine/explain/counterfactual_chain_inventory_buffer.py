"""Ordered cumulative mutations on InventoryBufferWorld templates."""

from __future__ import annotations

from typing import Any

import numpy as np

from fragility_engine.coevolution.defender import clone_inventory_buffer
from fragility_engine.explain.counterfactual import compare_rollouts
from fragility_engine.runner import rollout_inventory_buffer
from fragility_engine.types import RolloutResult
from fragility_engine.world.inventory_buffer import InventoryBufferWorld

INVENTORY_BUFFER_CHAIN_SPEC_SCHEMA = "inventory-buffer-mutation-chain-spec-v1"

_INVENTORY_BUFFER_CHAIN_KINDS = frozenset(
    {
        "demand_spike_gain",
        "fulfillment_erosion",
        "replenish_rate",
        "stock_recovery",
        "stockout_collapse",
        "fulfillment_floor_collapse",
        "recovery_stock",
        "max_steps",
    }
)


def parse_inventory_buffer_chain_spec_payload(obj: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate chain JSON: ``{"schema": ..., "steps": [{"kind": str, "value": number}, ...]}``."""

    sc = obj.get("schema")
    if sc is not None and sc != INVENTORY_BUFFER_CHAIN_SPEC_SCHEMA:
        raise ValueError(
            f"unsupported chain schema {sc!r}; expected {INVENTORY_BUFFER_CHAIN_SPEC_SCHEMA!r}"
        )
    raw_steps = obj.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise ValueError("chain spec must contain a non-empty list 'steps'")
    out: list[dict[str, Any]] = []
    for i, raw in enumerate(raw_steps):
        if not isinstance(raw, dict):
            raise ValueError(f"steps[{i}] must be an object")
        kind = raw.get("kind")
        if kind not in _INVENTORY_BUFFER_CHAIN_KINDS:
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


def apply_inventory_buffer_mutation_step(world: InventoryBufferWorld, step: dict[str, Any]) -> InventoryBufferWorld:
    """Return a clone after one validated physics knob mutation."""

    kind = step["kind"]
    val = step["value"]
    if kind == "max_steps":
        return clone_inventory_buffer(world, max_steps=int(val))
    return clone_inventory_buffer(world, **{kind: float(val)})


def counterfactual_inventory_buffer_mutation_chain_with_rollouts(
    genome: np.ndarray,
    template: InventoryBufferWorld,
    *,
    steps: list[dict[str, Any]],
    rollout_seed: int,
    initial_stock: float,
    variant_initial_stock: float | None = None,
    continue_after_collapse: bool = False,
    defender_genome: np.ndarray | None = None,
) -> tuple[dict[str, Any], RolloutResult, RolloutResult]:
    """Apply ``steps`` cumulatively on a clone; compare baseline template vs final clone."""

    if not steps:
        raise ValueError("steps must be non-empty")

    bis = float(initial_stock)
    vis = bis if variant_initial_stock is None else float(variant_initial_stock)

    tv = clone_inventory_buffer(template)
    applied: list[dict[str, Any]] = []
    for step in steps:
        tv = apply_inventory_buffer_mutation_step(tv, step)
        applied.append(dict(step))

    baseline = rollout_inventory_buffer(
        template,
        genome,
        seed=int(rollout_seed),
        initial_stock=bis,
        continue_after_collapse=bool(continue_after_collapse),
        defender_genome=defender_genome,
    )
    variant = rollout_inventory_buffer(
        tv,
        genome,
        seed=int(rollout_seed),
        initial_stock=vis,
        continue_after_collapse=bool(continue_after_collapse),
        defender_genome=defender_genome,
    )
    merged = compare_rollouts(baseline, variant, label_base="baseline", label_variant="counterfactual")
    merged["intervention"] = "inventory_buffer_mutation_chain"
    merged["mutation_steps"] = applied
    merged["baseline_initial_stock"] = bis
    merged["variant_initial_stock"] = vis
    merged["delta_attack_cost"] = float(baseline.attack_cost - variant.attack_cost)
    merged["delta_integral_instability"] = float(baseline.integral_instability - variant.integral_instability)
    return merged, baseline, variant


def mutation_chain_path_rollouts_inventory_buffer(
    genome: np.ndarray,
    template: InventoryBufferWorld,
    *,
    steps: list[dict[str, Any]],
    rollout_seed: int,
    initial_stock: float,
    variant_initial_stock: float | None = None,
    continue_after_collapse: bool = False,
    defender_genome: np.ndarray | None = None,
) -> list[RolloutResult]:
    """Roll out at each cumulative mutation prefix (path attribution for inventory buffer)."""

    if not steps:
        raise ValueError("steps must be non-empty")

    bis = float(initial_stock)
    vis = bis if variant_initial_stock is None else float(variant_initial_stock)
    cont = bool(continue_after_collapse)
    seed = int(rollout_seed)

    out: list[RolloutResult] = [
        rollout_inventory_buffer(
            template,
            genome,
            seed=seed,
            initial_stock=bis,
            continue_after_collapse=cont,
            defender_genome=defender_genome,
        )
    ]
    tv = clone_inventory_buffer(template)
    for i, step in enumerate(steps):
        tv = apply_inventory_buffer_mutation_step(tv, step)
        stock = bis if i < len(steps) - 1 else vis
        out.append(
            rollout_inventory_buffer(
                tv,
                genome,
                seed=seed,
                initial_stock=stock,
                continue_after_collapse=cont,
                defender_genome=defender_genome,
            )
        )
    return out
