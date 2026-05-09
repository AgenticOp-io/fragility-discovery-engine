from __future__ import annotations

import numpy as np

from fragility_engine.adversary.fitness import fitness_phase_a, fitness_severity_minus_cost, severity_score
from fragility_engine.types import RolloutResult, TrajectoryStep


def _dummy_rollout(*, attack_cost: float) -> RolloutResult:
    step = TrajectoryStep(
        timestep=0,
        state_vector=np.zeros(5),
        events=(),
        agent_actions_summary={},
        metrics={},
    )
    return RolloutResult(
        trajectory=[step],
        collapsed=True,
        collapse_timestep=1,
        final_instability=2.0,
        seed=1,
        attack_cost=attack_cost,
    )


def test_attack_cost_penalty_changes_ordering():
    hi = _dummy_rollout(attack_cost=5.0)
    lo = _dummy_rollout(attack_cost=0.1)
    assert severity_score(hi) == severity_score(lo)
    fn = fitness_severity_minus_cost(attack_cost_weight=1.0)
    assert fn(lo) > fn(hi)


def test_phase_a_ignores_attack_cost_magnitude():
    a = _dummy_rollout(attack_cost=0.0)
    b = _dummy_rollout(attack_cost=99.0)
    assert fitness_phase_a(a) == fitness_phase_a(b)
