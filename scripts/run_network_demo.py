"""Smoke + GA on the graph contagion world."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
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
    p.add_argument("--beta", type=float, default=0.38)
    p.add_argument("--whale-frac", type=float, default=0.24)
    args = p.parse_args()

    n = int(args.nodes)
    try:
        graph, topo_meta = contagion_graph_from_cli(
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

    def evaluator(genome: np.ndarray, seed: int):
        return rollout_stablecoin_network(template, genome, seed=seed)

    ga = genetic_search(
        evaluator,
        horizon=int(args.horizon),
        generations=int(args.generations),
        population_size=int(args.population_size),
        seed=int(args.ga_seed),
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
        }
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
