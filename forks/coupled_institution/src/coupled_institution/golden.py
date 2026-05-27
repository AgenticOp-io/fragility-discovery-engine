"""Pinned rollout bundle for fork CI (not main-engine benchmark suite)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from coupled_institution.rollout import rollout_coupled
from coupled_institution.types import ExogenousEvent
from coupled_institution.world import CoupledInstitutionWorld

BUNDLE_ID = "coupled_institution_rollout_v1"
_FIXTURE = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "pinned_rollout_schedule.json"

GOLDEN_METRICS: dict[str, float | bool] = {
    "integral_instability": 6.80391937052433,
    "attack_cost": 2.0949999999999998,
    "collapsed": True,
    "collapse_timestep": 5.0,
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
    """Deterministic pinned rollout; metrics checked in ``test_golden_bundle``."""

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
    }
