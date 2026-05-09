from __future__ import annotations

import numpy as np

from fragility_engine.types import ExogenousEvent, ShockKind


SHOCK_KINDS: tuple[ShockKind, ...] = ("none", "reserve_loss", "rumor")

# Abstract attacker budget units (not calibrated currency); tunable for search behavior.
DEFAULT_ATTACK_COST_WEIGHTS: dict[ShockKind, float] = {
    "none": 0.0,
    "reserve_loss": 2.5,
    "rumor": 1.0,
}


def decode_kind(index: int) -> ShockKind:
    return SHOCK_KINDS[int(index) % len(SHOCK_KINDS)]


def decode_schedule(genome: np.ndarray) -> dict[int, tuple[ExogenousEvent, ...]]:
    """
    Each row is one timestep: [kind_selector, magnitude].

    kind_selector in [0,1) maps evenly to ShockKind via bucketization.
    """

    if genome.ndim != 2 or genome.shape[1] != 2:
        raise ValueError("Genome must have shape (horizon, 2).")
    horizon = genome.shape[0]
    events: dict[int, tuple[ExogenousEvent, ...]] = {}
    for t in range(horizon):
        sel = float(np.clip(genome[t, 0], 0.0, 1.0 - 1e-9))
        bucket = int(sel * len(SHOCK_KINDS))
        if bucket >= len(SHOCK_KINDS):
            bucket = len(SHOCK_KINDS) - 1
        kind = SHOCK_KINDS[bucket]
        mag = float(np.clip(genome[t, 1], 0.0, 1.0))
        if kind == "none" or mag <= 1e-6:
            continue
        events[t] = (ExogenousEvent(kind=kind, magnitude=mag),)
    return events


def schedule_attack_cost(
    schedule: dict[int, tuple[ExogenousEvent, ...]],
    *,
    weights: dict[ShockKind, float] | None = None,
) -> float:
    """Sum marginal attack costs for decoded shocks (magnitude scales linearly)."""

    wmap = weights or DEFAULT_ATTACK_COST_WEIGHTS
    total = 0.0
    for events in schedule.values():
        for e in events:
            total += float(wmap[e.kind]) * float(np.clip(e.magnitude, 0.0, 1.0))
    return float(total)


def random_genome(horizon: int, rng: np.random.Generator) -> np.ndarray:
    return rng.uniform(size=(horizon, 2))


def mutate_genome(genome: np.ndarray, rng: np.random.Generator, rate: float = 0.15, sigma: float = 0.12) -> np.ndarray:
    child = genome.copy()
    mask = rng.random(size=genome.shape) < rate
    noise = rng.normal(scale=sigma, size=genome.shape)
    child = np.clip(child + mask * noise, 0.0, 1.0)
    return child


def crossover_genome(a: np.ndarray, b: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    h = a.shape[0]
    if h <= 1:
        return a.copy(), b.copy()
    cut = int(rng.integers(1, h))
    c1 = np.vstack([a[:cut], b[cut:]])
    c2 = np.vstack([b[:cut], a[cut:]])
    return c1, c2
