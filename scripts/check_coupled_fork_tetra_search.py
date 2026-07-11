#!/usr/bin/env python3
"""Pin tetra-contract GA + MC search summaries for the coupled mega-institution fork."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = ROOT / "tests" / "fixtures" / "benchmarks" / "coupled_fork_tetra_search_pins.json"
GA = ROOT / "forks" / "coupled_institution" / "scripts" / "run_coupled_ga_demo.py"


def _run_search(spec: dict) -> dict:
    method = spec["method"]
    cmd = [
        sys.executable,
        str(GA),
        "--method",
        method,
        "--contract",
        "tetra",
        "--coupling",
        str(spec["coupling_strength"]),
        "--horizon",
        str(spec["horizon"]),
        "--seed",
        str(spec["seed"]),
    ]
    if method == "ga":
        cmd.extend(
            [
                "--generations",
                str(spec["generations"]),
                "--population-size",
                str(spec["population_size"]),
            ]
        )
    else:
        cmd.extend(["--samples", str(spec["samples"])])
    proc = subprocess.run(cmd, cwd=str(ROOT), check=True, capture_output=True, text=True)
    return json.loads(proc.stdout)


def _measure_all(pins: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for key, spec in pins["searches"].items():
        payload = _run_search(spec)
        out[key] = {
            "best_fitness": float(payload["best_fitness"]),
            "integral_instability": float(payload["integral_instability"]),
            "collapsed": bool(payload["collapsed"]),
            "attack_cost": float(payload["attack_cost"]),
            "coupling_profile": payload.get("coupling_profile"),
        }
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--write-pins", action="store_true")
    args = p.parse_args()

    if not PINS.is_file():
        # bootstrap skeleton then measure
        skeleton = {
            "bundle_id": "coupled_institution_tetra_search_v1",
            "searches": {
                "ga": {
                    "method": "ga",
                    "seed": 62001,
                    "generations": 2,
                    "population_size": 8,
                    "horizon": 10,
                    "coupling_strength": 0.25,
                },
                "mc": {
                    "method": "mc",
                    "seed": 62002,
                    "samples": 24,
                    "horizon": 10,
                    "coupling_strength": 0.25,
                },
            },
            "expected": {},
            "note": "Re-pin via scripts/check_coupled_fork_tetra_search.py --write-pins after intentional search/physics changes.",
        }
        PINS.parent.mkdir(parents=True, exist_ok=True)
        PINS.write_text(json.dumps(skeleton, indent=2) + "\n", encoding="utf-8")
        pins = skeleton
    else:
        pins = json.loads(PINS.read_text(encoding="utf-8"))

    current = _measure_all(pins)
    if args.write_pins or not pins.get("expected"):
        pins["expected"] = current
        PINS.write_text(json.dumps(pins, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"wrote": str(PINS.relative_to(ROOT)), "expected": current}, indent=2))
        return 0

    expected = pins["expected"]
    errors: list[str] = []
    for key, got in current.items():
        want = expected.get(key) or {}
        for field in ("best_fitness", "integral_instability", "attack_cost"):
            if abs(float(got[field]) - float(want[field])) > 1e-9:
                errors.append(f"{key}.{field}: got {got[field]} want {want[field]}")
        if bool(got["collapsed"]) != bool(want["collapsed"]):
            errors.append(f"{key}.collapsed: got {got['collapsed']} want {want['collapsed']}")
    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, "bundle_id": pins.get("bundle_id"), "measured": current}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
