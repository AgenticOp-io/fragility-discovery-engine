from __future__ import annotations

from typing import Any

import numpy as np

from fragility_engine.adversary.encoding import decode_schedule, schedule_attack_cost
from fragility_engine.coevolution.defender import (
    build_defended_aggregate_world,
    build_defended_network_world,
    build_defended_resource_cascade_world,
)
from fragility_engine.types import RolloutResult, TrajectoryStep
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld

REPLAY_SCHEMA_VERSION = "0.4.0"


def rollout_stablecoin(
    world_template: StablecoinPegWorld,
    genome: np.ndarray,
    *,
    seed: int,
    initial_reserves: float = 1_000_000.0,
    initial_supply: float = 1_000_000.0,
    initial_panic: float = 0.05,
    continue_after_collapse: bool = False,
    defender_genome: np.ndarray | None = None,
) -> RolloutResult:
    """
    Deterministic given seed: clones behavioral RNG each step from master sequence.

    ``defender_genome`` applies bounded resilience knobs + reserve headroom via
    :mod:`fragility_engine.coevolution.defender`.
    """

    world, reserve_boost = build_defended_aggregate_world(world_template, defender_genome)
    eff_reserves = float(initial_reserves * reserve_boost)

    world.reset(initial_reserves=eff_reserves, initial_supply=initial_supply, initial_panic=initial_panic)
    world.population.reset(initial_supply=initial_supply, rng=np.random.default_rng(seed ^ 0x9E3779B9))

    schedule = decode_schedule(genome)
    attack_cost = schedule_attack_cost(schedule)

    trajectory: list[TrajectoryStep] = []
    collapsed = False
    collapse_timestep: int | None = None
    peak_instability = 0.0
    integral_instability = 0.0

    for t in range(world.max_steps):
        events = schedule.get(t, ())
        step_rng = np.random.default_rng(seed + 17 * (t + 1))
        step = world.step(events, step_rng)
        trajectory.append(step)
        inst = float(step.metrics["instability"])
        peak_instability = max(peak_instability, inst)
        integral_instability += inst

        if world.is_collapsed():
            if collapse_timestep is None:
                collapse_timestep = t
                collapsed = True
            if not continue_after_collapse:
                break

    recovery_timestep = _recovery_timestep(
        trajectory,
        collapsed=collapsed,
        collapse_timestep=collapse_timestep,
        continue_after_collapse=continue_after_collapse,
        depeg_threshold=world.depeg_threshold,
    )

    return RolloutResult(
        trajectory=trajectory,
        collapsed=collapsed,
        collapse_timestep=collapse_timestep,
        final_instability=peak_instability,
        seed=seed,
        attack_cost=attack_cost,
        simulation_mode="aggregate",
        integral_instability=float(integral_instability),
        recovery_timestep=recovery_timestep,
    )


def rollout_stablecoin_network(
    world_template: StablecoinNetworkWorld,
    genome: np.ndarray,
    *,
    seed: int,
    initial_reserves: float = 1_000_000.0,
    initial_supply: float = 1_000_000.0,
    base_panic: float = 0.05,
    continue_after_collapse: bool = False,
    defender_genome: np.ndarray | None = None,
) -> RolloutResult:
    """Graph contagion variant — panic vector diffuses before redemption aggregation.

    ``defender_genome`` applies the same resilience decoding as aggregate rollouts
    (:mod:`fragility_engine.coevolution.defender`); reserve headroom scales ``initial_reserves``.
    """

    world, reserve_boost = build_defended_network_world(world_template, defender_genome)
    eff_reserves = float(initial_reserves * reserve_boost)

    world.reset(initial_reserves=eff_reserves, initial_supply=initial_supply, base_panic=base_panic)
    world.population.reset(initial_supply=initial_supply, rng=np.random.default_rng(seed ^ 0x9E3779B9))

    schedule = decode_schedule(genome)
    attack_cost = schedule_attack_cost(schedule)

    trajectory: list[TrajectoryStep] = []
    collapsed = False
    collapse_timestep: int | None = None
    peak_instability = 0.0
    integral_instability = 0.0

    for t in range(world.max_steps):
        events = schedule.get(t, ())
        step_rng = np.random.default_rng(seed + 17 * (t + 1))
        step = world.step(events, step_rng)
        trajectory.append(step)
        inst = float(step.metrics["instability"])
        peak_instability = max(peak_instability, inst)
        integral_instability += inst

        if world.is_collapsed():
            if collapse_timestep is None:
                collapse_timestep = t
                collapsed = True
            if not continue_after_collapse:
                break

    recovery_timestep = _recovery_timestep(
        trajectory,
        collapsed=collapsed,
        collapse_timestep=collapse_timestep,
        continue_after_collapse=continue_after_collapse,
        depeg_threshold=world.depeg_threshold,
    )

    return RolloutResult(
        trajectory=trajectory,
        collapsed=collapsed,
        collapse_timestep=collapse_timestep,
        final_instability=peak_instability,
        seed=seed,
        attack_cost=attack_cost,
        simulation_mode="network",
        integral_instability=float(integral_instability),
        recovery_timestep=recovery_timestep,
    )


def rollout_resource_cascade(
    world_template: ResourceCascadeWorld,
    genome: np.ndarray,
    *,
    seed: int,
    initial_overload: float = 0.05,
    continue_after_collapse: bool = False,
    defender_genome: np.ndarray | None = None,
) -> RolloutResult:
    """Phase J reference rollout — same schedule decoding as aggregate/network (``decode_schedule``)."""

    world, reserve_boost = build_defended_resource_cascade_world(world_template, defender_genome)
    world.reset(initial_overload=float(initial_overload), capacity_scale=float(reserve_boost))
    world.population.reset(initial_supply=1_000_000.0, rng=np.random.default_rng(seed ^ 0x9E3779B9))

    schedule = decode_schedule(genome)
    attack_cost = schedule_attack_cost(schedule)

    trajectory: list[TrajectoryStep] = []
    collapsed = False
    collapse_timestep: int | None = None
    peak_instability = 0.0
    integral_instability = 0.0

    for t in range(world.max_steps):
        events = schedule.get(t, ())
        step_rng = np.random.default_rng(seed + 17 * (t + 1))
        step = world.step(events, step_rng)
        trajectory.append(step)
        inst = float(step.metrics["instability"])
        peak_instability = max(peak_instability, inst)
        integral_instability += inst

        if world.is_collapsed():
            if collapse_timestep is None:
                collapse_timestep = t
                collapsed = True
            if not continue_after_collapse:
                break

    recovery_timestep = _recovery_timestep(
        trajectory,
        collapsed=collapsed,
        collapse_timestep=collapse_timestep,
        continue_after_collapse=continue_after_collapse,
        depeg_threshold=world.depeg_threshold,
    )

    return RolloutResult(
        trajectory=trajectory,
        collapsed=collapsed,
        collapse_timestep=collapse_timestep,
        final_instability=peak_instability,
        seed=seed,
        attack_cost=attack_cost,
        simulation_mode="resource_cascade",
        integral_instability=float(integral_instability),
        recovery_timestep=recovery_timestep,
    )


def _recovery_timestep(
    trajectory: list[TrajectoryStep],
    *,
    collapsed: bool,
    collapse_timestep: int | None,
    continue_after_collapse: bool,
    depeg_threshold: float,
) -> int | None:
    if not (continue_after_collapse and collapsed and collapse_timestep is not None):
        return None
    for step in trajectory[collapse_timestep + 1 :]:
        if float(step.metrics["price"]) >= float(depeg_threshold) - 1e-12:
            return int(step.timestep)
    return None


def _replay_recoverability_fields(result: RolloutResult) -> dict[str, Any]:
    """Operational recoverability / stress summaries (additive replay keys, schema 0.4.x)."""

    n = len(result.trajectory)
    mean_inst = float(result.integral_instability / n) if n else 0.0
    latency: int | None = None
    if (
        result.collapsed
        and result.collapse_timestep is not None
        and result.recovery_timestep is not None
    ):
        latency = int(result.recovery_timestep - result.collapse_timestep)
    return {
        "steps_recorded": n,
        "mean_instability": mean_inst,
        "recovery_latency_steps": latency,
    }


def build_events_lane(trajectory: list[TrajectoryStep]) -> list[dict[str, Any]]:
    """Per-step shock intensities for replay UI (parallel to ``trajectory`` indices)."""

    lane: list[dict[str, Any]] = []
    for s in trajectory:
        rl = 0.0
        rum = 0.0
        for e in s.events:
            mag = float(np.clip(e.magnitude, 0.0, 1.0))
            if e.kind == "reserve_loss":
                rl = max(rl, mag)
            elif e.kind == "rumor":
                rum = max(rum, mag)
        lane.append(
            {
                "timestep": int(s.timestep),
                "reserve_loss": rl,
                "rumor": rum,
                "event_count": len(s.events),
            }
        )
    return lane


def rollout_to_replay_dict(result: RolloutResult) -> dict[str, Any]:
    """
    Serialize a rollout for replay / tooling (timeline UI, viewer, CI fixtures).

    **Contract** (``schema_version`` = :data:`REPLAY_SCHEMA_VERSION`):

    Top-level keys:

    - ``schema_version`` (`str`) — bump when fields change; viewers should branch on this.
    - ``simulation_mode`` (`str`) — ``aggregate``, ``network``, or ``resource_cascade`` (Phase J scaffold).
    - ``attack_cost`` (`float`) — abstract schedule cost from ``schedule_attack_cost``
      (:mod:`fragility_engine.adversary.encoding`).
    - ``integral_instability`` (`float`) — sum of per-step ``metrics["instability"]``.
    - ``mean_instability`` (`float`) — ``integral_instability / steps_recorded`` (0 if empty).
    - ``steps_recorded`` (`int`) — ``len(trajectory)``.
    - ``recovery_latency_steps`` (`int` or ``null``) — ``recovery_timestep - collapse_timestep`` when both exist.
    - ``recovery_timestep`` (`int` or ``null``) — first step after collapse where price recovers past depeg threshold;
      only when rollout used ``continue_after_collapse=True``.
    - ``collapsed`` (`bool`), ``collapse_timestep`` (`int` or ``null``).
    - ``final_instability`` (`float`) — peak instability observed.
    - ``seed`` (`int`) — RNG anchor for this rollout.
    - ``events_lane`` (`list[dict]`) — parallel shock intensities (``reserve_loss``, ``rumor``, counts).
    - ``trajectory`` (`list[dict]`) — ordered steps.

    Each trajectory element:

    - ``timestep`` (`int`)
    - ``state_vector`` (`list[float]`) — domain-specific layout (aggregate: reserves, supply, price, panic, t…).
    - ``events`` (`list[{"kind","magnitude"}]`)
    - ``agent_actions_summary`` (`dict`)
    - ``metrics`` (`dict`) — includes at least ``price``, ``backing_ratio``, ``instability``, …
    """

    def _step_dict(s: TrajectoryStep) -> dict[str, Any]:
        return {
            "timestep": s.timestep,
            "state_vector": s.state_vector.tolist(),
            "events": [{"kind": e.kind, "magnitude": e.magnitude} for e in s.events],
            "agent_actions_summary": dict(s.agent_actions_summary),
            "metrics": dict(s.metrics),
        }

    traj_dicts = [_step_dict(s) for s in result.trajectory]
    recovery_extras = _replay_recoverability_fields(result)
    return {
        "schema_version": REPLAY_SCHEMA_VERSION,
        "simulation_mode": result.simulation_mode,
        "attack_cost": result.attack_cost,
        "integral_instability": result.integral_instability,
        "recovery_timestep": result.recovery_timestep,
        "collapsed": result.collapsed,
        "collapse_timestep": result.collapse_timestep,
        "final_instability": result.final_instability,
        "seed": result.seed,
        "events_lane": build_events_lane(result.trajectory),
        "trajectory": traj_dicts,
        **recovery_extras,
    }


def summarize_findings(result: RolloutResult) -> str:
    rx = _replay_recoverability_fields(result)
    lines = [
        f"mode={result.simulation_mode}",
        f"attack_cost={result.attack_cost:.4f}",
        f"integral_instability={result.integral_instability:.4f}",
        f"mean_instability={rx['mean_instability']:.6f}",
        f"recovery_timestep={result.recovery_timestep}",
        f"recovery_latency_steps={rx['recovery_latency_steps']}",
        f"collapsed={result.collapsed}",
        f"collapse_timestep={result.collapse_timestep}",
        f"peak_instability={result.final_instability:.4f}",
        f"horizon_steps={len(result.trajectory)}",
    ]
    return "\n".join(lines)
