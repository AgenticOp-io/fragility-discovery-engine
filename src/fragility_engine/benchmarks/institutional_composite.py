"""Audit JSON: one attacker genome evaluated on two, three, or four reference kernels (not coupled)."""

from __future__ import annotations

import numpy as np

from fragility_engine.runner import (
    rollout_resource_cascade,
    rollout_service_backlog,
    rollout_stablecoin,
    rollout_stablecoin_network,
)
from fragility_engine.types import RolloutResult
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.service_backlog import ServiceBacklogWorld
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def _compact_rollout(r: RolloutResult) -> dict[str, float | bool | int | str | None]:
    return {
        "integral_instability": float(r.integral_instability),
        "collapsed": bool(r.collapsed),
        "attack_cost": float(r.attack_cost),
        "collapse_timestep": r.collapse_timestep,
        "simulation_mode": str(r.simulation_mode),
    }


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

    return {
        "schema": "fragility-institutional-composite-v1",
        "network": _compact_rollout(r_net),
        "resource_cascade": _compact_rollout(r_rc),
        "network_seed": int(network_seed),
        "resource_cascade_seed": int(cascade_seed),
        "genome_shape": [int(x) for x in genome.shape],
    }


def triple_domain_rollout_artifact(
    aggregate_template: StablecoinPegWorld,
    network_template: StablecoinNetworkWorld,
    resource_cascade_template: ResourceCascadeWorld,
    genome: np.ndarray,
    *,
    aggregate_seed: int,
    network_seed: int,
    cascade_seed: int,
    initial_panic: float = 0.05,
    base_panic: float = 0.05,
    initial_overload: float = 0.05,
    defender_genome_aggregate: np.ndarray | None = None,
    defender_genome_network: np.ndarray | None = None,
    defender_genome_cascade: np.ndarray | None = None,
) -> dict[str, object]:
    """
    Same schedule evaluated on **three** decoupled kernels: aggregate peg, network contagion, resource cascade.

    Still **not** a coupled institutional model—no cross-world state—only a bundled audit artifact.
    """

    r_agg = rollout_stablecoin(
        aggregate_template,
        genome,
        seed=int(aggregate_seed),
        initial_panic=float(initial_panic),
        defender_genome=defender_genome_aggregate,
    )
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

    return {
        "schema": "fragility-institutional-composite-v2",
        "aggregate": _compact_rollout(r_agg),
        "network": _compact_rollout(r_net),
        "resource_cascade": _compact_rollout(r_rc),
        "aggregate_seed": int(aggregate_seed),
        "network_seed": int(network_seed),
        "resource_cascade_seed": int(cascade_seed),
        "genome_shape": [int(x) for x in genome.shape],
    }


def quad_domain_rollout_artifact(
    aggregate_template: StablecoinPegWorld,
    network_template: StablecoinNetworkWorld,
    resource_cascade_template: ResourceCascadeWorld,
    service_backlog_template: ServiceBacklogWorld,
    genome: np.ndarray,
    *,
    aggregate_seed: int,
    network_seed: int,
    cascade_seed: int,
    backlog_seed: int,
    initial_panic: float = 0.05,
    base_panic: float = 0.05,
    initial_overload: float = 0.05,
    initial_backlog: float = 0.05,
    defender_genome_aggregate: np.ndarray | None = None,
    defender_genome_network: np.ndarray | None = None,
    defender_genome_cascade: np.ndarray | None = None,
    defender_genome_backlog: np.ndarray | None = None,
) -> dict[str, object]:
    """
    Same schedule evaluated on **four** decoupled kernels: peg, network, resource cascade, service backlog.

    Still **not** coupled—no cross-world state—only a bundled audit artifact (schema **v3**).
    """

    r_agg = rollout_stablecoin(
        aggregate_template,
        genome,
        seed=int(aggregate_seed),
        initial_panic=float(initial_panic),
        defender_genome=defender_genome_aggregate,
    )
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
    r_sb = rollout_service_backlog(
        service_backlog_template,
        genome,
        seed=int(backlog_seed),
        initial_backlog=float(initial_backlog),
        defender_genome=defender_genome_backlog,
    )

    return {
        "schema": "fragility-institutional-composite-v3",
        "aggregate": _compact_rollout(r_agg),
        "network": _compact_rollout(r_net),
        "resource_cascade": _compact_rollout(r_rc),
        "service_backlog": _compact_rollout(r_sb),
        "aggregate_seed": int(aggregate_seed),
        "network_seed": int(network_seed),
        "resource_cascade_seed": int(cascade_seed),
        "service_backlog_seed": int(backlog_seed),
        "genome_shape": [int(x) for x in genome.shape],
    }
