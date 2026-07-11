#!/usr/bin/env python3
"""Validate coupled_institution fork golden bundle (non-charter; research fork only)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORK_SRC = ROOT / "forks" / "coupled_institution" / "src"
if str(FORK_SRC) not in sys.path:
    sys.path.insert(0, str(FORK_SRC))

from coupled_institution.golden import (  # noqa: E402
    BUNDLE_ID,
    GOLDEN_METRICS,
    run_coupled_institution_rollout_v1,
)

TOL = 1e-9


def _check_close(name: str, got: float, want: float) -> None:
    if abs(got - want) > TOL:
        raise SystemExit(f"{name}: got {got!r} want {want!r}")


def main() -> None:
    snap = run_coupled_institution_rollout_v1()
    if snap["bundle_id"] != BUNDLE_ID:
        raise SystemExit(f"bundle_id mismatch: {snap['bundle_id']!r}")
    _check_close(
        "integral_instability",
        float(snap["integral_instability"]),
        float(GOLDEN_METRICS["integral_instability"]),
    )
    _check_close("attack_cost", float(snap["attack_cost"]), float(GOLDEN_METRICS["attack_cost"]))
    if bool(snap["collapsed"]) != bool(GOLDEN_METRICS["collapsed"]):
        raise SystemExit("collapsed mismatch")
    if snap["collapse_timestep"] != GOLDEN_METRICS["collapse_timestep"]:
        raise SystemExit("collapse_timestep mismatch")
    sample = ROOT / "forks" / "coupled_institution" / "artifacts" / "sample_coupled_replay.json"
    if not sample.is_file():
        raise SystemExit(f"missing sample replay: {sample}")
    data = json.loads(sample.read_text(encoding="utf-8"))
    if data.get("schema_version") != "coupled-fork-0.4.0":
        raise SystemExit("sample_coupled_replay.json schema_version mismatch")
    print(json.dumps({"ok": True, "bundle_id": BUNDLE_ID, "snap": snap}, indent=2))


if __name__ == "__main__":
    main()
