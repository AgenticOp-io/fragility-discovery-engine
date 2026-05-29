#!/usr/bin/env python3
"""Sweep coupling_strength on pinned schedule; write JSON for charts / narration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coupled_institution.golden import _load_fixture, _schedule_from_fixture  # noqa: E402
from coupled_institution.rollout import rollout_coupled  # noqa: E402
from coupled_institution.world import CoupledInstitutionWorld  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="Coupling strength sweep (pinned schedule).")
    p.add_argument(
        "--strengths",
        default="0,0.1,0.2,0.3,0.4,0.5,0.6",
        help="Comma-separated coupling_strength values.",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=ROOT / "artifacts" / "coupling_strength_sweep.json",
    )
    args = p.parse_args()

    raw = _load_fixture()
    schedule = _schedule_from_fixture(raw)
    seed = int(raw["rollout_seed"])
    strengths = [float(x.strip()) for x in str(args.strengths).split(",") if x.strip()]

    rows: list[dict] = []
    for c in strengths:
        world = CoupledInstitutionWorld(coupling_strength=c, max_steps=32)
        result = rollout_coupled(world, schedule, seed=seed)
        rows.append(
            {
                "coupling_strength": c,
                "integral_instability": float(result.integral_instability),
                "attack_cost": float(result.attack_cost),
                "collapsed": bool(result.collapsed),
                "collapse_timestep": result.collapse_timestep,
                "final_instability": float(result.final_instability),
            }
        )

    payload = {
        "schema": "coupled-institution-coupling-sweep-v1",
        "fixture": "tests/fixtures/pinned_rollout_schedule.json",
        "rollout_seed": seed,
        "rows": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "n": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
