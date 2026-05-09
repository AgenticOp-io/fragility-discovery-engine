"""Alternating attacker/defender evolution (aggregate or network world)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution import alternating_coevolution, alternating_coevolution_network
from fragility_engine.network.graph_cli import contagion_graph_from_cli
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_to_replay_dict
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    p = argparse.ArgumentParser(description="Alternating attacker/defender GA (aggregate or contagion network).")
    p.add_argument("--mode", choices=("aggregate", "network"), default="aggregate")
    p.add_argument("--max-steps", type=int, default=40, help="World horizon cap (both modes).")

    p.add_argument("--nodes", type=int, default=32)
    p.add_argument(
        "--graph-kind",
        choices=("erdos_renyi", "watts_strogatz"),
        default="erdos_renyi",
    )
    p.add_argument("--er-p", type=float, default=0.12)
    p.add_argument("--ws-k", type=int, default=6)
    p.add_argument("--ws-p", type=float, default=0.15)
    p.add_argument("--graph-seed", type=int, default=2026)
    p.add_argument("--beta", type=float, default=0.38)
    p.add_argument("--whale-frac", type=float, default=0.24)
    p.add_argument("--base-panic", type=float, default=0.05)

    p.add_argument("--rounds", type=int, default=2)
    p.add_argument("--attacker-horizon", type=int, default=16)
    p.add_argument("--attacker-generations", type=int, default=6)
    p.add_argument("--attacker-population", type=int, default=14)
    p.add_argument("--defender-generations", type=int, default=6)
    p.add_argument("--defender-population", type=int, default=12)
    p.add_argument("--seed", type=int, default=131)

    p.add_argument(
        "--json-summary",
        type=Path,
        default=None,
        help="Write full summary JSON (rounds, genomes, mode, optional topology).",
    )
    p.add_argument(
        "--export-replay",
        type=Path,
        default=None,
        help="Write final probe rollout as replay JSON (same seed stack as last training round).",
    )
    args = p.parse_args()

    topo_meta: dict | None = None

    if args.mode == "aggregate":
        template = StablecoinPegWorld(
            population=default_stablecoin_population(),
            max_steps=int(args.max_steps),
        )
        summary = alternating_coevolution(
            template,
            attacker_horizon=int(args.attacker_horizon),
            rounds=int(args.rounds),
            attacker_generations=int(args.attacker_generations),
            attacker_population=int(args.attacker_population),
            defender_generations=int(args.defender_generations),
            defender_population=int(args.defender_population),
            seed=int(args.seed),
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
            print(str(e), file=sys.stderr)
            raise SystemExit(2) from e

        n = int(args.nodes)
        weights = default_whale_weights(n, whale_index=0, whale_frac=float(args.whale_frac))
        template = StablecoinNetworkWorld(
            population=default_stablecoin_population(),
            adjacency=graph,
            node_weights=weights,
            contagion_beta=float(args.beta),
            max_steps=int(args.max_steps),
        )
        summary = alternating_coevolution_network(
            template,
            base_panic=float(args.base_panic),
            attacker_horizon=int(args.attacker_horizon),
            rounds=int(args.rounds),
            attacker_generations=int(args.attacker_generations),
            attacker_population=int(args.attacker_population),
            defender_generations=int(args.defender_generations),
            defender_population=int(args.defender_population),
            seed=int(args.seed),
        )

    payload: dict = {
        "mode": summary.simulation_mode,
        "rounds": summary.rounds,
        "best_attacker": summary.best_attacker.tolist() if summary.best_attacker is not None else None,
        "best_defender": summary.best_defender.tolist() if summary.best_defender is not None else None,
    }
    if topo_meta is not None:
        payload["topology"] = topo_meta

    print(json.dumps(payload, indent=2))

    if args.json_summary is not None:
        args.json_summary.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.export_replay is not None:
        if summary.last_rollout is None:
            raise SystemExit("Coevolution produced no rollout (try rounds >= 1).")
        replay = rollout_to_replay_dict(summary.last_rollout)
        meta = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "run_coevolution",
            "coevolution_rounds": len(summary.rounds),
            "coevolution_mode": summary.simulation_mode,
        }
        if topo_meta is not None:
            meta["topology"] = topo_meta
        replay["meta"] = meta
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
