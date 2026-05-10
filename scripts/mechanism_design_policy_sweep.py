"""Moonshot: discrete defender policies with inner GA adversary (network world)."""

from __future__ import annotations

import argparse
import json

import numpy as np

from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.network.contagion_graph import ContagionGraph
from fragility_engine.runner import rollout_stablecoin_network
from fragility_engine.types import RolloutResult
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights

_PRESETS: dict[str, np.ndarray] = {
    "weak": np.array([0.08, 0.08, 0.08, 0.08], dtype=np.float64),
    "mid": np.array([0.5, 0.5, 0.5, 0.5], dtype=np.float64),
    "strong": np.array([0.92, 0.92, 0.92, 0.92], dtype=np.float64),
}


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Outer loop: fixed defender genome presets; inner GA searches shock schedules.",
    )
    ap.add_argument(
        "--policies",
        type=str,
        default="weak,mid,strong",
        help="Comma-separated defender presets: weak|mid|strong (decode_defender_genome layout).",
    )
    ap.add_argument("--nodes", type=int, default=12)
    ap.add_argument("--er-p", type=float, default=0.16)
    ap.add_argument("--graph-seed", type=int, default=77)
    ap.add_argument("--horizon", type=int, default=10)
    ap.add_argument("--generations", type=int, default=3)
    ap.add_argument("--population-size", type=int, default=12)
    ap.add_argument("--ga-seed", type=int, default=12002)
    ap.add_argument("--base-panic", type=float, default=0.05)
    ap.add_argument("--max-steps", type=int, default=22)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    names = [x.strip() for x in str(args.policies).split(",") if x.strip()]
    defenders: list[np.ndarray] = []
    for n in names:
        key = n.lower()
        if key not in _PRESETS:
            raise SystemExit(f"Unknown policy {n!r}; choose from {sorted(_PRESETS)}.")
        defenders.append(_PRESETS[key])

    graph = ContagionGraph.erdos_renyi(int(args.nodes), p=float(args.er_p), seed=int(args.graph_seed))
    nn = graph.n_nodes
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=default_whale_weights(nn, whale_index=0, whale_frac=0.2),
        contagion_beta=0.34,
        max_steps=int(args.max_steps),
    )

    outer: list[dict[str, object]] = []
    for i, dgen in enumerate(defenders):

        def evaluator(genome: np.ndarray, seed: int, defender: np.ndarray = dgen) -> RolloutResult:
            return rollout_stablecoin_network(
                template,
                genome,
                seed=int(seed),
                base_panic=float(args.base_panic),
                defender_genome=defender,
            )

        sr = genetic_search(
            evaluator,
            horizon=int(args.horizon),
            generations=int(args.generations),
            population_size=int(args.population_size),
            seed=int(args.ga_seed) + i * 997,
        )
        outer.append(
            {
                "policy_name": names[i],
                "defender_genome": [float(x) for x in dgen.reshape(-1).tolist()],
                "inner_ga_best_fitness": float(sr.best_fitness),
                "inner_ga_best_attack_cost": float(sr.best_rollout.attack_cost),
                "inner_ga_collapsed": bool(sr.best_rollout.collapsed),
            }
        )

    payload: dict[str, object] = {
        "schema": "fragility-mechanism-design-outer-v1",
        "graph_seed": int(args.graph_seed),
        "nodes": int(args.nodes),
        "er_p": float(args.er_p),
        "horizon": int(args.horizon),
        "generations": int(args.generations),
        "population_size": int(args.population_size),
        "ga_seed_base": int(args.ga_seed),
        "policies": outer,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for row in outer:
            print(
                f"{row['policy_name']}: fitness={row['inner_ga_best_fitness']:.5f} "
                f"cost={row['inner_ga_best_attack_cost']:.5f} collapsed={row['inner_ga_collapsed']}"
            )


if __name__ == "__main__":
    main()
