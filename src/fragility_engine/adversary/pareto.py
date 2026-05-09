from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fragility_engine.adversary.fitness import severity_score
from fragility_engine.types import RolloutResult


@dataclass(frozen=True)
class ParetoPoint:
    genome: np.ndarray
    severity: float
    attack_cost: float
    collapsed: bool
    integral_instability: float = 0.0


def pareto_indices(severity: np.ndarray, attack_cost: np.ndarray) -> list[int]:
    """Maximize severity, minimize attack_cost (pairwise dominance in 2D)."""

    n = severity.shape[0]
    keep: list[int] = []
    for i in range(n):
        dominated = False
        for j in range(n):
            if i == j:
                continue
            better_or_equal = severity[j] >= severity[i] and attack_cost[j] <= attack_cost[i]
            strictly_better = severity[j] > severity[i] or attack_cost[j] < attack_cost[i]
            if better_or_equal and strictly_better:
                dominated = True
                break
        if not dominated:
            keep.append(i)
    return keep


def pareto_point_from_rollout(genome: np.ndarray, rollout: RolloutResult) -> ParetoPoint:
    return ParetoPoint(
        genome=genome.copy(),
        severity=float(severity_score(rollout)),
        attack_cost=float(rollout.attack_cost),
        collapsed=bool(rollout.collapsed),
        integral_instability=float(rollout.integral_instability),
    )


def merge_pareto_points(points: list[ParetoPoint]) -> list[ParetoPoint]:
    if not points:
        return []
    sev = np.array([p.severity for p in points], dtype=np.float64)
    cost = np.array([p.attack_cost for p in points], dtype=np.float64)
    idx = pareto_indices(sev, cost)
    return [points[i] for i in idx]


def rollout_cloud_to_pareto(genomes: list[np.ndarray], rollouts: list[RolloutResult]) -> list[ParetoPoint]:
    sev = np.array([severity_score(r) for r in rollouts], dtype=np.float64)
    cost = np.array([r.attack_cost for r in rollouts], dtype=np.float64)
    idx = pareto_indices(sev, cost)
    out: list[ParetoPoint] = []
    for i in idx:
        out.append(
            ParetoPoint(
                genome=genomes[i].copy(),
                severity=float(sev[i]),
                attack_cost=float(cost[i]),
                collapsed=rollouts[i].collapsed,
                integral_instability=float(rollouts[i].integral_instability),
            )
        )
    return out
