"""Emit `replay.json` from a deterministic rollout (engine-first artifact)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.network.graph_cli import contagion_graph_from_cli
from fragility_engine.runner import (
    REPLAY_SCHEMA_VERSION,
    rollout_resource_cascade,
    rollout_service_backlog,
    rollout_stablecoin,
    rollout_stablecoin_network,
    rollout_to_replay_dict,
)
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.service_backlog import ServiceBacklogWorld
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    p = argparse.ArgumentParser(description="Export rollout JSON for replay UI / tooling.")
    p.add_argument("--out", type=Path, default=Path("replay.json"))
    p.add_argument("--seed", type=int, default=12345)
    p.add_argument("--horizon", type=int, default=32)
    p.add_argument("--genome-seed", type=int, default=42, help="RNG seed constructing random genome.")
    p.add_argument(
        "--mode",
        choices=("aggregate", "network", "resource_cascade", "service_backlog"),
        default="aggregate",
        help="aggregate=StablecoinPegWorld; network=contagion graph (B); resource_cascade=Phase J; "
        "service_backlog=Phase M backlog/slack world.",
    )
    p.add_argument(
        "--continue-after-collapse",
        action="store_true",
        help="Keep stepping after collapse (aggregate or network) for recovery metrics when re-peg occurs.",
    )
    p.add_argument(
        "--initial-panic",
        type=float,
        default=0.05,
        help="[aggregate] initial panic passed to world.reset (stablecoin peg).",
    )
    p.add_argument(
        "--base-panic",
        type=float,
        default=0.05,
        help="[network] uniform panic at reset on every node.",
    )
    p.add_argument(
        "--initial-overload",
        type=float,
        default=0.05,
        help="[resource_cascade] overload at reset [0,1].",
    )
    p.add_argument(
        "--initial-backlog",
        type=float,
        default=0.05,
        help="[service_backlog] backlog at reset.",
    )
    p.add_argument("--nodes", type=int, default=32, help="[network] graph order.")
    p.add_argument(
        "--graph-kind",
        choices=("erdos_renyi", "watts_strogatz"),
        default="erdos_renyi",
        help="[network] topology generator.",
    )
    p.add_argument("--er-p", type=float, default=0.14, help="[network] ER edge probability.")
    p.add_argument("--ws-k", type=int, default=6, help="[network] Watts-Strogatz ring degree (even, < nodes).")
    p.add_argument("--ws-p", type=float, default=0.12, help="[network] Watts-Strogatz rewire probability.")
    p.add_argument("--graph-seed", type=int, default=2026, help="[network] topology RNG seed.")
    p.add_argument("--beta", type=float, default=0.38, help="[network] contagion_step mixing.")
    p.add_argument("--whale-frac", type=float, default=0.22, help="[network] weight on whale_index.")
    p.add_argument("--whale-index", type=int, default=0, help="[network] concentrated-weight node.")
    p.add_argument(
        "--neighbor-json",
        type=Path,
        default=None,
        help="[network] JSON array of out-neighbor lists (list-only topology, no dense matrix).",
    )
    p.add_argument(
        "--neighbor-weights-json",
        type=Path,
        default=None,
        help="[network] optional JSON weights per out-edge (same shape as neighbor-json).",
    )
    args = p.parse_args()

    rng = np.random.default_rng(args.genome_seed)
    genome = rng.uniform(size=(args.horizon, 2))

    cont = bool(args.continue_after_collapse)
    topo_for_meta: dict | None = None
    if args.mode == "aggregate":
        template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=max(args.horizon, 48))
        result = rollout_stablecoin(
            template,
            genome,
            seed=args.seed,
            initial_panic=float(args.initial_panic),
            continue_after_collapse=cont,
        )
    elif args.mode == "network":
        from fragility_engine.network.neighbor_io import load_neighbor_topology
        from fragility_engine.world.stablecoin_network import neighbor_lists_topology_meta

        if args.neighbor_json is not None:
            try:
                nl, nw = load_neighbor_topology(
                    Path(args.neighbor_json),
                    Path(args.neighbor_weights_json) if args.neighbor_weights_json else None,
                )
            except (ValueError, OSError, json.JSONDecodeError) as e:
                raise SystemExit(str(e)) from e
            n = len(nl)
            weights = default_whale_weights(
                n,
                whale_index=int(args.whale_index),
                whale_frac=float(args.whale_frac),
            )
            template = StablecoinNetworkWorld(
                population=default_stablecoin_population(),
                neighbor_lists=nl,
                neighbor_weights=nw,
                node_weights=weights,
                contagion_beta=float(args.beta),
                max_steps=max(args.horizon, 48),
            )
            topo_for_meta = neighbor_lists_topology_meta(nl, weighted=nw is not None)
        else:
            try:
                graph, topo_meta = contagion_graph_from_cli(
                    graph_kind=str(args.graph_kind),
                    nodes=int(args.nodes),
                    graph_seed=int(args.graph_seed),
                    er_p=float(args.er_p),
                    ws_k=int(args.ws_k),
                    ws_p=float(args.ws_p),
                )
            except ValueError as e:
                raise SystemExit(str(e)) from e
            weights = default_whale_weights(
                args.nodes,
                whale_index=int(args.whale_index),
                whale_frac=float(args.whale_frac),
            )
            template = StablecoinNetworkWorld(
                population=default_stablecoin_population(),
                adjacency=graph,
                node_weights=weights,
                contagion_beta=float(args.beta),
                max_steps=max(args.horizon, 48),
            )
            topo_for_meta = {
                **topo_meta,
                "undirected_edges": graph.undirected_edge_count(),
                "storage": "dense_adjacency",
            }
        result = rollout_stablecoin_network(
            template,
            genome,
            seed=args.seed,
            base_panic=float(args.base_panic),
            continue_after_collapse=cont,
        )
    elif args.mode == "resource_cascade":
        ms = max(int(args.horizon), 48)
        template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=ms)
        result = rollout_resource_cascade(
            template,
            genome,
            seed=int(args.seed),
            initial_overload=float(args.initial_overload),
            continue_after_collapse=cont,
        )
    else:
        ms = max(int(args.horizon), 48)
        template = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=ms)
        result = rollout_service_backlog(
            template,
            genome,
            seed=int(args.seed),
            initial_backlog=float(args.initial_backlog),
            continue_after_collapse=cont,
        )

    payload = rollout_to_replay_dict(result)
    meta = {
        "replay_schema": REPLAY_SCHEMA_VERSION,
        "cli": "export_replay",
        "mode": args.mode,
    }
    if cont:
        meta["continue_after_collapse"] = True
    if args.mode == "aggregate":
        meta["initial_panic"] = float(args.initial_panic)
    elif args.mode == "network":
        meta["base_panic"] = float(args.base_panic)
        if topo_for_meta is not None:
            meta["topology"] = topo_for_meta
    elif args.mode == "resource_cascade":
        meta["domain"] = "resource_cascade"
        meta["initial_overload"] = float(args.initial_overload)
    else:
        meta["domain"] = "service_backlog"
        meta["initial_backlog"] = float(args.initial_backlog)
    payload["meta"] = meta
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
