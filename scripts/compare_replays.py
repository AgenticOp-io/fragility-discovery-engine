"""Summarize differences between two replay JSON files (CLI / CI helper)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

COMPARE_KEYS = (
    "schema_version",
    "simulation_mode",
    "collapsed",
    "collapse_timestep",
    "attack_cost",
    "integral_instability",
    "mean_instability",
    "steps_recorded",
    "recovery_timestep",
    "recovery_latency_steps",
    "final_instability",
    "seed",
)


def main() -> None:
    p = argparse.ArgumentParser(description="Diff top-level replay metrics between two JSON artifacts.")
    p.add_argument("left", type=Path)
    p.add_argument("right", type=Path)
    p.add_argument("--out", type=Path, default=None, help="Write JSON diff to this path (stdout still prints).")
    args = p.parse_args()

    a = json.loads(args.left.read_text(encoding="utf-8"))
    b = json.loads(args.right.read_text(encoding="utf-8"))

    def pick(d: dict) -> dict:
        return {k: d.get(k) for k in COMPARE_KEYS}

    pa, pb = pick(a), pick(b)
    diff_keys = [k for k in COMPARE_KEYS if pa.get(k) != pb.get(k)]

    out = {
        "left_file": str(args.left),
        "right_file": str(args.right),
        "left": pa,
        "right": pb,
        "trajectory_lengths": (len(a.get("trajectory") or []), len(b.get("trajectory") or [])),
        "diff_keys": diff_keys,
    }
    text = json.dumps(out, indent=2)
    print(text)
    if args.out is not None:
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
