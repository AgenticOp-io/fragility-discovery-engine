"""Export baseline vs cumulative resource-cascade mutation-chain counterfactual JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import counterfactual_bundle_to_jsonable
from fragility_engine.explain.counterfactual_chain_resource_cascade import (
    RESOURCE_CASCADE_CHAIN_SPEC_SCHEMA,
    counterfactual_resource_cascade_mutation_chain_with_rollouts,
    mutation_chain_path_rollouts_resource_cascade,
    parse_resource_cascade_chain_spec_payload,
)
from fragility_engine.explain.trace import mutation_chain_path_to_trace_resource_cascade
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_to_replay_dict
from fragility_engine.world.resource_cascade import ResourceCascadeWorld


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Resource-cascade counterfactual: apply an ordered list of physics mutations cumulatively on a "
            "template clone, then compare rollout vs the original template (same genome + rollout seed)."
        ),
    )
    ap.add_argument(
        "--chain-json",
        type=Path,
        required=True,
        help=f'JSON file: {{"schema": "{RESOURCE_CASCADE_CHAIN_SPEC_SCHEMA}", "steps": [...]}}',
    )
    ap.add_argument("--out", type=Path, default=Path("counterfactual_rc_chain.json"))
    ap.add_argument("--seed", type=int, default=424242, help="Rollout RNG seed.")
    ap.add_argument("--genome-seed", type=int, default=7)
    ap.add_argument("--horizon", type=int, default=28)
    ap.add_argument("--initial-overload", type=float, default=0.06, help="Baseline reset overload [0,1].")
    ap.add_argument(
        "--variant-initial-overload",
        type=float,
        default=None,
        help="If set, counterfactual rollout uses this reset overload (baseline uses --initial-overload).",
    )
    ap.add_argument("--continue-after-collapse", action="store_true")
    ap.add_argument("--max-steps", type=int, default=40)
    ap.add_argument("--export-replay-dir", type=Path, default=None)
    ap.add_argument(
        "--emit-path-trace",
        action="store_true",
        help="Include explanation-mutation-chain-path-resource-cascade-v1 (one rollout per cumulative prefix).",
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
        steps = parse_resource_cascade_chain_spec_payload(raw_spec)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2) from e

    rng = np.random.default_rng(int(args.genome_seed))
    genome = rng.uniform(size=(int(args.horizon), 2))
    cont = bool(args.continue_after_collapse)
    ms = max(int(args.horizon), int(args.max_steps))

    template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=ms)

    try:
        report, baseline_rr, variant_rr = counterfactual_resource_cascade_mutation_chain_with_rollouts(
            genome,
            template,
            steps=steps,
            rollout_seed=int(args.seed),
            initial_overload=float(args.initial_overload),
            variant_initial_overload=args.variant_initial_overload,
            continue_after_collapse=cont,
        )
    except ValueError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2) from e

    payload = counterfactual_bundle_to_jsonable(report)
    payload["meta"] = {
        "cli": "export_resource_cascade_counterfactual_chain",
        "base_seed": int(args.seed),
        "chain_schema": raw_spec.get("schema", RESOURCE_CASCADE_CHAIN_SPEC_SCHEMA),
        "chain_json": str(args.chain_json),
        "continue_after_collapse": cont,
        "max_steps": ms,
    }

    bio = float(args.initial_overload)
    vio = bio if args.variant_initial_overload is None else float(args.variant_initial_overload)
    if args.emit_path_trace:
        path_rollouts = mutation_chain_path_rollouts_resource_cascade(
            genome,
            template,
            steps=steps,
            rollout_seed=int(args.seed),
            initial_overload=bio,
            variant_initial_overload=args.variant_initial_overload,
            continue_after_collapse=cont,
        )
        payload["path_trace"] = mutation_chain_path_to_trace_resource_cascade(
            path_rollouts,
            steps,
            rollout_seed=int(args.seed),
            baseline_initial_overload=bio,
            variant_initial_overload=vio,
        )

    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.export_replay_dir is not None:
        args.export_replay_dir.mkdir(parents=True, exist_ok=True)
        common_meta: dict = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "export_resource_cascade_counterfactual_chain",
            "base_seed": int(args.seed),
            "mutation_steps": report["mutation_steps"],
            "baseline_initial_overload": float(report["baseline_initial_overload"]),
            "variant_initial_overload": float(report["variant_initial_overload"]),
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
