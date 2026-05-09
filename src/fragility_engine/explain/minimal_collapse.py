from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

from fragility_engine.adversary.encoding import decode_schedule
from fragility_engine.types import RolloutResult


def minimize_schedule(
    genome: np.ndarray,
    rollout_fn: Callable[[np.ndarray, int], RolloutResult],
    *,
    base_seed: int,
) -> dict[str, Any]:
    """
    Greedy event removal: drop shocks while preserving collapse (if baseline collapsed).

    This is a cheap first pass at 'minimal collapse sequence' explainability.
    """

    base = rollout_fn(genome, base_seed)
    if not base.collapsed:
        return {
            "baseline_collapsed": False,
            "message": "Baseline schedule did not collapse; minimization undefined.",
            "genome": genome.tolist(),
        }

    schedule = decode_schedule(genome)
    kept_steps = sorted(schedule.keys())

    # Attempt remove one timestep at a time (greedy, order by timestep ascending).
    minimized = dict(schedule)
    for t in kept_steps:
        trial_genome = _genome_with_step_cleared(genome, t)
        trial = rollout_fn(trial_genome, base_seed + 991 + t)
        if trial.collapsed:
            minimized.pop(t, None)
            genome = trial_genome

    minimized_rollout = rollout_fn(genome, base_seed + 4242)
    return {
        "baseline_collapsed": True,
        "minimal_events_by_timestep": {
            str(t): [{"kind": e.kind, "magnitude": e.magnitude} for e in events]
            for t, events in sorted(minimized.items())
        },
        "minimal_genome": genome.tolist(),
        "collapsed": minimized_rollout.collapsed,
        "collapse_timestep": minimized_rollout.collapse_timestep,
    }


def _genome_with_step_cleared(genome: np.ndarray, timestep: int) -> np.ndarray:
    g = genome.copy()
    if 0 <= timestep < g.shape[0]:
        g[timestep, :] = 0.0
    return g


def ablate_event_kind(
    genome: np.ndarray,
    rollout_fn: Callable[[np.ndarray, int], RolloutResult],
    *,
    kind: str,
    base_seed: int,
) -> RolloutResult:
    """Zero-out magnitudes where decoded kind matches (approximate ablation)."""

    from fragility_engine.adversary.encoding import SHOCK_KINDS  # noqa: PLC0415

    g = genome.copy()
    horizon = g.shape[0]
    for t in range(horizon):
        sel = float(np.clip(g[t, 0], 0.0, 1.0 - 1e-9))
        bucket = int(sel * len(SHOCK_KINDS))
        bucket = min(bucket, len(SHOCK_KINDS) - 1)
        if SHOCK_KINDS[bucket] == kind:
            g[t, 1] = 0.0
            g[t, 0] = 0.0
    return rollout_fn(g, base_seed + 8800)
