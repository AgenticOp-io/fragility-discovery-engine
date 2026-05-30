#!/usr/bin/env python3
"""Pin coupled fork GA Pareto search metrics (best_fitness, archive size, hypervolume)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fragility_engine.benchmarks.hypervolume import hypervolume_2d_attack_pareto

ROOT = Path(__file__).resolve().parents[1]
PIN_FILES = {
    "v1": ROOT / "tests" / "fixtures" / "benchmarks" / "coupled_fork_pareto_search_pins.json",
    "v2": ROOT / "tests" / "fixtures" / "benchmarks" / "coupled_fork_pareto_search_v2_pins.json",
}


def _measure(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema") != "pareto-front-v1":
        raise SystemExit(f"{path}: expected pareto-front-v1")
    arch = obj.get("archive") or []
    if not arch:
        raise SystemExit(f"{path}: empty archive")
    hv, ref_t, _nd = hypervolume_2d_attack_pareto(arch)
    return {
        "best_fitness": float(obj.get("best_fitness", 0)),
        "archive_points": len(arch),
        "hypervolume_reference": [ref_t[0], ref_t[1]],
        "expected_hypervolume": float(hv),
    }


def _check_one(pins_path: Path, *, write_pins: bool) -> None:
    pins = json.loads(pins_path.read_text(encoding="utf-8"))
    rel = pins.get("artifact_relpath")
    if not rel:
        raise SystemExit(f"{pins_path}: missing artifact_relpath")
    path = ROOT / rel
    if not path.is_file():
        print(f"missing artifact: {path}", file=sys.stderr)
        if "pareto_viewer" in rel:
            print("Run: python scripts/regenerate_coupled_fork_artifacts.py", file=sys.stderr)
        raise SystemExit(1)

    current = _measure(path)
    if write_pins:
        pins["expected"] = current
        pins_path.write_text(json.dumps(pins, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {pins_path.relative_to(ROOT)}")
        return

    expected = pins.get("expected") or {}
    errors: list[str] = []
    for key in ("best_fitness", "archive_points", "expected_hypervolume"):
        if key not in expected:
            errors.append(f"{pins_path.name}: missing expected.{key}")
            continue
        got = current[key]
        want = expected[key]
        if key == "archive_points":
            if int(got) != int(want):
                errors.append(f"{key}: got {got} want {want}")
        elif abs(float(got) - float(want)) > 1e-9:
            errors.append(f"{key}: got {got} want {want}")
    ref = expected.get("hypervolume_reference")
    if ref and current.get("hypervolume_reference"):
        for i, label in enumerate(("ref[0]", "ref[1]")):
            if abs(float(current["hypervolume_reference"][i]) - float(ref[i])) > 1e-9:
                errors.append(f"{label}: got {current['hypervolume_reference'][i]} want {ref[i]}")

    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        raise SystemExit(1)

    print(f"OK: {pins.get('bundle_id')} pins match {rel}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--tier",
        choices=("v1", "v2", "all"),
        default="all",
        help="Which pinned search budget to check (default: all).",
    )
    ap.add_argument(
        "--write-pins",
        action="store_true",
        help="Rewrite pins fixture from the tier artifact (after intentional GA change).",
    )
    args = ap.parse_args()

    tiers = ("v1", "v2") if args.tier == "all" else (args.tier,)
    for tier in tiers:
        path = PIN_FILES.get(tier)
        if path is None or not path.is_file():
            raise SystemExit(f"missing pins for tier {tier}: {path}")
        _check_one(path, write_pins=bool(args.write_pins))


if __name__ == "__main__":
    main()
