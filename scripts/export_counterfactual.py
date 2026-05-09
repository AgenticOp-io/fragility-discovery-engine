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
    counterfactual_remove_steps_with_rollouts,
)
from fragility_engine.network.graph_cli import contagion_graph_from_cli
from fragility_engine.runner import (
    REPLAY_SCHEMA_VERSION,
    rollout_stablecoin,
    rollout_stablecoin_network,
    rollout_to_replay_dict,
)
from fragility_engine.world.stablecoin_network import (
    StablecoinNetworkWorld,
    default_whale_weights,
    neighbor_lists_topology_meta,
)
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    ap = argparse.ArgumentParser(description="Export counterfactual JSON (drop shock timesteps, same seed).")
    ap.add_argument("--out", type=Path, default=Path("counterfactual.json"))
    ap.add_argument("--seed", type=int, default=424242)
    ap.add_argument("--horizon", type=int, default=28)
    ap.add_argument("--remove", type=str, default="0,1,2", help="Comma-separated timestep indices to zero out.")
    ap.add_argument("--genome-seed", type=int, default=7, help="RNG seed for random attacker genome.")
    ap.add_argument(
        "--mode",
        choices=("aggregate", "network"),
        default="aggregate",
        help="aggregate = peg world; network = StablecoinNetworkWorld.",
    )
    ap.add_argument("--initial-panic", type=float, default=0.05, help="[aggregate] reset panic.")
    ap.add_argument("--base-panic", type=float, default=0.05, help="[network] uniform node panic at reset.")
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
    ap.add_argument("--beta", type=float, default=0.38)
    ap.add_argument("--whale-frac", type=float, default=0.22)
    ap.add_argument("--neighbor-json", type=Path, default=None, help="[network] list-only topology JSON.")
    ap.add_argument("--neighbor-weights-json", type=Path, default=None)
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

    topo_meta: dict | None = None

    if args.mode == "aggregate":
        template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=max(args.horizon, 32))

        def evaluator(g: np.ndarray, s: int):
            return rollout_stablecoin(
                template,
                g,
                seed=s,
                initial_panic=float(args.initial_panic),
                continue_after_collapse=bool(args.continue_after_collapse),
            )

    else:
        if args.neighbor_json is not None:
            from fragility_engine.network.neighbor_io import load_neighbor_topology

            try:
                nl, nw = load_neighbor_topology(
                    Path(args.neighbor_json),
                    Path(args.neighbor_weights_json) if args.neighbor_weights_json else None,
                )
            except (ValueError, OSError, json.JSONDecodeError) as e:
                print(str(e), file=sys.stderr)
                raise SystemExit(2) from e
            n = len(nl)
            weights = default_whale_weights(n, whale_index=0, whale_frac=float(args.whale_frac))
            template = StablecoinNetworkWorld(
                population=default_stablecoin_population(),
                neighbor_lists=nl,
                neighbor_weights=nw,
                node_weights=weights,
                contagion_beta=float(args.beta),
                max_steps=max(args.horizon, 32),
            )
            topo_meta = neighbor_lists_topology_meta(nl, weighted=nw is not None)
        else:
            try:
                graph, gen_meta = contagion_graph_from_cli(
                    graph_kind=str(args.graph_kind),
                    nodes=int(args.nodes),
                    graph_seed=int(args.graph_seed),
                    er_p=float(args.er_p),
                    ws_k=int(args.ws_k),
                    ws_p=float(args.ws_p),
                )
            except ValueError as e:
                print(str(e), file=sys.stderr)
                raise SystemExit(2) from e
            n = int(args.nodes)
            weights = default_whale_weights(n, whale_index=0, whale_frac=float(args.whale_frac))
            template = StablecoinNetworkWorld(
                population=default_stablecoin_population(),
                adjacency=graph,
                node_weights=weights,
                contagion_beta=float(args.beta),
                max_steps=max(args.horizon, 32),
            )
            topo_meta = {
                **gen_meta,
                "undirected_edges": graph.undirected_edge_count(),
                "storage": "dense_adjacency",
            }

        def evaluator(g: np.ndarray, s: int):
            return rollout_stablecoin_network(
                template,
                g,
                seed=s,
                base_panic=float(args.base_panic),
                continue_after_collapse=bool(args.continue_after_collapse),
            )

    report, baseline_rr, variant_rr = counterfactual_remove_steps_with_rollouts(
        genome, evaluator, remove_timesteps=remove_ts, base_seed=args.seed
    )
    payload = counterfactual_bundle_to_jsonable(report)
    payload["meta"] = {
        "cli": "export_counterfactual",
        "base_seed": args.seed,
        "mode": args.mode,
        "continue_after_collapse": bool(args.continue_after_collapse),
    }
    if topo_meta is not None:
        payload["meta"]["topology"] = topo_meta
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.export_replay_dir is not None:
        args.export_replay_dir.mkdir(parents=True, exist_ok=True)
        common_meta = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "export_counterfactual",
            "base_seed": args.seed,
            "removed_timesteps": remove_ts,
            "mode": args.mode,
            "continue_after_collapse": bool(args.continue_after_collapse),
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
