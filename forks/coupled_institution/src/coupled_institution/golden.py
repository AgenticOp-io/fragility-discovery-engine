"""Pinned rollout bundles for fork CI (not main-engine benchmark suite)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from coupled_institution.rollout import rollout_coupled
from coupled_institution.types import ExogenousEvent
from coupled_institution.world import CoupledInstitutionWorld, tetra_contract

BUNDLE_ID = "coupled_institution_rollout_v1"
BUNDLE_ID_TETRA = "coupled_institution_tetra_rollout_v1"
_FIXTURE = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "pinned_rollout_schedule.json"

GOLDEN_METRICS: dict[str, float | bool] = {
    "integral_instability": 6.80391937052433,
    "attack_cost": 2.0949999999999998,
    "collapsed": True,
    "collapse_timestep": 5.0,
}

GOLDEN_METRICS_TETRA: dict[str, float | bool] = {
    "integral_instability": 9.16930598124866,
    "attack_cost": 2.0949999999999998,
    "collapsed": True,
    "collapse_timestep": 3.0,
    "final_liquidity": 0.0,
    "final_backlog": 2.0,
}


def _load_fixture() -> dict[str, Any]:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def _schedule_from_fixture(raw: dict[str, Any]) -> list[tuple[ExogenousEvent, ...]]:
    out: list[tuple[ExogenousEvent, ...]] = []
    for step in raw["schedule"]:
        events: list[ExogenousEvent] = []
        for ev in step:
            events.append(ExogenousEvent(str(ev["kind"]), float(ev["magnitude"])))
        out.append(tuple(events))
    return out


def run_coupled_institution_rollout_v1() -> dict[str, Any]:
    """Deterministic pinned rollout (default two-scalar contract)."""

    raw = _load_fixture()
    world = CoupledInstitutionWorld(
        coupling_strength=float(raw["coupling_strength"]),
        max_steps=32,
    )
    result = rollout_coupled(
        world,
        _schedule_from_fixture(raw),
        seed=int(raw["rollout_seed"]),
    )
    return {
        "bundle_id": BUNDLE_ID,
        "integral_instability": float(result.integral_instability),
        "attack_cost": float(result.attack_cost),
        "collapsed": bool(result.collapsed),
        "collapse_timestep": result.collapse_timestep,
        "simulation_mode": result.simulation_mode,
        "steps_recorded": len(result.trajectory),
        "coupling_profile": "two_scalar",
    }


def run_coupled_institution_tetra_rollout_v1() -> dict[str, Any]:
    """Same pinned schedule under ``tetra_contract()`` (liquidity + backlog)."""

    raw = _load_fixture()
    world = CoupledInstitutionWorld(
        coupling_strength=float(raw["coupling_strength"]),
        max_steps=32,
        contract=tetra_contract(),
    )
    result = rollout_coupled(
        world,
        _schedule_from_fixture(raw),
        seed=int(raw["rollout_seed"]),
    )
    last = result.trajectory[-1].metrics if result.trajectory else {}
    return {
        "bundle_id": BUNDLE_ID_TETRA,
        "integral_instability": float(result.integral_instability),
        "attack_cost": float(result.attack_cost),
        "collapsed": bool(result.collapsed),
        "collapse_timestep": result.collapse_timestep,
        "simulation_mode": result.simulation_mode,
        "steps_recorded": len(result.trajectory),
        "final_liquidity": float(last.get("liquidity", 0.0)),
        "final_backlog": float(last.get("backlog", 0.0)),
        "coupling_profile": "backlog_tetra",
    }
