from __future__ import annotations

from typing import Any

import numpy as np

from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def decode_defender_genome_params(
    genome: np.ndarray,
    *,
    panic_decay: float,
    rumor_panic_gain: float,
    depeg_threshold: float,
) -> tuple[dict[str, Any], float]:
    """
    Map bounded defender knobs from baseline world parameters:

    - panic decay multiplier (calms hangover effects)
    - rumor sensitivity multiplier
    - depeg tolerance shift (lower threshold ⇒ harder to declare collapse)
    - reserve headroom boost (aggregate initial reserves only)
    """

    vec = np.clip(np.asarray(genome, dtype=np.float64).reshape(-1), 0.0, 1.0)
    pad = np.zeros(4, dtype=np.float64)
    pad[: min(4, vec.size)] = vec[:4]

    panic_decay_out = float(panic_decay * (0.55 + 0.9 * pad[0]))
    rumor_gain = float(rumor_panic_gain * (0.55 + 0.9 * pad[1]))
    depeg = float(depeg_threshold - 0.07 * pad[2])
    depeg = float(np.clip(depeg, 0.82, 0.995))
    reserve_boost = float(1.0 + 0.5 * pad[3])

    overrides: dict[str, Any] = {
        "panic_decay": panic_decay_out,
        "rumor_panic_gain": rumor_gain,
        "depeg_threshold": depeg,
    }
    return overrides, reserve_boost


def decode_defender_genome(genome: np.ndarray, template: StablecoinPegWorld) -> tuple[dict[str, Any], float]:
    return decode_defender_genome_params(
        genome,
        panic_decay=float(template.panic_decay),
        rumor_panic_gain=float(template.rumor_panic_gain),
        depeg_threshold=float(template.depeg_threshold),
    )


def build_defended_aggregate_world(
    template: StablecoinPegWorld,
    defender_genome: np.ndarray | None,
) -> tuple[StablecoinPegWorld, float]:
    """Clone template parameters with optional defender overrides."""

    if defender_genome is None:
        world = StablecoinPegWorld(
            population=template.population,
            depeg_threshold=template.depeg_threshold,
            panic_decay=template.panic_decay,
            rumor_panic_gain=template.rumor_panic_gain,
            max_steps=template.max_steps,
        )
        return world, 1.0

    overrides, reserve_boost = decode_defender_genome(defender_genome, template)
    world = StablecoinPegWorld(
        population=template.population,
        depeg_threshold=float(overrides["depeg_threshold"]),
        panic_decay=float(overrides["panic_decay"]),
        rumor_panic_gain=float(overrides["rumor_panic_gain"]),
        max_steps=template.max_steps,
    )
    return world, reserve_boost


def clone_stablecoin_network(template: StablecoinNetworkWorld, **phys: Any) -> StablecoinNetworkWorld:
    """Clone topology (dense or list-only) with optional overridden physics kwargs (counterfactuals, studies).

    Optional ``population=`` replaces the template's ``population`` attribute
    (thread-isolated fitness evaluation).
    """

    return _clone_stablecoin_network(template, **phys)


def _clone_stablecoin_network(template: StablecoinNetworkWorld, **phys: Any) -> StablecoinNetworkWorld:
    """Clone topology (dense or list-only) with optional overridden physics kwargs."""

    common: dict[str, Any] = {
        "population": phys.get("population", template.population),
        "node_weights": template.node_weights,
        "max_steps": template.max_steps,
        "contagion_beta": phys.get("contagion_beta", template.contagion_beta),
        "depeg_threshold": phys.get("depeg_threshold", template.depeg_threshold),
        "panic_decay": phys.get("panic_decay", template.panic_decay),
        "rumor_panic_gain": phys.get("rumor_panic_gain", template.rumor_panic_gain),
    }
    if template.adjacency is not None:
        return StablecoinNetworkWorld(adjacency=template.adjacency, **common)
    nl = [list(row) for row in template._neighbor_lists]
    nw_override = phys.get("neighbor_weights", None)
    if nw_override is not None:
        nw = [list(row) for row in nw_override]
    else:
        nw = [list(row) for row in template._neighbor_weights] if template._neighbor_weights else None
    return StablecoinNetworkWorld(neighbor_lists=nl, neighbor_weights=nw, **common)


def build_defended_network_world(
    template: StablecoinNetworkWorld,
    defender_genome: np.ndarray | None,
) -> tuple[StablecoinNetworkWorld, float]:
    """Clone network template with optional defender resilience knobs (same decoding as aggregate)."""

    if defender_genome is None:
        return clone_stablecoin_network(template), 1.0

    overrides, reserve_boost = decode_defender_genome_params(
        defender_genome,
        panic_decay=float(template.panic_decay),
        rumor_panic_gain=float(template.rumor_panic_gain),
        depeg_threshold=float(template.depeg_threshold),
    )
    world = clone_stablecoin_network(
        template,
        depeg_threshold=float(overrides["depeg_threshold"]),
        panic_decay=float(overrides["panic_decay"]),
        rumor_panic_gain=float(overrides["rumor_panic_gain"]),
    )
    return world, reserve_boost


def clone_resource_cascade(template: ResourceCascadeWorld, **phys: Any) -> ResourceCascadeWorld:
    """Clone cascade parameters with optional physics overrides (counterfactuals, defenders).

    Optional ``population=`` replaces the template's ``population`` for concurrent evaluation safety.
    """

    return ResourceCascadeWorld(
        population=phys.get("population", template.population),
        cascade_coupling=float(phys.get("cascade_coupling", template.cascade_coupling)),
        overload_decay=float(phys.get("overload_decay", template.overload_decay)),
        rumor_gain=float(phys.get("rumor_gain", template.rumor_gain)),
        reserve_hit_primary=float(phys.get("reserve_hit_primary", template.reserve_hit_primary)),
        reserve_hit_secondary=float(phys.get("reserve_hit_secondary", template.reserve_hit_secondary)),
        redeem_damage_primary=float(phys.get("redeem_damage_primary", template.redeem_damage_primary)),
        collapse_headroom=float(phys.get("collapse_headroom", template.collapse_headroom)),
        recovery_headroom=float(phys.get("recovery_headroom", template.recovery_headroom)),
        max_steps=int(phys.get("max_steps", template.max_steps)),
    )


def build_defended_resource_cascade_world(
    template: ResourceCascadeWorld,
    defender_genome: np.ndarray | None,
) -> tuple[ResourceCascadeWorld, float]:
    """
    Apply the same four-knob defender decoding as aggregate/network:

    - Slots map to ``overload_decay``, ``rumor_gain``, ``recovery_headroom``; ``reserve_boost`` damps initial overload.
    """

    if defender_genome is None:
        return clone_resource_cascade(template), 1.0

    overrides, reserve_boost = decode_defender_genome_params(
        defender_genome,
        panic_decay=float(template.overload_decay),
        rumor_panic_gain=float(template.rumor_gain),
        depeg_threshold=float(template.recovery_headroom),
    )
    world = clone_resource_cascade(
        template,
        overload_decay=float(overrides["panic_decay"]),
        rumor_gain=float(overrides["rumor_panic_gain"]),
        recovery_headroom=float(overrides["depeg_threshold"]),
    )
    return world, reserve_boost


def random_defender_genome(rng: np.random.Generator) -> np.ndarray:
    return rng.uniform(size=(4,))
