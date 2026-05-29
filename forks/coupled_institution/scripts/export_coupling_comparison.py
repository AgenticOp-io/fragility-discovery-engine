#!/usr/bin/env python3
"""Compare two coupling_strength values on the pinned schedule (fork attribution-style JSON)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coupled_institution.golden import _load_fixture, _schedule_from_fixture  # noqa: E402
from coupled_institution.rollout import rollout_coupled  # noqa: E402
from coupled_institution.world import CoupledInstitutionWorld  # noqa: E402

SCHEMA = "coupled-institution-coupling-comparison-v1"


def _run(coupling: float, schedule: list, seed: int) -> dict[str, Any]:
    world = CoupledInstitutionWorld(coupling_strength=coupling, max_steps=32)
    result = rollout_coupled(world, schedule, seed=seed)
    return {
        "coupling_strength": coupling,
        "integral_instability": float(result.integral_instability),
        "attack_cost": float(result.attack_cost),
        "collapsed": bool(result.collapsed),
        "collapse_timestep": result.collapse_timestep,
        "final_instability": float(result.final_instability),
        "simulation_mode": result.simulation_mode,
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Low vs high coupling on pinned schedule.")
    p.add_argument("--low", type=float, default=0.1)
    p.add_argument("--high", type=float, default=0.5)
    p.add_argument(
        "--out",
        type=Path,
        default=ROOT / "artifacts" / "sample_coupling_comparison.json",
    )
    args = p.parse_args()

    raw = _load_fixture()
    schedule = _schedule_from_fixture(raw)
    seed = int(raw["rollout_seed"])
    baseline = _run(float(args.low), schedule, seed)
    variant = _run(float(args.high), schedule, seed)
    payload = {
        "schema": SCHEMA,
        "fixture": "tests/fixtures/pinned_rollout_schedule.json",
        "rollout_seed": seed,
        "intervention": f"coupling_strength {args.low} -> {args.high}",
        "baseline": baseline,
        "variant": variant,
        "delta_integral_instability": float(baseline["integral_instability"])
        - float(variant["integral_instability"]),
        "delta_attack_cost": float(baseline["attack_cost"]) - float(variant["attack_cost"]),
        "interpretation_hint": (
            "Higher coupling_strength feeds panic into overload and overload into panic each step."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "schema": SCHEMA}, indent=2))


if __name__ == "__main__":
    main()
