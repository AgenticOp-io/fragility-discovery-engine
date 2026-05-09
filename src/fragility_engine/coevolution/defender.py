from __future__ import annotations

from typing import Any

import numpy as np

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


def build_defended_network_world(
    template: StablecoinNetworkWorld,
    defender_genome: np.ndarray | None,
) -> tuple[StablecoinNetworkWorld, float]:
    """Clone network template with optional defender resilience knobs (same decoding as aggregate)."""

    if defender_genome is None:
        world = StablecoinNetworkWorld(
            population=template.population,
            adjacency=template.adjacency,
            node_weights=template.node_weights,
            contagion_beta=template.contagion_beta,
            depeg_threshold=template.depeg_threshold,
            panic_decay=template.panic_decay,
            rumor_panic_gain=template.rumor_panic_gain,
            max_steps=template.max_steps,
        )
        return world, 1.0

    overrides, reserve_boost = decode_defender_genome_params(
        defender_genome,
        panic_decay=float(template.panic_decay),
        rumor_panic_gain=float(template.rumor_panic_gain),
        depeg_threshold=float(template.depeg_threshold),
    )
    world = StablecoinNetworkWorld(
        population=template.population,
        adjacency=template.adjacency,
        node_weights=template.node_weights,
        contagion_beta=template.contagion_beta,
        depeg_threshold=float(overrides["depeg_threshold"]),
        panic_decay=float(overrides["panic_decay"]),
        rumor_panic_gain=float(overrides["rumor_panic_gain"]),
        max_steps=template.max_steps,
    )
    return world, reserve_boost


def random_defender_genome(rng: np.random.Generator) -> np.ndarray:
    return rng.uniform(size=(4,))
