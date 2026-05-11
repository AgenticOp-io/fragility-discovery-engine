"""Ordered cumulative mutations on a :class:`~fragility_engine.world.service_backlog.ServiceBacklogWorld` template."""

from __future__ import annotations

from typing import Any

import numpy as np

from fragility_engine.coevolution.defender import clone_service_backlog
from fragility_engine.explain.counterfactual import compare_rollouts
from fragility_engine.runner import rollout_service_backlog
from fragility_engine.types import RolloutResult
from fragility_engine.world.service_backlog import ServiceBacklogWorld

SERVICE_BACKLOG_CHAIN_SPEC_SCHEMA = "service-backlog-mutation-chain-spec-v1"

_SERVICE_BACKLOG_CHAIN_KINDS = frozenset(
    {
        "ingest_gain",
        "rumor_slack_damage",
        "process_rate",
        "slack_recovery",
        "backlog_collapse",
        "slack_floor_collapse",
        "recovery_slack",
        "max_steps",
    }
)


def parse_service_backlog_chain_spec_payload(obj: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate chain JSON: ``{"schema": ..., "steps": [{"kind": str, "value": number}, ...]}``."""

    sc = obj.get("schema")
    if sc is not None and sc != SERVICE_BACKLOG_CHAIN_SPEC_SCHEMA:
        raise ValueError(f"unsupported chain schema {sc!r}; expected {SERVICE_BACKLOG_CHAIN_SPEC_SCHEMA!r}")
    raw_steps = obj.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise ValueError("chain spec must contain a non-empty list 'steps'")
    out: list[dict[str, Any]] = []
    for i, raw in enumerate(raw_steps):
        if not isinstance(raw, dict):
            raise ValueError(f"steps[{i}] must be an object")
        kind = raw.get("kind")
        if kind not in _SERVICE_BACKLOG_CHAIN_KINDS:
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


def apply_service_backlog_mutation_step(world: ServiceBacklogWorld, step: dict[str, Any]) -> ServiceBacklogWorld:
    """Return a clone after one validated physics knob mutation."""

    kind = step["kind"]
    val = step["value"]
    if kind == "max_steps":
        return clone_service_backlog(world, max_steps=int(val))
    return clone_service_backlog(world, **{kind: float(val)})


def counterfactual_service_backlog_mutation_chain_with_rollouts(
    genome: np.ndarray,
    template: ServiceBacklogWorld,
    *,
    steps: list[dict[str, Any]],
    rollout_seed: int,
    initial_backlog: float,
    variant_initial_backlog: float | None = None,
    continue_after_collapse: bool = False,
    defender_genome: np.ndarray | None = None,
) -> tuple[dict[str, Any], RolloutResult, RolloutResult]:
    """
    Apply ``steps`` cumulatively on a template clone; compare baseline (original template) vs final clone.

    Same genome and rollout seed; optional different reset backlog on the variant via
    ``variant_initial_backlog``.
    """

    if not steps:
        raise ValueError("steps must be non-empty")

    bib = float(initial_backlog)
    vib = bib if variant_initial_backlog is None else float(variant_initial_backlog)

    tv = clone_service_backlog(template)
    applied: list[dict[str, Any]] = []
    for step in steps:
        tv = apply_service_backlog_mutation_step(tv, step)
        applied.append(dict(step))

    baseline = rollout_service_backlog(
        template,
        genome,
        seed=int(rollout_seed),
        initial_backlog=bib,
        continue_after_collapse=bool(continue_after_collapse),
        defender_genome=defender_genome,
    )
    variant = rollout_service_backlog(
        tv,
        genome,
        seed=int(rollout_seed),
        initial_backlog=vib,
        continue_after_collapse=bool(continue_after_collapse),
        defender_genome=defender_genome,
    )
    merged = compare_rollouts(baseline, variant, label_base="baseline", label_variant="counterfactual")
    merged["intervention"] = "service_backlog_mutation_chain"
    merged["mutation_steps"] = applied
    merged["baseline_initial_backlog"] = bib
    merged["variant_initial_backlog"] = vib
    merged["delta_attack_cost"] = float(baseline.attack_cost - variant.attack_cost)
    merged["delta_integral_instability"] = float(baseline.integral_instability - variant.integral_instability)
    return merged, baseline, variant


def mutation_chain_path_rollouts_service_backlog(
    genome: np.ndarray,
    template: ServiceBacklogWorld,
    *,
    steps: list[dict[str, Any]],
    rollout_seed: int,
    initial_backlog: float,
    variant_initial_backlog: float | None = None,
    continue_after_collapse: bool = False,
    defender_genome: np.ndarray | None = None,
) -> list[RolloutResult]:
    """
    Roll out at each cumulative mutation prefix (path attribution for service backlog).

    Index ``0`` is the original template with ``initial_backlog``. Each later index applies one more
    step from ``steps`` on a clone. Intermediates use ``initial_backlog`` at reset; the **final**
    rollout uses ``variant_initial_backlog`` when provided.
    """

    if not steps:
        raise ValueError("steps must be non-empty")

    bib = float(initial_backlog)
    vib = bib if variant_initial_backlog is None else float(variant_initial_backlog)
    cont = bool(continue_after_collapse)
    seed = int(rollout_seed)

    out: list[RolloutResult] = [
        rollout_service_backlog(
            template,
            genome,
            seed=seed,
            initial_backlog=bib,
            continue_after_collapse=cont,
            defender_genome=defender_genome,
        )
    ]
    tv = clone_service_backlog(template)
    for i, step in enumerate(steps):
        tv = apply_service_backlog_mutation_step(tv, step)
        ib = bib if i < len(steps) - 1 else vib
        out.append(
            rollout_service_backlog(
                tv,
                genome,
                seed=seed,
                initial_backlog=ib,
                continue_after_collapse=cont,
                defender_genome=defender_genome,
            )
        )
    return out
