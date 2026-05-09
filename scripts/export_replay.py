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
    rollout_stablecoin,
    rollout_stablecoin_network,
    rollout_to_replay_dict,
)
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
        choices=("aggregate", "network"),
        default="aggregate",
        help="aggregate = StablecoinPegWorld; network = contagion graph world (Phase B).",
    )
    p.add_argument(
        "--continue-after-collapse",
        action="store_true",
        help="[aggregate] keep stepping after collapse to populate recovery_timestep / latency when re-peg occurs.",
    )
    p.add_argument("--nodes", type=int, default=32, help="[network] graph order.")
    p.add_argument(
        "--graph-kind",
        choices=("erdos_renyi", "watts_strogatz"),
        default="erdos_renyi",
        help="[network] topology generator.",
    )
    p.add_argument("--er-p", type=float, default=0.14, help="[network] ER edge probability.")
    p.add_argument("--ws-k", type=int, default=6, help="[network] Watts–Strogatz ring degree (even, < nodes).")
    p.add_argument("--ws-p", type=float, default=0.12, help="[network] Watts–Strogatz rewire probability.")
    p.add_argument("--graph-seed", type=int, default=2026, help="[network] topology RNG seed.")
    p.add_argument("--beta", type=float, default=0.38, help="[network] contagion_step mixing.")
    p.add_argument("--whale-frac", type=float, default=0.22, help="[network] weight on whale_index.")
    p.add_argument("--whale-index", type=int, default=0, help="[network] concentrated-weight node.")
    args = p.parse_args()

    rng = np.random.default_rng(args.genome_seed)
    genome = rng.uniform(size=(args.horizon, 2))

    if args.mode == "aggregate":
        template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=max(args.horizon, 48))
        result = rollout_stablecoin(
            template,
            genome,
            seed=args.seed,
            continue_after_collapse=bool(args.continue_after_collapse),
        )
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
        result = rollout_stablecoin_network(template, genome, seed=args.seed)

    payload = rollout_to_replay_dict(result)
    meta = {
        "replay_schema": REPLAY_SCHEMA_VERSION,
        "cli": "export_replay",
        "mode": args.mode,
    }
    if args.mode == "aggregate" and args.continue_after_collapse:
        meta["continue_after_collapse"] = True
    if args.mode == "network":
        meta["topology"] = topo_meta
    payload["meta"] = meta
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
