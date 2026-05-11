"""Summarize differences between two replay JSON files (CLI / CI helper)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _price_metric_note(mode: str | None) -> str:
    """Replay ``metrics.price`` is peg ratio (aggregate) or min headroom (resource cascade); same JSON field."""

    if mode == "resource_cascade":
        return "metrics.price encodes min layer headroom [0,1] (not a peg)."
    if mode == "service_backlog":
        return "metrics.price encodes service slack headroom S in [0,1] (not a peg)."
    if mode == "network":
        return "metrics.price encodes network summary headroom proxy (see trajectory step metrics)."
    return "metrics.price encodes peg ratio (aggregate)."


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
        "metric_notes": {
            "left_price_metric": _price_metric_note(pa.get("simulation_mode")),
            "right_price_metric": _price_metric_note(pb.get("simulation_mode")),
        },
    }
    text = json.dumps(out, indent=2)
    print(text)
    if args.out is not None:
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
