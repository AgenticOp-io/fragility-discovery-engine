"""Phase O — robustness sweeps via named stretch presets (capped rollout budget)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from fragility_engine.benchmarks.stretch_presets import STRETCH_PRESETS, estimate_rollout_budget

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser(description="Run fragility_robustness_sweep with a stretch preset.")
    ap.add_argument(
        "--preset",
        choices=tuple(STRETCH_PRESETS.keys()),
        default="small",
        help="small|medium|large grid sizes (see SCALE_AND_LIMITS.md).",
    )
    ap.add_argument(
        "--mode",
        choices=("ensemble", "physics_2d", "ga_budget_2d"),
        default="ensemble",
    )
    ap.add_argument("--dry-run", action="store_true", help="Print argv only.")
    ap.add_argument("--json", action="store_true", help="Pass --json to underlying sweep.")
    args = ap.parse_args()

    preset = STRETCH_PRESETS[str(args.preset)]
    cap = int(preset["max_rollout_budget"])
    est = estimate_rollout_budget(preset, mode=str(args.mode))
    if est > cap:
        print(
            f"warning: estimated rollouts ~{est} exceeds preset cap {cap}; reduce preset or mode",
            file=sys.stderr,
        )

    cmd = [sys.executable, str(ROOT / "scripts" / "fragility_robustness_sweep.py")]
    cmd.extend(["--graph-seeds", str(preset["graph_seeds"])])
    if args.json:
        cmd.append("--json")

    if args.mode == "ensemble":
        pass
    elif args.mode == "physics_2d":
        cmd.extend(
            [
                "--sweep-param",
                "er_p",
                "--sweep-values",
                str(preset.get("sweep_values", "0.10,0.14,0.18")),
                "--sweep-param-2",
                "base_panic",
                "--sweep-values-2",
                str(preset.get("sweep_values_2", "0.05,0.10,0.15")),
            ]
        )
    else:
        cmd.extend(
            [
                "--ga-budget-2d",
                "--ga-generations-values",
                str(preset.get("ga_generations_values", "2,4")),
                "--ga-population-values",
                str(preset.get("ga_population_values", "8,12")),
            ]
        )

    meta = {
        "schema": "fragility-robustness-stretch-v1",
        "preset": args.preset,
        "mode": args.mode,
        "max_rollout_budget": cap,
        "estimated_rollouts": est,
        "argv": cmd,
    }
    if args.dry_run:
        print(json.dumps(meta, indent=2))
        return

    proc = subprocess.run(cmd, cwd=str(ROOT), check=False)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)
    print(json.dumps({"stretch_meta": meta}, indent=2))


if __name__ == "__main__":
    main()
