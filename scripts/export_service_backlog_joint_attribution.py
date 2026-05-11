"""Emit attribution-merge-v1 for ServiceBacklogWorld: remove_steps + second branch (shared baseline)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import (
    counterfactual_remove_steps_with_rollouts,
    counterfactual_service_backlog_initial_backlog_shift_with_rollouts,
    counterfactual_service_backlog_process_rate_shift_with_rollouts,
)
from fragility_engine.explain.merge_attribution import merge_heterogeneous_counterfactuals
from fragility_engine.runner import rollout_service_backlog
from fragility_engine.world.service_backlog import ServiceBacklogWorld


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Merge two service-backlog counterfactual bundles that share the same baseline rollout "
            "(genome + seed + baseline initial_backlog): shock removal vs backlog shift or process_rate shift."
        ),
    )
    ap.add_argument("--out", type=Path, default=Path("service_backlog_attribution_merge.json"))
    ap.add_argument("--seed", type=int, default=70707, help="Rollout seed (shared baseline).")
    ap.add_argument("--genome-seed", type=int, default=80808)
    ap.add_argument("--horizon", type=int, default=14)
    ap.add_argument("--max-steps", type=int, default=28)
    ap.add_argument("--initial-backlog", type=float, default=0.07, help="Baseline backlog at reset.")
    ap.add_argument(
        "--second-branch",
        choices=("initial_backlog_shift", "process_rate_shift"),
        default="initial_backlog_shift",
        help="Second merged branch after remove_steps (same baseline genome/seed/backlog).",
    )
    ap.add_argument(
        "--variant-initial-backlog",
        type=float,
        default=0.02,
        help="[second-branch initial_backlog_shift] counterfactual reset backlog.",
    )
    ap.add_argument(
        "--variant-process-rate",
        type=float,
        default=None,
        help="[second-branch process_rate_shift] counterfactual process_rate (baseline = template default).",
    )
    ap.add_argument("--remove", type=str, default="0", help="Comma-separated shock rows to zero (remove_steps branch).")
    ap.add_argument(
        "--continue-after-collapse",
        action="store_true",
        help="Forward rollouts after collapse when applicable.",
    )
    args = ap.parse_args()

    if args.second_branch == "process_rate_shift" and args.variant_process_rate is None:
        raise SystemExit("--variant-process-rate required when --second-branch process_rate_shift.")

    remove_ts = [int(x.strip()) for x in args.remove.split(",") if x.strip() != ""]
    rng = np.random.default_rng(int(args.genome_seed))
    genome = rng.uniform(size=(int(args.horizon), 2))
    cont = bool(args.continue_after_collapse)
    ms = max(int(args.horizon), int(args.max_steps))
    template = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=ms)

    def evaluator(g: np.ndarray, s: int):
        return rollout_service_backlog(
            template,
            g,
            seed=s,
            initial_backlog=float(args.initial_backlog),
            continue_after_collapse=cont,
        )

    bundle_remove, _, _ = counterfactual_remove_steps_with_rollouts(
        genome, evaluator, remove_timesteps=remove_ts, base_seed=int(args.seed)
    )
    if args.second_branch == "initial_backlog_shift":
        bundle_second, _, _ = counterfactual_service_backlog_initial_backlog_shift_with_rollouts(
            genome,
            template,
            baseline_initial_backlog=float(args.initial_backlog),
            variant_initial_backlog=float(args.variant_initial_backlog),
            rollout_seed=int(args.seed),
            continue_after_collapse=cont,
        )
    else:
        bundle_second, _, _ = counterfactual_service_backlog_process_rate_shift_with_rollouts(
            genome,
            template,
            variant_process_rate=float(args.variant_process_rate),
            rollout_seed=int(args.seed),
            initial_backlog=float(args.initial_backlog),
            continue_after_collapse=cont,
        )

    merged = merge_heterogeneous_counterfactuals([bundle_remove, bundle_second], strict_baseline=True)
    meta: dict[str, object] = {
        "cli": "export_service_backlog_joint_attribution",
        "domain": "service_backlog",
        "second_branch": str(args.second_branch),
        "baseline_initial_backlog": float(args.initial_backlog),
        "removed_timesteps_branch": remove_ts,
        "rollout_seed": int(args.seed),
        "genome_seed": int(args.genome_seed),
    }
    if args.second_branch == "initial_backlog_shift":
        meta["variant_initial_backlog_branch"] = float(args.variant_initial_backlog)
    else:
        meta["variant_process_rate_branch"] = float(args.variant_process_rate)
        meta["baseline_process_rate_template"] = float(template.process_rate)
    merged["meta"] = meta
    args.out.write_text(json.dumps(merged, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
