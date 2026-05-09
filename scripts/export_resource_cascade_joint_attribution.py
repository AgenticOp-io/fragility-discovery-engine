"""Emit attribution-merge-v1 for ResourceCascadeWorld: remove_steps + second branch (shared baseline)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import (
    counterfactual_remove_steps_with_rollouts,
    counterfactual_resource_cascade_cascade_coupling_shift_with_rollouts,
    counterfactual_resource_cascade_initial_overload_shift_with_rollouts,
)
from fragility_engine.explain.merge_attribution import merge_heterogeneous_counterfactuals
from fragility_engine.runner import rollout_resource_cascade
from fragility_engine.world.resource_cascade import ResourceCascadeWorld


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Merge two resource-cascade counterfactual bundles that share the same baseline rollout "
            "(genome + seed + baseline initial_overload): shock removal vs overload shift or cascade coupling shift."
        ),
    )
    ap.add_argument("--out", type=Path, default=Path("resource_cascade_attribution_merge.json"))
    ap.add_argument("--seed", type=int, default=70707, help="Rollout seed (shared baseline).")
    ap.add_argument("--genome-seed", type=int, default=80808)
    ap.add_argument("--horizon", type=int, default=14)
    ap.add_argument("--max-steps", type=int, default=28)
    ap.add_argument("--initial-overload", type=float, default=0.07, help="Baseline overload at reset [0,1].")
    ap.add_argument(
        "--second-branch",
        choices=("initial_overload_shift", "cascade_coupling_shift"),
        default="initial_overload_shift",
        help="Second merged branch after remove_steps (same baseline genome/seed/overload).",
    )
    ap.add_argument(
        "--variant-initial-overload",
        type=float,
        default=0.12,
        help="[second-branch initial_overload_shift] counterfactual reset overload [0,1].",
    )
    ap.add_argument(
        "--variant-cascade-coupling",
        type=float,
        default=None,
        help="[second-branch cascade_coupling_shift] counterfactual cascade_coupling (baseline = template default).",
    )
    ap.add_argument("--remove", type=str, default="0", help="Comma-separated shock rows to zero (remove_steps branch).")
    ap.add_argument(
        "--continue-after-collapse",
        action="store_true",
        help="Forward rollouts after collapse when applicable.",
    )
    args = ap.parse_args()

    if args.second_branch == "cascade_coupling_shift" and args.variant_cascade_coupling is None:
        raise SystemExit("--variant-cascade-coupling required when --second-branch cascade_coupling_shift.")

    remove_ts = [int(x.strip()) for x in args.remove.split(",") if x.strip() != ""]
    rng = np.random.default_rng(int(args.genome_seed))
    genome = rng.uniform(size=(int(args.horizon), 2))
    cont = bool(args.continue_after_collapse)
    ms = max(int(args.horizon), int(args.max_steps))
    template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=ms)

    def evaluator(g: np.ndarray, s: int):
        return rollout_resource_cascade(
            template,
            g,
            seed=s,
            initial_overload=float(args.initial_overload),
            continue_after_collapse=cont,
        )

    bundle_remove, _, _ = counterfactual_remove_steps_with_rollouts(
        genome, evaluator, remove_timesteps=remove_ts, base_seed=int(args.seed)
    )
    if args.second_branch == "initial_overload_shift":
        bundle_second, _, _ = counterfactual_resource_cascade_initial_overload_shift_with_rollouts(
            genome,
            template,
            baseline_initial_overload=float(args.initial_overload),
            variant_initial_overload=float(args.variant_initial_overload),
            rollout_seed=int(args.seed),
            continue_after_collapse=cont,
        )
    else:
        bundle_second, _, _ = counterfactual_resource_cascade_cascade_coupling_shift_with_rollouts(
            genome,
            template,
            variant_cascade_coupling=float(args.variant_cascade_coupling),
            rollout_seed=int(args.seed),
            initial_overload=float(args.initial_overload),
            continue_after_collapse=cont,
        )

    merged = merge_heterogeneous_counterfactuals([bundle_remove, bundle_second], strict_baseline=True)
    meta: dict[str, object] = {
        "cli": "export_resource_cascade_joint_attribution",
        "domain": "resource_cascade",
        "second_branch": str(args.second_branch),
        "baseline_initial_overload": float(args.initial_overload),
        "removed_timesteps_branch": remove_ts,
        "rollout_seed": int(args.seed),
        "genome_seed": int(args.genome_seed),
    }
    if args.second_branch == "initial_overload_shift":
        meta["variant_initial_overload_branch"] = float(args.variant_initial_overload)
    else:
        meta["variant_cascade_coupling_branch"] = float(args.variant_cascade_coupling)
        meta["baseline_cascade_coupling_template"] = float(template.cascade_coupling)
    merged["meta"] = meta
    args.out.write_text(json.dumps(merged, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
