#!/usr/bin/env python3
"""Regenerate pinned replay JSON and print golden metrics for coupled_institution_rollout_v1."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coupled_institution.golden import run_coupled_institution_rollout_v1  # noqa: E402
from coupled_institution.golden import _load_fixture, _schedule_from_fixture  # noqa: E402
from coupled_institution.rollout import rollout_coupled  # noqa: E402
from coupled_institution.world import CoupledInstitutionWorld  # noqa: E402

ARTIFACTS = ROOT / "artifacts"


def main() -> None:
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
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    out = ARTIFACTS / "sample_coupled_replay.json"
    out.write_text(json.dumps(result.to_replay_dict(), indent=2), encoding="utf-8")
    snap = run_coupled_institution_rollout_v1()
    print(json.dumps({"artifact": str(out.relative_to(ROOT)), "metrics": snap}, indent=2))


if __name__ == "__main__":
    main()
