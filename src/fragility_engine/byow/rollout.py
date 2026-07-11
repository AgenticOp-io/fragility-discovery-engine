"""Generic rollout loop for custom worlds (BYOW adapter)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

from fragility_engine.adversary.encoding import decode_schedule, schedule_attack_cost
from fragility_engine.types import RolloutResult, TrajectoryStep


def run_rollout(
    world: Any,
    genome: np.ndarray,
    *,
    seed: int,
    simulation_mode: str,
    reset: Callable[[], None] | None = None,
    max_steps: int | None = None,
) -> RolloutResult:
    """
    Standard BYOW rollout: decode genome, step world, track instability.

    ``reset`` defaults to ``world.reset()`` with no kwargs. ``max_steps`` defaults
    to ``world.max_steps``.
    """

    if reset is not None:
        reset()
    else:
        world.reset()

    horizon = int(max_steps if max_steps is not None else world.max_steps)
    schedule = decode_schedule(genome)
    attack_cost = schedule_attack_cost(schedule)

    trajectory: list[TrajectoryStep] = []
    collapsed = False
    collapse_timestep: int | None = None
    peak_instability = 0.0
    integral_instability = 0.0

    for t in range(horizon):
        events = schedule.get(t, ())
        step_rng = np.random.default_rng(seed + 17 * (t + 1))
        step = world.step(events, step_rng)
        trajectory.append(step)
        inst = float(step.metrics.get("instability", world.instability_score()))
        peak_instability = max(peak_instability, inst)
        integral_instability += inst
        if world.is_collapsed():
            collapsed = True
            collapse_timestep = t
            break

    result = RolloutResult(
        trajectory=trajectory,
        collapsed=collapsed,
        collapse_timestep=collapse_timestep,
        final_instability=peak_instability,
        seed=seed,
        attack_cost=attack_cost,
        simulation_mode=simulation_mode,
        integral_instability=integral_instability,
    )
    return result
