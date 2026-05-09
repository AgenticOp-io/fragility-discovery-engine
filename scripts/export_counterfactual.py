"""Export a counterfactual attribution bundle as JSON (pinned seeds)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import (
    counterfactual_bundle_to_jsonable,
    counterfactual_remove_steps_with_rollouts,
)
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_stablecoin, rollout_to_replay_dict
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    ap = argparse.ArgumentParser(description="Export counterfactual JSON (drop shock timesteps, same seed).")
    ap.add_argument("--out", type=Path, default=Path("counterfactual.json"))
    ap.add_argument("--seed", type=int, default=424242)
    ap.add_argument("--horizon", type=int, default=28)
    ap.add_argument("--remove", type=str, default="0,1,2", help="Comma-separated timestep indices to zero out.")
    ap.add_argument("--genome-seed", type=int, default=7, help="RNG seed for random attacker genome.")
    ap.add_argument(
        "--export-replay-dir",
        type=Path,
        default=None,
        help="If set, write baseline.json + counterfactual.json (full replays) into this directory.",
    )
    args = ap.parse_args()

    remove_ts = [int(x.strip()) for x in args.remove.split(",") if x.strip() != ""]
    rng = np.random.default_rng(args.genome_seed)
    genome = rng.uniform(size=(args.horizon, 2))

    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=max(args.horizon, 32))

    def evaluator(g: np.ndarray, s: int):
        return rollout_stablecoin(template, g, seed=s)

    report, baseline_rr, variant_rr = counterfactual_remove_steps_with_rollouts(
        genome, evaluator, remove_timesteps=remove_ts, base_seed=args.seed
    )
    payload = counterfactual_bundle_to_jsonable(report)
    payload["meta"] = {"cli": "export_counterfactual", "base_seed": args.seed}
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.export_replay_dir is not None:
        args.export_replay_dir.mkdir(parents=True, exist_ok=True)
        common_meta = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "export_counterfactual",
            "base_seed": args.seed,
            "removed_timesteps": remove_ts,
        }
        br = rollout_to_replay_dict(baseline_rr)
        br["meta"] = {**common_meta, "variant": "baseline"}
        vr = rollout_to_replay_dict(variant_rr)
        vr["meta"] = {**common_meta, "variant": "counterfactual"}
        (args.export_replay_dir / "baseline.json").write_text(json.dumps(br, indent=2), encoding="utf-8")
        (args.export_replay_dir / "counterfactual.json").write_text(json.dumps(vr, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
