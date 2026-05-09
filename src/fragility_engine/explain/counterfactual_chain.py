"""Ordered cumulative mutations on a network template (Phase I — intervention chains)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import numpy as np

from fragility_engine.coevolution.defender import clone_stablecoin_network
from fragility_engine.explain.counterfactual import (
    compare_rollouts,
    neighbor_edges_weight_patch_apply,
    neighbor_lists_explicit_weights,
    out_edge_index,
    parse_neighbor_edges_patch,
)
from fragility_engine.runner import rollout_stablecoin_network
from fragility_engine.types import RolloutResult
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld

CHAIN_SPEC_SCHEMA = "network-mutation-chain-spec-v1"


def parse_chain_spec_payload(obj: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Validate a chain-spec dict (typically loaded from JSON).

    Accepts optional top-level ``schema`` (must be :data:`CHAIN_SPEC_SCHEMA` when present).
    """

    sc = obj.get("schema")
    if sc is not None and sc != CHAIN_SPEC_SCHEMA:
        raise ValueError(f"unsupported chain schema {sc!r}; expected {CHAIN_SPEC_SCHEMA!r}")
    raw_steps = obj.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise ValueError("chain spec must contain a non-empty list 'steps'")
    out: list[dict[str, Any]] = []
    for i, raw in enumerate(raw_steps):
        if not isinstance(raw, dict):
            raise ValueError(f"steps[{i}] must be an object")
        kind = raw.get("kind")
        if kind == "contagion_beta":
            if "value" not in raw:
                raise ValueError(f"steps[{i}] contagion_beta requires 'value'")
            out.append({"kind": "contagion_beta", "value": float(raw["value"])})
        elif kind == "edge_weight":
            for key in ("from", "to", "weight"):
                if key not in raw:
                    raise ValueError(f"steps[{i}] edge_weight requires '{key}'")
            w = float(raw["weight"])
            if w <= 0.0:
                raise ValueError(f"steps[{i}] edge_weight.weight must be positive")
            out.append(
                {
                    "kind": "edge_weight",
                    "from": int(raw["from"]),
                    "to": int(raw["to"]),
                    "weight": w,
                }
            )
        elif kind == "edge_weights_patch":
            edges = raw.get("edges")
            if not isinstance(edges, list) or not edges:
                raise ValueError(f"steps[{i}] edge_weights_patch requires non-empty edges array")
            norm: list[dict[str, Any]] = []
            for j, e in enumerate(edges):
                if not isinstance(e, dict):
                    raise ValueError(f"steps[{i}].edges[{j}] must be an object")
                for key in ("from", "to", "weight"):
                    if key not in e:
                        raise ValueError(f"steps[{i}].edges[{j}] missing {key!r}")
                wf = float(e["weight"])
                if wf <= 0.0:
                    raise ValueError(f"steps[{i}].edges[{j}].weight must be positive")
                norm.append({"from": int(e["from"]), "to": int(e["to"]), "weight": wf})
            parse_neighbor_edges_patch(norm)
            out.append({"kind": "edge_weights_patch", "edges": norm})
        else:
            raise ValueError(f"steps[{i}] unknown kind {kind!r}")
    return out


def apply_network_mutation_step(world: StablecoinNetworkWorld, step: dict[str, Any]) -> StablecoinNetworkWorld:
    """Return a topology-preserving clone after one validated mutation step."""

    kind = step["kind"]
    if kind == "contagion_beta":
        return clone_stablecoin_network(world, contagion_beta=float(step["value"]))
    if kind == "edge_weight":
        ef = int(step["from"])
        et = int(step["to"])
        w = float(step["weight"])
        nl = world._neighbor_lists
        k = out_edge_index(nl, ef, et)
        base_w = neighbor_lists_explicit_weights(world)
        new_w = deepcopy(base_w)
        new_w[ef][k] = w
        return clone_stablecoin_network(world, neighbor_weights=new_w)
    if kind == "edge_weights_patch":
        nl = world._neighbor_lists
        patches = parse_neighbor_edges_patch(step["edges"])
        base_w = neighbor_lists_explicit_weights(world)
        new_w = neighbor_edges_weight_patch_apply(base_w, nl, patches)
        return clone_stablecoin_network(world, neighbor_weights=new_w)
    raise ValueError(f"unknown mutation kind {kind!r}")


def counterfactual_network_mutation_chain_with_rollouts(
    genome: np.ndarray,
    template: StablecoinNetworkWorld,
    *,
    steps: list[dict[str, Any]],
    rollout_seed: int,
    base_panic: float,
    variant_base_panic: float | None = None,
    continue_after_collapse: bool = False,
) -> tuple[dict[str, Any], RolloutResult, RolloutResult]:
    """
    Apply ``steps`` cumulatively on a template clone; compare baseline (original template) vs final clone.

    Same genome and rollout seed; optional different reset panic on the variant via ``variant_base_panic``.
    """

    if not steps:
        raise ValueError("steps must be non-empty")
    if (
        any(s.get("kind") in ("edge_weight", "edge_weights_patch") for s in steps)
        and template.adjacency is not None
    ):
        raise ValueError("edge weight steps require neighbor_lists topology (not dense adjacency)")

    bp = float(base_panic)
    vbp = bp if variant_base_panic is None else float(variant_base_panic)

    tv = clone_stablecoin_network(template)
    applied: list[dict[str, Any]] = []
    for step in steps:
        tv = apply_network_mutation_step(tv, step)
        applied.append(dict(step))

    baseline = rollout_stablecoin_network(
        template,
        genome,
        seed=int(rollout_seed),
        base_panic=bp,
        continue_after_collapse=bool(continue_after_collapse),
    )
    variant = rollout_stablecoin_network(
        tv,
        genome,
        seed=int(rollout_seed),
        base_panic=vbp,
        continue_after_collapse=bool(continue_after_collapse),
    )
    merged = compare_rollouts(baseline, variant, label_base="baseline", label_variant="counterfactual")
    merged["intervention"] = "network_mutation_chain"
    merged["mutation_steps"] = applied
    merged["baseline_base_panic"] = bp
    merged["variant_base_panic"] = vbp
    merged["delta_attack_cost"] = float(baseline.attack_cost - variant.attack_cost)
    merged["delta_integral_instability"] = float(baseline.integral_instability - variant.integral_instability)
    return merged, baseline, variant


def mutation_chain_path_rollouts(
    genome: np.ndarray,
    template: StablecoinNetworkWorld,
    *,
    steps: list[dict[str, Any]],
    rollout_seed: int,
    base_panic: float,
    variant_base_panic: float | None = None,
    continue_after_collapse: bool = False,
) -> list[RolloutResult]:
    """
    Roll out at each **cumulative** mutation prefix (path attribution).

    Index ``0`` is the original template with ``base_panic``. Each later index applies one more
    step from ``steps`` on a clone. All intermediates use ``base_panic`` at reset; the **final**
    rollout uses ``variant_base_panic`` when provided (same rule as
    :func:`counterfactual_network_mutation_chain_with_rollouts`).
    """

    if not steps:
        raise ValueError("steps must be non-empty")
    if (
        any(s.get("kind") in ("edge_weight", "edge_weights_patch") for s in steps)
        and template.adjacency is not None
    ):
        raise ValueError("edge weight steps require neighbor_lists topology (not dense adjacency)")

    bp = float(base_panic)
    vbp = bp if variant_base_panic is None else float(variant_base_panic)
    cont = bool(continue_after_collapse)
    seed = int(rollout_seed)

    out: list[RolloutResult] = [
        rollout_stablecoin_network(
            template,
            genome,
            seed=seed,
            base_panic=bp,
            continue_after_collapse=cont,
        )
    ]
    tv = clone_stablecoin_network(template)
    for i, step in enumerate(steps):
        tv = apply_network_mutation_step(tv, step)
        panic = bp if i < len(steps) - 1 else vbp
        out.append(
            rollout_stablecoin_network(
                tv,
                genome,
                seed=seed,
                base_panic=panic,
                continue_after_collapse=cont,
            )
        )
    return out
