from __future__ import annotations

from collections.abc import Callable

from fragility_engine.types import RolloutResult


def severity_score(r: RolloutResult) -> float:
    """Instability peak plus early-collapse bonus (matches legacy Phase A scalar without attack economics)."""

    speed_bonus = 0.0
    if r.collapsed and r.collapse_timestep is not None:
        speed_bonus = 10.0 / (1 + r.collapse_timestep)
    return float(r.final_instability + speed_bonus)


def fitness_phase_a(r: RolloutResult) -> float:
    """Backward-compatible scalar: severity only (attack_cost ignored)."""

    return severity_score(r)


def fitness_severity_minus_cost(*, attack_cost_weight: float) -> Callable[[RolloutResult], float]:
    """Phase C hook: penalize expensive schedules."""

    w = float(attack_cost_weight)

    def _score(r: RolloutResult) -> float:
        return severity_score(r) - w * r.attack_cost

    return _score
