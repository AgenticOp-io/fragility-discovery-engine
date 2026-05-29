"""Smoke: alternating co-evolution on coupled_institution fork (optional install)."""

from __future__ import annotations

import pytest

pytest.importorskip("coupled_institution")

from coupled_institution.world import CoupledInstitutionWorld

from fragility_engine.coevolution.coupled_institution import alternating_coevolution_coupled_institution


def test_alternating_coevolution_coupled_institution_smoke() -> None:
    template = CoupledInstitutionWorld(coupling_strength=0.3, max_steps=24)
    summary = alternating_coevolution_coupled_institution(
        template,
        horizon=6,
        rounds=1,
        attacker_generations=2,
        attacker_population=4,
        defender_generations=2,
        defender_population=4,
        seed=99,
    )
    assert summary.simulation_mode == "coupled_institution_v1"
    assert len(summary.rounds) == 1
    assert summary.last_rollout is not None
