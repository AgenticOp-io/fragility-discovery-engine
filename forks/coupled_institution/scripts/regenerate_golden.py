#!/usr/bin/env python3
"""Regenerate pinned replay JSON (default + tetra) and print golden metrics."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coupled_institution.factory import coupling_profile_label  # noqa: E402
from coupled_institution.golden import (  # noqa: E402
    run_coupled_institution_rollout_v1,
    run_coupled_institution_tetra_rollout_v1,
    _load_fixture,
    _schedule_from_fixture,
)
from coupled_institution.rollout import rollout_coupled  # noqa: E402
from coupled_institution.world import CoupledInstitutionWorld, tetra_contract  # noqa: E402

ARTIFACTS = ROOT / "artifacts"


def main() -> None:
    raw = _load_fixture()
    sched = _schedule_from_fixture(raw)
    seed = int(raw["rollout_seed"])
    coupling = float(raw["coupling_strength"])

    default_world = CoupledInstitutionWorld(coupling_strength=coupling, max_steps=32)
    default_result = rollout_coupled(default_world, sched, seed=seed)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    out = ARTIFACTS / "sample_coupled_replay.json"
    replay = default_result.to_replay_dict()
    replay["coupling_profile"] = coupling_profile_label("default")
    out.write_text(json.dumps(replay, indent=2), encoding="utf-8")

    tetra_world = CoupledInstitutionWorld(
        coupling_strength=coupling, max_steps=32, contract=tetra_contract()
    )
    tetra_result = rollout_coupled(tetra_world, sched, seed=seed)
    tetra_replay = tetra_result.to_replay_dict()
    tetra_replay["coupling_profile"] = coupling_profile_label("tetra")
    tetra_out = ARTIFACTS / "sample_coupled_tetra_replay.json"
    tetra_out.write_text(json.dumps(tetra_replay, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "default": {"artifact": str(out.relative_to(ROOT)), "metrics": run_coupled_institution_rollout_v1()},
                "tetra": {
                    "artifact": str(tetra_out.relative_to(ROOT)),
                    "metrics": run_coupled_institution_tetra_rollout_v1(),
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
