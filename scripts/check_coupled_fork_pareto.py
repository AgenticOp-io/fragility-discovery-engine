#!/usr/bin/env python3
"""Pin coupled fork GA Pareto search metrics (best_fitness, archive size, hypervolume)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fragility_engine.benchmarks.hypervolume import hypervolume_2d_min, nondominated_points_min

ROOT = Path(__file__).resolve().parents[1]
PINS_PATH = ROOT / "tests" / "fixtures" / "benchmarks" / "coupled_fork_pareto_search_pins.json"


def _load_pins() -> dict:
    if not PINS_PATH.is_file():
        raise SystemExit(f"missing pins fixture: {PINS_PATH}")
    return json.loads(PINS_PATH.read_text(encoding="utf-8"))


def _measure(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema") != "pareto-front-v1":
        raise SystemExit(f"{path}: expected pareto-front-v1")
    arch = obj.get("archive") or []
    pts = [(float(e["severity"]), float(e["attack_cost"])) for e in arch if isinstance(e, dict)]
    nd = nondominated_points_min(pts)
    if not nd:
        raise SystemExit(f"{path}: empty nondominated set")
    ref = [
        max(s for s, _ in nd) * 1.15 + 0.01,
        max(a for _, a in nd) * 1.15 + 0.01,
    ]
    hv = hypervolume_2d_min(nd, (float(ref[0]), float(ref[1])))
    return {
        "best_fitness": float(obj.get("best_fitness", 0)),
        "archive_points": len(arch),
        "hypervolume_reference": ref,
        "expected_hypervolume": float(hv),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--write-pins",
        action="store_true",
        help="Rewrite pins fixture from the bundled pareto sample (after intentional GA change).",
    )
    args = ap.parse_args()

    pins = _load_pins()
    rel = pins.get("artifact_relpath") or "artifacts/pareto_viewer/sample_pareto_coupled_institution.json"
    path = ROOT / rel
    if not path.is_file():
        print(f"missing artifact: {path}", file=sys.stderr)
        print("Run: python scripts/regenerate_coupled_fork_artifacts.py", file=sys.stderr)
        raise SystemExit(1)

    current = _measure(path)
    if args.write_pins:
        pins["expected"] = current
        PINS_PATH.write_text(json.dumps(pins, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {PINS_PATH.relative_to(ROOT)}")
        return

    expected = pins.get("expected") or {}
    errors: list[str] = []
    for key in ("best_fitness", "archive_points", "expected_hypervolume"):
        if key not in expected:
            errors.append(f"pins missing expected.{key}")
            continue
        got = current[key]
        want = expected[key]
        if key == "archive_points":
            if int(got) != int(want):
                errors.append(f"{key}: got {got} want {want}")
        else:
            if abs(float(got) - float(want)) > 1e-9:
                errors.append(f"{key}: got {got} want {want}")
    ref = expected.get("hypervolume_reference")
    if ref and current.get("hypervolume_reference"):
        for i, label in enumerate(("ref[0]", "ref[1]")):
            if abs(float(current["hypervolume_reference"][i]) - float(ref[i])) > 1e-9:
                errors.append(f"{label}: got {current['hypervolume_reference'][i]} want {ref[i]}")

    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        print("Re-run export or update pins with --write-pins if intentional.", file=sys.stderr)
        raise SystemExit(1)

    print(f"OK: {pins.get('bundle_id', 'coupled_institution_pareto_search_v1')} pins match {rel}")


if __name__ == "__main__":
    main()
