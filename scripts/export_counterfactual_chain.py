"""Export baseline vs cumulative mutation-chain counterfactual (network list or dense topology)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from fragility_engine.explain.counterfactual import counterfactual_bundle_to_jsonable
from fragility_engine.explain.counterfactual_chain import (
    CHAIN_SPEC_SCHEMA,
    counterfactual_network_mutation_chain_with_rollouts,
    mutation_chain_path_rollouts,
    parse_chain_spec_payload,
)
from fragility_engine.explain.trace import mutation_chain_path_to_trace
from fragility_engine.network.network_world_cli import build_stablecoin_network_world_cli
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_to_replay_dict


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Network counterfactual: apply an ordered list of physics mutations cumulatively on a template "
            "clone, then compare rollout vs the original template (same genome + rollout seed)."
        ),
    )
    ap.add_argument(
        "--chain-json",
        type=Path,
        required=True,
        help=f'JSON file: {{"schema": "{CHAIN_SPEC_SCHEMA}", "steps": [...]}}',
    )
    ap.add_argument("--out", type=Path, default=Path("counterfactual_chain.json"))
    ap.add_argument("--seed", type=int, default=424242, help="Rollout RNG seed.")
    ap.add_argument("--genome-seed", type=int, default=7)
    ap.add_argument("--horizon", type=int, default=28)
    ap.add_argument("--base-panic", type=float, default=0.05)
    ap.add_argument(
        "--variant-base-panic",
        type=float,
        default=None,
        help="If set, counterfactual rollout uses this reset panic (baseline uses --base-panic).",
    )
    ap.add_argument("--continue-after-collapse", action="store_true")
    ap.add_argument("--nodes", type=int, default=24)
    ap.add_argument("--graph-kind", choices=("erdos_renyi", "watts_strogatz"), default="erdos_renyi")
    ap.add_argument("--er-p", type=float, default=0.12)
    ap.add_argument("--ws-k", type=int, default=6)
    ap.add_argument("--ws-p", type=float, default=0.15)
    ap.add_argument("--graph-seed", type=int, default=2026)
    ap.add_argument("--beta", type=float, default=0.38)
    ap.add_argument("--whale-frac", type=float, default=0.22)
    ap.add_argument("--neighbor-json", type=Path, default=None)
    ap.add_argument("--neighbor-weights-json", type=Path, default=None)
    ap.add_argument("--export-replay-dir", type=Path, default=None)
    ap.add_argument(
        "--emit-path-trace",
        action="store_true",
        help="Include explanation-mutation-chain-path-v1 (one rollout per cumulative mutation prefix).",
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
        steps = parse_chain_spec_payload(raw_spec)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2) from e

    needs_neighbor = any(s["kind"] in ("edge_weight", "edge_weights_patch") for s in steps)
    if needs_neighbor and args.neighbor_json is None:
        raise SystemExit("Chain steps include edge_weight; provide --neighbor-json (list topology).")

    rng = np.random.default_rng(int(args.genome_seed))
    genome = rng.uniform(size=(int(args.horizon), 2))
    cont = bool(args.continue_after_collapse)
    ms = max(int(args.horizon), 32)

    try:
        template, topo_meta = build_stablecoin_network_world_cli(
            neighbor_json=args.neighbor_json,
            neighbor_weights_json=args.neighbor_weights_json,
            nodes=int(args.nodes),
            graph_kind=str(args.graph_kind),
            graph_seed=int(args.graph_seed),
            er_p=float(args.er_p),
            ws_k=int(args.ws_k),
            ws_p=float(args.ws_p),
            beta=float(args.beta),
            whale_frac=float(args.whale_frac),
            max_steps=ms,
        )
    except (ValueError, OSError, json.JSONDecodeError) as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2) from e

    try:
        report, baseline_rr, variant_rr = counterfactual_network_mutation_chain_with_rollouts(
            genome,
            template,
            steps=steps,
            rollout_seed=int(args.seed),
            base_panic=float(args.base_panic),
            variant_base_panic=args.variant_base_panic,
            continue_after_collapse=cont,
        )
    except ValueError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2) from e

    payload = counterfactual_bundle_to_jsonable(report)
    payload["meta"] = {
        "cli": "export_counterfactual_chain",
        "base_seed": int(args.seed),
        "chain_schema": raw_spec.get("schema", CHAIN_SPEC_SCHEMA),
        "chain_json": str(args.chain_json),
        "continue_after_collapse": cont,
    }
    if topo_meta is not None:
        payload["meta"]["topology"] = topo_meta

    bp = float(args.base_panic)
    vbp = bp if args.variant_base_panic is None else float(args.variant_base_panic)
    if args.emit_path_trace:
        path_rollouts = mutation_chain_path_rollouts(
            genome,
            template,
            steps=steps,
            rollout_seed=int(args.seed),
            base_panic=bp,
            variant_base_panic=args.variant_base_panic,
            continue_after_collapse=cont,
        )
        payload["path_trace"] = mutation_chain_path_to_trace(
            path_rollouts,
            steps,
            rollout_seed=int(args.seed),
            baseline_base_panic=bp,
            variant_base_panic=vbp,
        )

    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.export_replay_dir is not None:
        args.export_replay_dir.mkdir(parents=True, exist_ok=True)
        common_meta: dict = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "export_counterfactual_chain",
            "base_seed": int(args.seed),
            "mutation_steps": report["mutation_steps"],
            "baseline_base_panic": float(report["baseline_base_panic"]),
            "variant_base_panic": float(report["variant_base_panic"]),
            "continue_after_collapse": cont,
        }
        if topo_meta is not None:
            common_meta["topology"] = topo_meta
        br = rollout_to_replay_dict(baseline_rr)
        br["meta"] = {**common_meta, "variant": "baseline"}
        vr = rollout_to_replay_dict(variant_rr)
        vr["meta"] = {**common_meta, "variant": "counterfactual"}
        (args.export_replay_dir / "baseline.json").write_text(json.dumps(br, indent=2), encoding="utf-8")
        (args.export_replay_dir / "counterfactual.json").write_text(json.dumps(vr, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
