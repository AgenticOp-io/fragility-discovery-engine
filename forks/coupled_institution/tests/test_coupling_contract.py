"""Coupling contract + worth-it bar."""

from __future__ import annotations

from coupled_institution.rollout import rollout_coupled
from coupled_institution.types import ExogenousEvent
from coupled_institution.world import CoupledInstitutionWorld, CouplingContract
from coupled_institution.worth_it import demo_schedule, evaluate_worth_it


def test_default_contract_emits_channel_metrics() -> None:
    w = CoupledInstitutionWorld(coupling_strength=0.3)
    w.reset()
    row = w.step((ExogenousEvent("reserve_loss", 0.4),), __import__("numpy").random.default_rng(0))
    assert "coupling_contrib_to_panic" in row.metrics
    assert "coupling_contrib_to_overload" in row.metrics
    assert row.metrics["gain_overload_to_panic"] == 0.3


def test_asymmetric_gains_differ_from_symmetric() -> None:
    sched = [
        (ExogenousEvent("reserve_loss", 0.35),),
        (ExogenousEvent("rumor", 0.35),),
        (),
    ]
    sym = CoupledInstitutionWorld(coupling_strength=0.25)
    asym = CoupledInstitutionWorld(
        coupling_strength=0.25,
        contract=CouplingContract(gain_overload_to_panic=0.45, gain_panic_to_overload=0.05),
    )
    i_sym = rollout_coupled(sym, sched, seed=1).integral_instability
    i_asym = rollout_coupled(asym, sched, seed=1).integral_instability
    assert i_sym != i_asym


def test_lag1_differs_from_lag0() -> None:
    sched = demo_schedule(horizon=8, seed=3)
    lag0 = CoupledInstitutionWorld(coupling_strength=0.3, contract=CouplingContract(lag_steps=0))
    lag1 = CoupledInstitutionWorld(coupling_strength=0.3, contract=CouplingContract(lag_steps=1))
    assert rollout_coupled(lag0, sched, seed=9).integral_instability != rollout_coupled(
        lag1, sched, seed=9
    ).integral_instability


def test_worth_it_demo_schedule_passes() -> None:
    report = evaluate_worth_it(demo_schedule(), seed=7, coupling_strength=0.25)
    assert report.worth_it
    assert report.triad_worth_it
    assert report.tetra_worth_it
    assert abs(report.delta_vs_zero) > 0
    assert report.delta_vs_reversed > 0
    assert abs(report.triad_vs_twoscalar) > 0
    assert abs(report.tetra_vs_triad) > 0


def test_default_liquidity_off_preserves_two_scalar_path() -> None:
    """Liquidity/backlog metrics exist but channels default inactive."""
    w = CoupledInstitutionWorld(coupling_strength=0.3)
    w.reset()
    row = w.step((ExogenousEvent("reserve_loss", 0.4),), __import__("numpy").random.default_rng(0))
    assert row.metrics["liquidity"] == 1.0
    assert row.metrics["backlog"] == 0.05
    assert row.metrics["liquidity_channels_active"] == 0.0
    assert row.metrics["backlog_channels_active"] == 0.0
    assert row.metrics["coupling_contrib_to_liquidity"] == 0.0
    assert row.metrics["coupling_contrib_to_backlog"] == 0.0


def test_triad_drains_liquidity() -> None:
    from coupled_institution.world import triad_contract

    w = CoupledInstitutionWorld(coupling_strength=0.25, contract=triad_contract())
    sched = demo_schedule(horizon=8, seed=3)
    r = rollout_coupled(w, sched, seed=3)
    assert r.trajectory[-1].metrics["liquidity"] < 1.0
    assert r.trajectory[-1].metrics["liquidity_channels_active"] == 1.0
    assert len(r.trajectory[0].state_vector) == 6


def test_tetra_builds_backlog() -> None:
    from coupled_institution.world import tetra_contract

    w = CoupledInstitutionWorld(coupling_strength=0.25, contract=tetra_contract())
    sched = demo_schedule(horizon=8, seed=3)
    r = rollout_coupled(w, sched, seed=3)
    assert r.trajectory[-1].metrics["backlog"] > 0.05
    assert r.trajectory[-1].metrics["backlog_channels_active"] == 1.0
