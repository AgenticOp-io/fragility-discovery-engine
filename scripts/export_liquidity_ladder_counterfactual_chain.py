"""Export baseline vs cumulative liquidity-ladder mutation-chain counterfactual JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import counterfactual_bundle_to_jsonable
from fragility_engine.explain.counterfactual_chain_liquidity_ladder import (
    LIQUIDITY_LADDER_CHAIN_SPEC_SCHEMA,
    counterfactual_liquidity_ladder_mutation_chain_with_rollouts,
    mutation_chain_path_rollouts_liquidity_ladder,
    parse_liquidity_ladder_chain_spec_payload,
)
from fragility_engine.explain.trace import mutation_chain_path_to_trace_liquidity_ladder
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_to_replay_dict
from fragility_engine.world.liquidity_ladder import LiquidityLadderWorld


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Liquidity-ladder counterfactual: apply an ordered list of physics mutations cumulatively on a "
            "template clone, then compare rollout vs the original template (same genome + rollout seed)."
        ),
    )
    ap.add_argument(
        "--chain-json",
        type=Path,
        required=True,
        help=f'JSON file: {{"schema": "{LIQUIDITY_LADDER_CHAIN_SPEC_SCHEMA}", "steps": [...]}}',
    )
    ap.add_argument("--out", type=Path, default=Path("counterfactual_ll_chain.json"))
    ap.add_argument("--seed", type=int, default=424243, help="Rollout RNG seed.")
    ap.add_argument("--genome-seed", type=int, default=7)
    ap.add_argument("--horizon", type=int, default=28)
    ap.add_argument("--initial-margin", type=float, default=0.06, help="Baseline reset margin utilization.")
    ap.add_argument(
        "--variant-initial-margin",
        type=float,
        default=None,
        help="If set, counterfactual rollout uses this reset margin (baseline uses --initial-margin).",
    )
    ap.add_argument("--continue-after-collapse", action="store_true")
    ap.add_argument("--max-steps", type=int, default=40)
    ap.add_argument("--export-replay-dir", type=Path, default=None)
    ap.add_argument(
        "--emit-path-trace",
        action="store_true",
        help="Include explanation-mutation-chain-path-liquidity-ladder-v1 (one rollout per cumulative prefix).",
    )
    args = ap.parse_args()

    try:
        raw_spec = json.loads(args.chain_json.read_text(encoding="utf-8"))
    except OSError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2) from e
    except json.JSONDecodeError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2) from e
    if not isinstance(raw_spec, dict):
        raise SystemExit("--chain-json must contain a JSON object")
    try:
        steps = parse_liquidity_ladder_chain_spec_payload(raw_spec)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2) from e

    rng = np.random.default_rng(int(args.genome_seed))
    genome = rng.uniform(size=(int(args.horizon), 2))
    cont = bool(args.continue_after_collapse)
    ms = max(int(args.horizon), int(args.max_steps))

    template = LiquidityLadderWorld(population=default_stablecoin_population(), max_steps=ms)

    try:
        report, baseline_rr, variant_rr = counterfactual_liquidity_ladder_mutation_chain_with_rollouts(
            genome,
            template,
            steps=steps,
            rollout_seed=int(args.seed),
            initial_margin=float(args.initial_margin),
            variant_initial_margin=args.variant_initial_margin,
            continue_after_collapse=cont,
        )
    except ValueError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2) from e

    payload = counterfactual_bundle_to_jsonable(report)
    payload["meta"] = {
        "cli": "export_liquidity_ladder_counterfactual_chain",
        "base_seed": int(args.seed),
        "chain_schema": raw_spec.get("schema", LIQUIDITY_LADDER_CHAIN_SPEC_SCHEMA),
        "chain_json": str(args.chain_json),
        "continue_after_collapse": cont,
        "max_steps": ms,
    }

    bim = float(args.initial_margin)
    vim = bim if args.variant_initial_margin is None else float(args.variant_initial_margin)
    if args.emit_path_trace:
        path_rollouts = mutation_chain_path_rollouts_liquidity_ladder(
            genome,
            template,
            steps=steps,
            rollout_seed=int(args.seed),
            initial_margin=bim,
            variant_initial_margin=args.variant_initial_margin,
            continue_after_collapse=cont,
        )
        payload["path_trace"] = mutation_chain_path_to_trace_liquidity_ladder(
            path_rollouts,
            steps,
            rollout_seed=int(args.seed),
            baseline_initial_margin=bim,
            variant_initial_margin=vim,
        )

    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.export_replay_dir is not None:
        args.export_replay_dir.mkdir(parents=True, exist_ok=True)
        common_meta: dict = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "export_liquidity_ladder_counterfactual_chain",
            "base_seed": int(args.seed),
            "mutation_steps": report["mutation_steps"],
            "baseline_initial_margin": float(report["baseline_initial_margin"]),
            "variant_initial_margin": float(report["variant_initial_margin"]),
            "continue_after_collapse": cont,
        }
        br = rollout_to_replay_dict(baseline_rr)
        br["meta"] = {**common_meta, "variant": "baseline"}
        vr = rollout_to_replay_dict(variant_rr)
        vr["meta"] = {**common_meta, "variant": "counterfactual"}
        (args.export_replay_dir / "baseline.json").write_text(json.dumps(br, indent=2), encoding="utf-8")
        (args.export_replay_dir / "counterfactual.json").write_text(json.dumps(vr, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
