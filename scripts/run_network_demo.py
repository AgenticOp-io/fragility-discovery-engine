"""Smoke + GA on the graph contagion world."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution.thread_safe_template import thread_safe_network_clone
from fragility_engine.network.graph_cli import contagion_graph_from_cli
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_stablecoin_network, rollout_to_replay_dict
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights


def main() -> None:
    p = argparse.ArgumentParser(description="GA on StablecoinNetworkWorld (contagion graph).")
    p.add_argument("--export-replay", type=Path, default=None, help="Write best-rollout replay JSON.")
    p.add_argument("--nodes", type=int, default=48)
    p.add_argument(
        "--graph-kind",
        choices=("erdos_renyi", "watts_strogatz"),
        default="erdos_renyi",
    )
    p.add_argument("--er-p", type=float, default=0.12)
    p.add_argument("--ws-k", type=int, default=6)
    p.add_argument("--ws-p", type=float, default=0.15)
    p.add_argument("--graph-seed", type=int, default=2026)
    p.add_argument("--generations", type=int, default=10)
    p.add_argument("--population-size", type=int, default=20)
    p.add_argument("--ga-seed", type=int, default=131)
    p.add_argument("--horizon", type=int, default=20)
    p.add_argument("--base-panic", type=float, default=0.05, help="Uniform panic at reset for all nodes.")
    p.add_argument("--beta", type=float, default=0.38)
    p.add_argument("--whale-frac", type=float, default=0.24)
    p.add_argument(
        "--neighbor-json",
        type=Path,
        default=None,
        help="List-only topology JSON (out-neighbor lists); skips synthetic graph flags.",
    )
    p.add_argument("--neighbor-weights-json", type=Path, default=None, help="Optional edge weights JSON.")
    p.add_argument(
        "--eval-workers",
        type=int,
        default=1,
        help="Thread pool size for GA fitness evaluation (uses topology clone + fresh population when >1).",
    )
    args = p.parse_args()
    ew = max(1, int(args.eval_workers))

    topo_meta: dict
    if args.neighbor_json is not None:
        from fragility_engine.network.neighbor_io import load_neighbor_topology
        from fragility_engine.world.stablecoin_network import neighbor_lists_topology_meta

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
            max_steps=40,
        )
        topo_meta = neighbor_lists_topology_meta(nl, weighted=nw is not None)
    else:
        n = int(args.nodes)
        try:
            graph, gen_meta = contagion_graph_from_cli(
                graph_kind=str(args.graph_kind),
                nodes=n,
                graph_seed=int(args.graph_seed),
                er_p=float(args.er_p),
                ws_k=int(args.ws_k),
                ws_p=float(args.ws_p),
            )
        except ValueError as e:
            print(str(e), file=sys.stderr)
            raise SystemExit(2) from e

        weights = default_whale_weights(n, whale_index=0, whale_frac=float(args.whale_frac))
        template = StablecoinNetworkWorld(
            population=default_stablecoin_population(),
            adjacency=graph,
            node_weights=weights,
            contagion_beta=float(args.beta),
            max_steps=40,
        )
        topo_meta = {
            **gen_meta,
            "undirected_edges": graph.undirected_edge_count(),
            "storage": "dense_adjacency",
        }

    def evaluator(genome: np.ndarray, seed: int):
        world = thread_safe_network_clone(template) if ew > 1 else template
        return rollout_stablecoin_network(
            world, genome, seed=seed, base_panic=float(args.base_panic)
        )

    ga = genetic_search(
        evaluator,
        horizon=int(args.horizon),
        generations=int(args.generations),
        population_size=int(args.population_size),
        seed=int(args.ga_seed),
        eval_workers=ew,
    )
    replay = rollout_to_replay_dict(ga.best_rollout)
    print(json.dumps({"best_fitness": ga.best_fitness, "replay_summary": replay["trajectory"][-1]}, indent=2))

    if args.export_replay is not None:
        replay["meta"] = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "run_network_demo",
            "topology": topo_meta,
            "generations": int(args.generations),
            "population_size": int(args.population_size),
            "eval_workers": ew,
        }
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
