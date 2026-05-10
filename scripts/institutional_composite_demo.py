"""Moonshot: emit twin-domain composite JSON (network + resource cascade, same genome)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.benchmarks.institutional_composite import twin_domain_rollout_artifact
from fragility_engine.network.contagion_graph import ContagionGraph
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights


def main() -> None:
    ap = argparse.ArgumentParser(description=twin_domain_rollout_artifact.__doc__ or "")
    ap.add_argument("--nodes", type=int, default=11)
    ap.add_argument("--er-p", type=float, default=0.14)
    ap.add_argument("--graph-seed", type=int, default=55)
    ap.add_argument("--genome-seed", type=int, default=333)
    ap.add_argument("--horizon", type=int, default=10)
    ap.add_argument("--network-seed", type=int, default=7001)
    ap.add_argument("--cascade-seed", type=int, default=7002)
    ap.add_argument("--base-panic", type=float, default=0.05)
    ap.add_argument("--initial-overload", type=float, default=0.05)
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional path to write JSON (UTF-8); still prints to stdout.",
    )
    args = ap.parse_args()

    rng = np.random.default_rng(int(args.genome_seed))
    genome = rng.uniform(size=(int(args.horizon), 2))

    graph = ContagionGraph.erdos_renyi(int(args.nodes), p=float(args.er_p), seed=int(args.graph_seed))
    nn = graph.n_nodes
    net_w = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=default_whale_weights(nn, whale_index=0, whale_frac=0.2),
        contagion_beta=0.35,
        max_steps=24,
    )
    rc_w = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=22)

    out = twin_domain_rollout_artifact(
        net_w,
        rc_w,
        genome,
        network_seed=int(args.network_seed),
        cascade_seed=int(args.cascade_seed),
        base_panic=float(args.base_panic),
        initial_overload=float(args.initial_overload),
    )
    text = json.dumps(out, indent=2)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
