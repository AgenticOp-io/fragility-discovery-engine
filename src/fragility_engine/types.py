from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np

ShockKind = Literal["none", "reserve_loss", "rumor"]


@dataclass(frozen=True)
class ExogenousEvent:
    """World-facing perturbation. The simulation decides physics; adversary chooses timing."""

    kind: ShockKind
    magnitude: float


@dataclass
class TrajectoryStep:
    timestep: int
    state_vector: np.ndarray
    events: tuple[ExogenousEvent, ...]
    agent_actions_summary: dict[str, float]
    metrics: dict[str, float]


@dataclass
class RolloutResult:
    """Single deterministic rollout under a shock schedule + agent configuration."""

    trajectory: list[TrajectoryStep]
    collapsed: bool
    collapse_timestep: int | None
    final_instability: float
    seed: int
    attack_cost: float = 0.0
    simulation_mode: str = "aggregate"
    integral_instability: float = 0.0
    recovery_timestep: int | None = None


@dataclass
class SearchResult:
    """Output of adversary search."""

    best_genome: np.ndarray
    best_fitness: float
    best_rollout: RolloutResult
    history: list[dict[str, Any]] = field(default_factory=list)
    pareto_archive: list[Any] = field(default_factory=list)

