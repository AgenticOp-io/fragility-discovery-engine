"""Tests for Fragility Evidence Language conventions."""

from fragility_engine.fel import (
    FEL_VERSION,
    attack_pareto_dominates,
    delta_counterfactual,
    delta_path_forward,
    to_min_objectives,
)
from fragility_engine.fel.conventions import (
    apply_delta_counterfactual_to_rollouts,
    apply_delta_path_to_rollouts,
    fel_laws_summary,
)


class _FakeRollout:
    def __init__(self, integral_instability: float, attack_cost: float):
        self.integral_instability = integral_instability
        self.attack_cost = attack_cost
        self.final_instability = integral_instability
        self.collapsed = False
        self.collapse_timestep = None


def test_fel_version():
    assert FEL_VERSION == "fel-v0.1"


def test_delta_counterfactual_sign():
    # baseline worse (higher instability) => positive delta => variant improved
    assert delta_counterfactual(10.0, 7.0) == 3.0
    assert delta_counterfactual(5.0, 8.0) == -3.0


def test_delta_path_forward_sign():
    # successor higher => positive forward step
    assert delta_path_forward(3.0, 5.0) == 2.0
    assert delta_path_forward(5.0, 3.0) == -2.0


def test_counterfactual_and_path_opposite_on_same_pair():
    base, var = _FakeRollout(10.0, 4.0), _FakeRollout(8.0, 5.0)
    cf = apply_delta_counterfactual_to_rollouts(base, var)
    path = apply_delta_path_to_rollouts(base, var)
    assert cf["delta_integral_instability"] == 2.0
    assert path["delta_integral_instability"] == -2.0
    assert cf["delta_attack_cost"] == -1.0
    assert path["delta_attack_cost"] == 1.0


def test_attack_pareto_dominance():
    assert attack_pareto_dominates(severity_a=5.0, cost_a=2.0, severity_b=4.0, cost_b=3.0)
    assert not attack_pareto_dominates(severity_a=5.0, cost_a=3.0, severity_b=4.0, cost_b=2.0)
    assert not attack_pareto_dominates(severity_a=4.0, cost_a=2.0, severity_b=4.0, cost_b=2.0)


def test_to_min_objectives():
    assert to_min_objectives(3.5, 1.2) == (-3.5, 1.2)


def test_fel_laws_summary_keys():
    laws = fel_laws_summary()
    assert "determinism" in laws
    assert "delta_counterfactual" in laws
    assert "delta_path_forward" in laws
