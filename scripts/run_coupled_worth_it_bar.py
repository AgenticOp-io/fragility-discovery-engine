#!/usr/bin/env python3
"""Run coupled mega-institution worth-it bar; write JSON under fork artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORK_SRC = ROOT / "forks" / "coupled_institution" / "src"
sys.path.insert(0, str(FORK_SRC))

from coupled_institution.golden import _load_fixture, _schedule_from_fixture  # noqa: E402
from coupled_institution.worth_it import demo_schedule, evaluate_worth_it  # noqa: E402

OUT = ROOT / "forks" / "coupled_institution" / "artifacts" / "worth_it_bar.json"


def main() -> int:
    raw = _load_fixture()
    pinned = evaluate_worth_it(
        _schedule_from_fixture(raw),
        seed=int(raw["rollout_seed"]),
        coupling_strength=float(raw["coupling_strength"]),
    )
    demo = evaluate_worth_it(demo_schedule(), seed=7, coupling_strength=0.25)
    payload = {
        "kind": "coupled-worth-it-bar-bundle-v2",
        "pinned_golden_schedule": pinned.to_dict(),
        "demo_frontloaded_schedule": demo.to_dict(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    ok = bool(demo.worth_it and demo.triad_worth_it and demo.tetra_worth_it)
    if not ok:
        print(
            "worth-it bar: FAIL "
            f"(two-scalar={demo.worth_it}, triad={demo.triad_worth_it}, tetra={demo.tetra_worth_it})",
            file=sys.stderr,
        )
        return 1
    print("worth-it bar: PASS (demo two-scalar + triad + tetra)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
