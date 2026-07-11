"""Differential stress search: schedules that break world A but not world B.

Engineering differential (not FEL counterfactual Δ⁻ on one world): evaluate the
*same* exogenous schedule on two rollout callables and prefer outcomes where A
collapses and B survives.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np

from fragility_engine.adversary.fitness import severity_score
from fragility_engine.adversary.search import genetic_search, monte_carlo_search
from fragility_engine.types import RolloutResult, SearchResult

DIFFERENTIAL_STRESS_SCHEMA = "differential-stress-v1"


@dataclass(frozen=True)
class DifferentialRollout:
    genome: np.ndarray
    rollout_a: RolloutResult
    rollout_b: RolloutResult
    fitness: float


def differential_fitness(rollout_a: RolloutResult, rollout_b: RolloutResult) -> float:
    """Higher is better: reward A-collapse∧¬B-collapse, then severity gap."""

    sev_a = float(severity_score(rollout_a))
    sev_b = float(severity_score(rollout_b))
    gap = sev_a - sev_b
    if rollout_a.collapsed and not rollout_b.collapsed:
        return 1000.0 + gap
    if rollout_a.collapsed and rollout_b.collapsed:
        return 100.0 + gap
    if (not rollout_a.collapsed) and (not rollout_b.collapsed):
        return gap
    return -1000.0 + gap


def differential_search(
    rollout_a: Callable[[np.ndarray, int], RolloutResult],
    rollout_b: Callable[[np.ndarray, int], RolloutResult],
    *,
    horizon: int,
    seed: int,
    method: str = "ga",
    generations: int = 8,
    population_size: int = 16,
    samples: int = 40,
) -> tuple[SearchResult, DifferentialRollout]:
    """Search schedules maximizing ``differential_fitness(A, B)``."""

    last: dict[str, Any] = {"rb": None}

    def rollout_fn(genome: np.ndarray, s: int) -> RolloutResult:
        ra = rollout_a(genome, s)
        rb = rollout_b(genome, s + 17_771)
        last["rb"] = rb
        return ra

    def fitness_fn(rr: RolloutResult) -> float:
        rb = last.get("rb")
        if rb is None:
            return float(severity_score(rr))
        return differential_fitness(rr, rb)

    if method == "mc":
        result = monte_carlo_search(
            rollout_fn,
            horizon=horizon,
            samples=samples,
            seed=seed,
            fitness_fn=fitness_fn,
        )
    else:
        result = genetic_search(
            rollout_fn,
            horizon=horizon,
            generations=generations,
            population_size=population_size,
            seed=seed,
            fitness_fn=fitness_fn,
        )

    genome = result.best_genome
    ra = rollout_a(genome, seed + 9)
    rb = rollout_b(genome, seed + 9 + 17_771)
    diff = DifferentialRollout(
        genome=genome.copy(),
        rollout_a=ra,
        rollout_b=rb,
        fitness=differential_fitness(ra, rb),
    )
    result.best_rollout = ra
    result.best_fitness = diff.fitness
    return result, diff


def differential_stress_payload(
    diff: DifferentialRollout,
    *,
    world_a: str,
    world_b: str,
) -> dict[str, Any]:
    ra, rb = diff.rollout_a, diff.rollout_b
    return {
        "schema": DIFFERENTIAL_STRESS_SCHEMA,
        "world_a": world_a,
        "world_b": world_b,
        "fitness": diff.fitness,
        "a_collapsed_b_survived": bool(ra.collapsed and not rb.collapsed),
        "delta_severity": float(severity_score(ra) - severity_score(rb)),
        "delta_integral_instability": float(ra.integral_instability - rb.integral_instability),
        "delta_attack_cost": float(ra.attack_cost - rb.attack_cost),
        "note": (
            "Engineering differential on the same schedule across two worlds; "
            "not FEL counterfactual Δ⁻ (same world, different intervention)."
        ),
        "metrics_a": {
            "collapsed": ra.collapsed,
            "collapse_timestep": ra.collapse_timestep,
            "severity": float(severity_score(ra)),
            "integral_instability": ra.integral_instability,
            "attack_cost": ra.attack_cost,
            "simulation_mode": ra.simulation_mode,
        },
        "metrics_b": {
            "collapsed": rb.collapsed,
            "collapse_timestep": rb.collapse_timestep,
            "severity": float(severity_score(rb)),
            "integral_instability": rb.integral_instability,
            "attack_cost": rb.attack_cost,
            "simulation_mode": rb.simulation_mode,
        },
        "genome": diff.genome.tolist(),
    }
