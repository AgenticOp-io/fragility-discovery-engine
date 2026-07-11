"""Falsification rollout loop."""

from __future__ import annotations

from typing import Any

import numpy as np

from fragility_engine.adversary.encoding import decode_schedule, schedule_attack_cost
from fragility_engine.falsify.protocol import HARNESS_KIND
from fragility_engine.types import RolloutResult, TrajectoryStep


def run_falsification_rollout(
    world: Any,
    genome: np.ndarray,
    *,
    seed: int,
    simulation_mode: str,
) -> RolloutResult:
    """
    Run a cumulative schedule; collapse when ``claim_violated()`` (or ``is_collapsed``).

    Each rollout begins from ``reset()`` (worlds may use ``SnapshotMixin`` internally).
    """

    world.reset()

    horizon = int(world.max_steps)
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
        violated = bool(world.claim_violated()) if hasattr(world, "claim_violated") else world.is_collapsed()
        if violated:
            collapsed = True
            collapse_timestep = t
            break

    return RolloutResult(
        trajectory=trajectory,
        collapsed=collapsed,
        collapse_timestep=collapse_timestep,
        final_instability=peak_instability,
        seed=seed,
        attack_cost=attack_cost,
        simulation_mode=simulation_mode,
        integral_instability=integral_instability,
    )


def replay_meta_for_falsification(*, example: str, harness_kind: str = HARNESS_KIND) -> dict[str, str]:
    return {"harness_kind": harness_kind, "falsification_example": example}
