"""Export a counterfactual attribution bundle as JSON (pinned seeds)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import (
    counterfactual_bundle_to_jsonable,
    counterfactual_network_base_panic_with_rollouts,
    counterfactual_network_contagion_beta_with_rollouts,
    counterfactual_network_edge_weight_with_rollouts,
    counterfactual_network_neighbor_edges_weight_patch_with_rollouts,
    counterfactual_remove_steps_with_rollouts,
    counterfactual_resource_cascade_cascade_coupling_shift_with_rollouts,
    counterfactual_resource_cascade_initial_overload_shift_with_rollouts,
)
from fragility_engine.network.network_world_cli import build_stablecoin_network_world_cli
from fragility_engine.runner import (
    REPLAY_SCHEMA_VERSION,
    rollout_resource_cascade,
    rollout_stablecoin,
    rollout_stablecoin_network,
    rollout_to_replay_dict,
)
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Export counterfactual JSON: remove shock timesteps (default), or network shifts to "
            "base_panic / contagion_beta (same genome + rollout seed)."
        ),
    )
    ap.add_argument("--out", type=Path, default=Path("counterfactual.json"))
    ap.add_argument(
        "--seed",
        type=int,
        default=424242,
        help="Rollout RNG seed (pinned for baseline vs counterfactual).",
    )
    ap.add_argument("--horizon", type=int, default=28)
    ap.add_argument(
        "--remove",
        type=str,
        default="0,1,2",
        help="[remove_steps] comma-separated timestep indices to zero.",
    )
    ap.add_argument("--genome-seed", type=int, default=7, help="RNG seed for random attacker genome.")
    ap.add_argument(
        "--intervention",
        choices=(
            "remove_steps",
            "initial_overload_shift",
            "cascade_coupling_shift",
            "base_panic_shift",
            "contagion_beta_shift",
            "edge_weight_shift",
            "edge_weights_shift",
        ),
        default="remove_steps",
        help=(
            "remove_steps: zero shock rows; resource_cascade: initial_overload_shift or cascade_coupling_shift "
            "(physics clone); network-only: base_panic / contagion_beta / edge weights "
            "(--neighbor-json for edge shifts); edge_weights_shift uses --edges-patch-json."
        ),
    )
    ap.add_argument(
        "--variant-base-panic",
        type=float,
        default=None,
        help="[network, base_panic_shift] counterfactual uniform reset panic.",
    )
    ap.add_argument(
        "--variant-beta",
        type=float,
        default=None,
        help="[network, contagion_beta_shift] counterfactual contagion beta.",
    )
    ap.add_argument(
        "--edge-from",
        type=int,
        default=None,
        help="[network, edge_weight_shift] tail node index (directed out-edge).",
    )
    ap.add_argument(
        "--edge-to",
        type=int,
        default=None,
        help="[network, edge_weight_shift] head node index.",
    )
    ap.add_argument(
        "--variant-edge-weight",
        type=float,
        default=None,
        help="[network, edge_weight_shift] positive weight on that out-edge in the counterfactual clone.",
    )
    ap.add_argument(
        "--mode",
        choices=("aggregate", "network", "resource_cascade"),
        default="aggregate",
        help="aggregate = peg world; network = StablecoinNetworkWorld; resource_cascade = Phase J scaffold.",
    )
    ap.add_argument("--initial-panic", type=float, default=0.05, help="[aggregate] reset panic.")
    ap.add_argument(
        "--initial-overload",
        type=float,
        default=0.06,
        help="[resource_cascade] baseline reset overload [0,1] (also overload for remove_steps evaluator).",
    )
    ap.add_argument(
        "--variant-initial-overload",
        type=float,
        default=None,
        help="[resource_cascade, initial_overload_shift] counterfactual reset overload [0,1].",
    )
    ap.add_argument(
        "--variant-cascade-coupling",
        type=float,
        default=None,
        help="[resource_cascade, cascade_coupling_shift] counterfactual cascade_coupling (baseline = template).",
    )
    ap.add_argument("--base-panic", type=float, default=0.05, help="[network] baseline uniform reset panic.")
    ap.add_argument(
        "--continue-after-collapse",
        action="store_true",
        help="Forward both baseline and counterfactual rollouts after collapse when applicable.",
    )
    ap.add_argument("--nodes", type=int, default=24, help="[network] graph order (synthetic topology).")
    ap.add_argument(
        "--graph-kind",
        choices=("erdos_renyi", "watts_strogatz"),
        default="erdos_renyi",
        help="[network] topology generator when not using --neighbor-json.",
    )
    ap.add_argument("--er-p", type=float, default=0.12)
    ap.add_argument("--ws-k", type=int, default=6)
    ap.add_argument("--ws-p", type=float, default=0.15)
    ap.add_argument("--graph-seed", type=int, default=2026)
    ap.add_argument("--beta", type=float, default=0.38, help="[network] baseline contagion beta.")
    ap.add_argument("--whale-frac", type=float, default=0.22)
    ap.add_argument("--neighbor-json", type=Path, default=None, help="[network] list-only topology JSON.")
    ap.add_argument("--neighbor-weights-json", type=Path, default=None)
    ap.add_argument(
        "--edges-patch-json",
        type=Path,
        default=None,
        help='[network, edge_weights_shift] JSON array of {"from","to","weight"} objects.',
    )
    ap.add_argument(
        "--export-replay-dir",
        type=Path,
        default=None,
        help="If set, write baseline.json + counterfactual.json (full replays) into this directory.",
    )
    args = ap.parse_args()

    _network_only = frozenset(
        {"base_panic_shift", "contagion_beta_shift", "edge_weight_shift", "edge_weights_shift"}
    )
    if args.intervention in _network_only and args.mode != "network":
        raise SystemExit(
            "--intervention base_panic_shift, contagion_beta_shift, edge_weight_shift, and edge_weights_shift "
            "require --mode network."
        )
    if args.intervention == "initial_overload_shift" and args.mode != "resource_cascade":
        raise SystemExit("--intervention initial_overload_shift requires --mode resource_cascade.")
    if args.intervention == "cascade_coupling_shift" and args.mode != "resource_cascade":
        raise SystemExit("--intervention cascade_coupling_shift requires --mode resource_cascade.")
    if args.intervention == "base_panic_shift" and args.variant_base_panic is None:
        raise SystemExit("--variant-base-panic required for --intervention base_panic_shift.")
    if args.intervention == "contagion_beta_shift" and args.variant_beta is None:
        raise SystemExit("--variant-beta required for --intervention contagion_beta_shift.")
    if args.intervention == "edge_weight_shift":
        if args.neighbor_json is None:
            raise SystemExit("--intervention edge_weight_shift requires --neighbor-json (list topology).")
        if args.edge_from is None or args.edge_to is None:
            raise SystemExit("--edge-from and --edge-to required for --intervention edge_weight_shift.")
        if args.variant_edge_weight is None:
            raise SystemExit("--variant-edge-weight required for --intervention edge_weight_shift.")
    if args.intervention == "edge_weights_shift":
        if args.neighbor_json is None:
            raise SystemExit("--intervention edge_weights_shift requires --neighbor-json (list topology).")
        if args.edges_patch_json is None:
            raise SystemExit("--edges-patch-json required for --intervention edge_weights_shift.")
    if args.mode == "resource_cascade":
        if args.intervention not in ("remove_steps", "initial_overload_shift", "cascade_coupling_shift"):
            raise SystemExit(
                "resource_cascade mode supports remove_steps, initial_overload_shift, or cascade_coupling_shift."
            )
        if args.intervention == "initial_overload_shift" and args.variant_initial_overload is None:
            raise SystemExit("--variant-initial-overload required for --intervention initial_overload_shift.")
        if args.intervention == "cascade_coupling_shift" and args.variant_cascade_coupling is None:
            raise SystemExit("--variant-cascade-coupling required for --intervention cascade_coupling_shift.")

    remove_ts = [int(x.strip()) for x in args.remove.split(",") if x.strip() != ""]
    rng = np.random.default_rng(args.genome_seed)
    genome = rng.uniform(size=(args.horizon, 2))

    topo_meta: dict | None = None
    cont = bool(args.continue_after_collapse)

    if args.mode == "aggregate":
        if args.intervention != "remove_steps":
            raise SystemExit("Aggregate mode supports only --intervention remove_steps.")
        template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=max(args.horizon, 32))

        def evaluator(g: np.ndarray, s: int):
            return rollout_stablecoin(
                template,
                g,
                seed=s,
                initial_panic=float(args.initial_panic),
                continue_after_collapse=cont,
            )

        report, baseline_rr, variant_rr = counterfactual_remove_steps_with_rollouts(
            genome, evaluator, remove_timesteps=remove_ts, base_seed=args.seed
        )
    elif args.mode == "resource_cascade":
        ms = max(args.horizon, 32)
        template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=ms)
        if args.intervention == "remove_steps":

            def evaluator_rc(g: np.ndarray, s: int):
                return rollout_resource_cascade(
                    template,
                    g,
                    seed=s,
                    initial_overload=float(args.initial_overload),
                    continue_after_collapse=cont,
                )

            report, baseline_rr, variant_rr = counterfactual_remove_steps_with_rollouts(
                genome, evaluator_rc, remove_timesteps=remove_ts, base_seed=args.seed
            )
        elif args.intervention == "initial_overload_shift":
            report, baseline_rr, variant_rr = counterfactual_resource_cascade_initial_overload_shift_with_rollouts(
                genome,
                template,
                baseline_initial_overload=float(args.initial_overload),
                variant_initial_overload=float(args.variant_initial_overload),
                rollout_seed=int(args.seed),
                continue_after_collapse=cont,
            )
        else:
            report, baseline_rr, variant_rr = counterfactual_resource_cascade_cascade_coupling_shift_with_rollouts(
                genome,
                template,
                variant_cascade_coupling=float(args.variant_cascade_coupling),
                rollout_seed=int(args.seed),
                initial_overload=float(args.initial_overload),
                continue_after_collapse=cont,
            )
    else:
        ms = max(args.horizon, 32)
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

        if args.intervention == "remove_steps":

            def evaluator(g: np.ndarray, s: int):
                return rollout_stablecoin_network(
                    template,
                    g,
                    seed=s,
                    base_panic=float(args.base_panic),
                    continue_after_collapse=cont,
                )

            report, baseline_rr, variant_rr = counterfactual_remove_steps_with_rollouts(
                genome, evaluator, remove_timesteps=remove_ts, base_seed=args.seed
            )
        elif args.intervention == "base_panic_shift":
            report, baseline_rr, variant_rr = counterfactual_network_base_panic_with_rollouts(
                genome,
                template,
                baseline_base_panic=float(args.base_panic),
                variant_base_panic=float(args.variant_base_panic),
                rollout_seed=int(args.seed),
                continue_after_collapse=cont,
            )
        elif args.intervention == "contagion_beta_shift":
            report, baseline_rr, variant_rr = counterfactual_network_contagion_beta_with_rollouts(
                genome,
                template,
                baseline_beta=float(args.beta),
                variant_beta=float(args.variant_beta),
                rollout_seed=int(args.seed),
                base_panic=float(args.base_panic),
                continue_after_collapse=cont,
            )
        elif args.intervention == "edge_weight_shift":
            report, baseline_rr, variant_rr = counterfactual_network_edge_weight_with_rollouts(
                genome,
                template,
                edge_from=int(args.edge_from),
                edge_to=int(args.edge_to),
                variant_edge_weight=float(args.variant_edge_weight),
                rollout_seed=int(args.seed),
                base_panic=float(args.base_panic),
                continue_after_collapse=cont,
            )
        else:
            try:
                patch_raw = json.loads(args.edges_patch_json.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as e:
                print(str(e), file=sys.stderr)
                raise SystemExit(2) from e
            if not isinstance(patch_raw, list):
                raise SystemExit("--edges-patch-json must be a JSON array")
            report, baseline_rr, variant_rr = counterfactual_network_neighbor_edges_weight_patch_with_rollouts(
                genome,
                template,
                edges_patch=patch_raw,
                rollout_seed=int(args.seed),
                base_panic=float(args.base_panic),
                continue_after_collapse=cont,
            )

    payload = counterfactual_bundle_to_jsonable(report)
    payload["meta"] = {
        "cli": "export_counterfactual",
        "base_seed": args.seed,
        "mode": args.mode,
        "intervention": args.intervention,
        "continue_after_collapse": cont,
    }
    if topo_meta is not None:
        payload["meta"]["topology"] = topo_meta
    if args.mode == "resource_cascade":
        payload["meta"]["domain"] = "resource_cascade"
        payload["meta"]["initial_overload"] = float(args.initial_overload)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.export_replay_dir is not None:
        args.export_replay_dir.mkdir(parents=True, exist_ok=True)
        common_meta: dict = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "export_counterfactual",
            "base_seed": args.seed,
            "mode": args.mode,
            "intervention": args.intervention,
            "continue_after_collapse": cont,
        }
        if args.intervention == "remove_steps":
            common_meta["removed_timesteps"] = remove_ts
        elif args.intervention == "base_panic_shift":
            common_meta["baseline_base_panic"] = float(args.base_panic)
            common_meta["variant_base_panic"] = float(args.variant_base_panic)
        elif args.intervention == "contagion_beta_shift":
            common_meta["baseline_beta"] = float(args.beta)
            common_meta["variant_beta"] = float(args.variant_beta)
        elif args.intervention == "edge_weight_shift":
            common_meta["edge_from"] = int(args.edge_from)
            common_meta["edge_to"] = int(args.edge_to)
            common_meta["variant_edge_weight"] = float(args.variant_edge_weight)
        elif args.intervention == "initial_overload_shift":
            common_meta["baseline_initial_overload"] = float(args.initial_overload)
            common_meta["variant_initial_overload"] = float(args.variant_initial_overload)
        elif args.intervention == "cascade_coupling_shift":
            common_meta["baseline_cascade_coupling"] = float(report["baseline_cascade_coupling"])
            common_meta["variant_cascade_coupling"] = float(report["variant_cascade_coupling"])
        else:
            common_meta["edges_patch"] = report.get("edges_patch")
        if topo_meta is not None:
            common_meta["topology"] = topo_meta
        if args.mode == "resource_cascade":
            common_meta["domain"] = "resource_cascade"
            common_meta["initial_overload"] = float(args.initial_overload)
        br = rollout_to_replay_dict(baseline_rr)
        br["meta"] = {**common_meta, "variant": "baseline"}
        vr = rollout_to_replay_dict(variant_rr)
        vr["meta"] = {**common_meta, "variant": "counterfactual"}
        (args.export_replay_dir / "baseline.json").write_text(json.dumps(br, indent=2), encoding="utf-8")
        (args.export_replay_dir / "counterfactual.json").write_text(json.dumps(vr, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
