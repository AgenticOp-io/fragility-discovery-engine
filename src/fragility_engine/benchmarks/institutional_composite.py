"""Moonshot: audit artifact coupling one attacker genome to two reference kernels (decoupled worlds)."""

from __future__ import annotations

import numpy as np

from fragility_engine.runner import rollout_resource_cascade, rollout_stablecoin_network
from fragility_engine.types import RolloutResult
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld


def twin_domain_rollout_artifact(
    network_template: StablecoinNetworkWorld,
    resource_cascade_template: ResourceCascadeWorld,
    genome: np.ndarray,
    *,
    network_seed: int,
    cascade_seed: int,
    base_panic: float = 0.05,
    initial_overload: float = 0.05,
    defender_genome_network: np.ndarray | None = None,
    defender_genome_cascade: np.ndarray | None = None,
) -> dict[str, object]:
    """
    Same decoded shock schedule attacks **two** worlds independently.

    This is **not** a coupled institutional mega-model: kernels stay separate; the composite is an
    explicit side-by-side trace for transfer / benchmarking narratives.
    """

    r_net = rollout_stablecoin_network(
        network_template,
        genome,
        seed=int(network_seed),
        base_panic=float(base_panic),
        defender_genome=defender_genome_network,
    )
    r_rc = rollout_resource_cascade(
        resource_cascade_template,
        genome,
        seed=int(cascade_seed),
        initial_overload=float(initial_overload),
        defender_genome=defender_genome_cascade,
    )

    def compact(r: RolloutResult) -> dict[str, float | bool | int | str | None]:
        return {
            "integral_instability": float(r.integral_instability),
            "collapsed": bool(r.collapsed),
            "attack_cost": float(r.attack_cost),
            "collapse_timestep": r.collapse_timestep,
            "simulation_mode": str(r.simulation_mode),
        }

    return {
        "schema": "fragility-institutional-composite-v1",
        "network": compact(r_net),
        "resource_cascade": compact(r_rc),
        "network_seed": int(network_seed),
        "resource_cascade_seed": int(cascade_seed),
        "genome_shape": [int(x) for x in genome.shape],
    }
