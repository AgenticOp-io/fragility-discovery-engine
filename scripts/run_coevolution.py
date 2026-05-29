"""Alternating attacker/defender evolution (aggregate, network, resource cascade, or service backlog)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution import (
    alternating_coevolution,
    alternating_coevolution_inventory_buffer,
    alternating_coevolution_liquidity_ladder,
    alternating_coevolution_network,
    alternating_coevolution_resource_cascade,
    alternating_coevolution_service_backlog,
)
from fragility_engine.coevolution.coupled_institution import alternating_coevolution_coupled_institution
from fragility_engine.coevolution.pareto_export import (
    flatten_coevolution_attacker_pareto,
    pareto_front_payload_from_archive_dicts,
)
from fragility_engine.network.graph_cli import contagion_graph_from_cli
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_to_replay_dict
from fragility_engine.world.inventory_buffer import InventoryBufferWorld
from fragility_engine.world.liquidity_ladder import LiquidityLadderWorld
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.service_backlog import ServiceBacklogWorld
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    p = argparse.ArgumentParser(
        description=(
            "Alternating attacker/defender GA: aggregate, network, resource cascade, or service backlog."
        )
    )
    p.add_argument(
        "--mode",
        choices=(
            "aggregate",
            "network",
            "resource_cascade",
            "service_backlog",
            "liquidity_ladder",
            "inventory_buffer",
            "coupled_institution",
        ),
        default="aggregate",
    )
    p.add_argument(
        "--coupling",
        type=float,
        default=0.3,
        help="[coupled_institution] in-step coupling strength between peg panic and overload.",
    )
    p.add_argument(
        "--initial-panic",
        type=float,
        default=0.05,
        help="[coupled_institution] peg panic at reset.",
    )
    p.add_argument("--max-steps", type=int, default=40, help="World horizon cap (all modes).")
    p.add_argument(
        "--initial-overload",
        type=float,
        default=0.05,
        help="[resource_cascade] overload at reset [0,1] (defender reserve_boost damps effective overload).",
    )
    p.add_argument(
        "--initial-backlog",
        type=float,
        default=0.05,
        help="[service_backlog] backlog at reset (defender reserve_boost damps effective backlog).",
    )
    p.add_argument(
        "--initial-margin",
        type=float,
        default=0.06,
        help="[liquidity_ladder] margin utilization at reset (defender reserve_boost damps effective margin).",
    )
    p.add_argument(
        "--initial-stock",
        type=float,
        default=0.88,
        help="[inventory_buffer] normalized stock level at reset (defender reserve_boost damps effective stock drain).",
    )

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
        "--eval-workers",
        type=int,
        default=1,
        help="Thread pool size for attacker/defender GA fitness evaluation (built-in modes clone worlds when >1).",
    )
    p.add_argument(
        "--continue-after-collapse",
        action="store_true",
        help="Keep rolling after collapse for recovery metrics (passed through to rollouts).",
    )

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
    p.add_argument(
        "--neighbor-json",
        type=Path,
        default=None,
        help="[network] list-only topology JSON (out-neighbor lists); skips synthetic graph flags.",
    )
    p.add_argument(
        "--neighbor-weights-json",
        type=Path,
        default=None,
        help="[network] optional positive weights JSON (same shape as --neighbor-json).",
    )
    p.add_argument(
        "--collect-attacker-pareto",
        action="store_true",
        help="Each round: attach attacker GA Pareto points (severity vs attack_cost) under rounds[].attacker_pareto.",
    )
    p.add_argument(
        "--export-pareto-json",
        type=Path,
        default=None,
        help="Write merged pareto-front-v1 JSON (implies --collect-attacker-pareto) for artifacts/pareto_viewer.",
    )
    args = p.parse_args()

    collect_pareto = bool(args.collect_attacker_pareto or args.export_pareto_json)
    ew = max(1, int(args.eval_workers))

    enriched_topo: dict | None = None
    network_graph = None

    if args.mode == "aggregate":
        template = StablecoinPegWorld(
            population=default_stablecoin_population(),
            max_steps=int(args.max_steps),
        )
        summary = alternating_coevolution(
            template,
            continue_after_collapse=bool(args.continue_after_collapse),
            collect_attacker_pareto=collect_pareto,
            attacker_horizon=int(args.attacker_horizon),
            rounds=int(args.rounds),
            attacker_generations=int(args.attacker_generations),
            attacker_population=int(args.attacker_population),
            defender_generations=int(args.defender_generations),
            defender_population=int(args.defender_population),
            seed=int(args.seed),
            eval_workers=ew,
        )
    elif args.mode == "network":
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
                max_steps=int(args.max_steps),
            )
            enriched_topo = neighbor_lists_topology_meta(nl, weighted=nw is not None)
        else:
            try:
                network_graph, topo_meta = contagion_graph_from_cli(
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
                adjacency=network_graph,
                node_weights=weights,
                contagion_beta=float(args.beta),
                max_steps=int(args.max_steps),
            )
            enriched_topo = {
                **topo_meta,
                "undirected_edges": network_graph.undirected_edge_count(),
                "storage": "dense_adjacency",
            }
        summary = alternating_coevolution_network(
            template,
            base_panic=float(args.base_panic),
            continue_after_collapse=bool(args.continue_after_collapse),
            collect_attacker_pareto=collect_pareto,
            attacker_horizon=int(args.attacker_horizon),
            rounds=int(args.rounds),
            attacker_generations=int(args.attacker_generations),
            attacker_population=int(args.attacker_population),
            defender_generations=int(args.defender_generations),
            defender_population=int(args.defender_population),
            seed=int(args.seed),
            eval_workers=ew,
        )
    elif args.mode == "resource_cascade":
        template = ResourceCascadeWorld(population=default_stablecoin_population(), max_steps=int(args.max_steps))
        enriched_topo = {"domain": "resource_cascade", "initial_overload": float(args.initial_overload)}
        summary = alternating_coevolution_resource_cascade(
            template,
            initial_overload=float(args.initial_overload),
            continue_after_collapse=bool(args.continue_after_collapse),
            collect_attacker_pareto=collect_pareto,
            attacker_horizon=int(args.attacker_horizon),
            rounds=int(args.rounds),
            attacker_generations=int(args.attacker_generations),
            attacker_population=int(args.attacker_population),
            defender_generations=int(args.defender_generations),
            defender_population=int(args.defender_population),
            seed=int(args.seed),
            eval_workers=ew,
        )
    elif args.mode == "service_backlog":
        template = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=int(args.max_steps))
        enriched_topo = {"domain": "service_backlog", "initial_backlog": float(args.initial_backlog)}
        summary = alternating_coevolution_service_backlog(
            template,
            initial_backlog=float(args.initial_backlog),
            continue_after_collapse=bool(args.continue_after_collapse),
            collect_attacker_pareto=collect_pareto,
            attacker_horizon=int(args.attacker_horizon),
            rounds=int(args.rounds),
            attacker_generations=int(args.attacker_generations),
            attacker_population=int(args.attacker_population),
            defender_generations=int(args.defender_generations),
            defender_population=int(args.defender_population),
            seed=int(args.seed),
            eval_workers=ew,
        )
    elif args.mode == "liquidity_ladder":
        template = LiquidityLadderWorld(population=default_stablecoin_population(), max_steps=int(args.max_steps))
        enriched_topo = {"domain": "liquidity_ladder", "initial_margin": float(args.initial_margin)}
        summary = alternating_coevolution_liquidity_ladder(
            template,
            initial_margin=float(args.initial_margin),
            continue_after_collapse=bool(args.continue_after_collapse),
            collect_attacker_pareto=collect_pareto,
            attacker_horizon=int(args.attacker_horizon),
            rounds=int(args.rounds),
            attacker_generations=int(args.attacker_generations),
            attacker_population=int(args.attacker_population),
            defender_generations=int(args.defender_generations),
            defender_population=int(args.defender_population),
            seed=int(args.seed),
            eval_workers=ew,
        )
    elif args.mode == "coupled_institution":
        try:
            from coupled_institution.world import CoupledInstitutionWorld
        except ImportError as e:
            print(
                "coupled_institution fork not installed; run: pip install -e forks/coupled_institution",
                file=sys.stderr,
            )
            raise SystemExit(2) from e
        template = CoupledInstitutionWorld(
            coupling_strength=float(args.coupling),
            max_steps=int(args.max_steps),
        )
        enriched_topo = {
            "domain": "coupled_institution",
            "coupling_strength": float(args.coupling),
            "initial_panic": float(args.initial_panic),
            "initial_overload": float(args.initial_overload),
        }
        summary = alternating_coevolution_coupled_institution(
            template,
            coupling=float(args.coupling),
            initial_panic=float(args.initial_panic),
            initial_overload=float(args.initial_overload),
            horizon=int(args.attacker_horizon),
            collect_attacker_pareto=collect_pareto,
            attacker_horizon=int(args.attacker_horizon),
            rounds=int(args.rounds),
            attacker_generations=int(args.attacker_generations),
            attacker_population=int(args.attacker_population),
            defender_generations=int(args.defender_generations),
            defender_population=int(args.defender_population),
            seed=int(args.seed),
            eval_workers=ew,
        )
    else:  # inventory_buffer
        template = InventoryBufferWorld(population=default_stablecoin_population(), max_steps=int(args.max_steps))
        enriched_topo = {"domain": "inventory_buffer", "initial_stock": float(args.initial_stock)}
        summary = alternating_coevolution_inventory_buffer(
            template,
            initial_stock=float(args.initial_stock),
            continue_after_collapse=bool(args.continue_after_collapse),
            collect_attacker_pareto=collect_pareto,
            attacker_horizon=int(args.attacker_horizon),
            rounds=int(args.rounds),
            attacker_generations=int(args.attacker_generations),
            attacker_population=int(args.attacker_population),
            defender_generations=int(args.defender_generations),
            defender_population=int(args.defender_population),
            seed=int(args.seed),
            eval_workers=ew,
        )

    payload: dict = {
        "mode": summary.simulation_mode,
        "rounds": summary.rounds,
        "best_attacker": summary.best_attacker.tolist() if summary.best_attacker is not None else None,
        "best_defender": summary.best_defender.tolist() if summary.best_defender is not None else None,
    }
    if enriched_topo is not None:
        payload["topology"] = enriched_topo

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
            "continue_after_collapse": bool(args.continue_after_collapse),
            "eval_workers": ew,
        }
        if enriched_topo is not None:
            meta["topology"] = enriched_topo
        if args.mode == "resource_cascade":
            meta["domain"] = "resource_cascade"
            meta["initial_overload"] = float(args.initial_overload)
        if args.mode == "service_backlog":
            meta["domain"] = "service_backlog"
            meta["initial_backlog"] = float(args.initial_backlog)
        if args.mode == "liquidity_ladder":
            meta["domain"] = "liquidity_ladder"
            meta["initial_margin"] = float(args.initial_margin)
        if args.mode == "inventory_buffer":
            meta["domain"] = "inventory_buffer"
            meta["initial_stock"] = float(args.initial_stock)
        if args.mode == "coupled_institution":
            meta["domain"] = "coupled_institution"
            meta["coupling_strength"] = float(args.coupling)
            meta["initial_panic"] = float(args.initial_panic)
            meta["initial_overload"] = float(args.initial_overload)
        replay["meta"] = meta
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")

    if args.export_pareto_json is not None:
        entries = flatten_coevolution_attacker_pareto(summary.rounds)
        if not entries:
            raise SystemExit(
                "No attacker Pareto points to export (try rounds >= 1, or check GA produced a non-empty archive)."
            )
        pf = pareto_front_payload_from_archive_dicts(entries, source="run_coevolution")
        args.export_pareto_json.write_text(json.dumps(pf, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
