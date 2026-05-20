from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np

ShockKind = Literal["none", "reserve_loss", "rumor"]


@dataclass(frozen=True)
class ExogenousEvent:
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
    trajectory: list[TrajectoryStep]
    collapsed: bool
    collapse_timestep: int | None
    final_instability: float
    seed: int
    attack_cost: float = 0.0
    simulation_mode: str = "coupled_institution_v1"
    integral_instability: float = 0.0
    recovery_timestep: int | None = None

    def to_replay_dict(self) -> dict[str, Any]:
        from coupled_institution.replay import rollout_to_replay_dict

        return rollout_to_replay_dict(self)
