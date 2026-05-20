from __future__ import annotations

import numpy as np

from coupled_institution.types import ExogenousEvent, RolloutResult, TrajectoryStep
from coupled_institution.world import CoupledInstitutionWorld


def _attack_cost(events_lane: list[tuple[ExogenousEvent, ...]]) -> float:
    cost = 0.0
    for step_events in events_lane:
        for ev in step_events:
            if ev.kind == "reserve_loss":
                cost += float(ev.magnitude)
            elif ev.kind == "rumor":
                cost += 0.85 * float(ev.magnitude)
    return cost


def rollout_coupled(
    world: CoupledInstitutionWorld,
    schedule: list[tuple[ExogenousEvent, ...]],
    *,
    seed: int,
) -> RolloutResult:
    """Deterministic rollout under a fixed per-timestep shock schedule."""
    world.reset()
    rng = np.random.default_rng(seed)
    trajectory: list[TrajectoryStep] = []
    collapsed = False
    collapse_timestep: int | None = None
    peak_instability = 0.0
    integral = 0.0

    for t, events in enumerate(schedule):
        row = world.step(events, rng)
        inst = float(row.metrics["instability"])
        integral += inst
        peak_instability = max(peak_instability, inst)
        trajectory.append(row)
        if not collapsed and world.is_collapsed():
            collapsed = True
            collapse_timestep = t

    return RolloutResult(
        trajectory=trajectory,
        collapsed=collapsed,
        collapse_timestep=collapse_timestep,
        final_instability=peak_instability,
        seed=int(seed),
        attack_cost=_attack_cost(schedule),
        simulation_mode="coupled_institution_v1",
        integral_instability=integral,
    )


def random_schedule(
    horizon: int,
    *,
    seed: int,
    p_shock: float = 0.35,
) -> list[tuple[ExogenousEvent, ...]]:
    rng = np.random.default_rng(seed)
    out: list[tuple[ExogenousEvent, ...]] = []
    for _ in range(horizon):
        if float(rng.random()) > p_shock:
            out.append(())
            continue
        kind = "reserve_loss" if rng.random() < 0.55 else "rumor"
        mag = float(rng.uniform(0.15, 0.55))
        out.append((ExogenousEvent(kind=kind, magnitude=mag),))
    return out
