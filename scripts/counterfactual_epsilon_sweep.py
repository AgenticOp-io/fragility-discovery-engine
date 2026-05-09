"""Deterministic ε-sweep: aggregate/cascade/network scalar axes (+ optional linear trace)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.sweep import (
    sweep_aggregate_initial_panic,
    sweep_network_edge_weight,
    sweep_network_scalar_axis,
    sweep_resource_cascade_initial_overload,
)
from fragility_engine.explain.trace import linear_epsilon_sweep_to_trace
from fragility_engine.network.network_world_cli import build_stablecoin_network_world_cli
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def _parse_float_list(raw: str) -> list[float]:
    out: list[float] = []
    for part in raw.split(","):
        part = part.strip()
        if part:
            out.append(float(part))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Sweep one scalar: aggregate initial_panic, resource_cascade initial_overload, or network "
            "base_panic / contagion_beta / edge_weight on neighbor-list topology "
            "(fixed genome + rollout_seed). Optional linear explanation trace JSON."
        ),
    )
    ap.add_argument("--mode", choices=("aggregate", "network", "resource_cascade"), default="network")
    ap.add_argument(
        "--axis",
        choices=("initial_panic", "initial_overload", "base_panic", "contagion_beta", "edge_weight"),
        required=True,
    )
    ap.add_argument(
        "--values",
        type=str,
        required=True,
        help="Comma-separated floats, e.g. 0.05,0.1,0.15,0.2",
    )
    ap.add_argument("--rollout-seed", type=int, default=42424)
    ap.add_argument("--genome-seed", type=int, default=131)
    ap.add_argument("--horizon", type=int, default=14)
    ap.add_argument(
        "--base-panic",
        type=float,
        default=0.06,
        help="[network, contagion_beta] fixed reset panic. Ignored for aggregate.",
    )
    ap.add_argument(
        "--continue-after-collapse",
        action="store_true",
    )
    ap.add_argument("--nodes", type=int, default=16)
    ap.add_argument("--graph-kind", choices=("erdos_renyi", "watts_strogatz"), default="erdos_renyi")
    ap.add_argument("--er-p", type=float, default=0.12)
    ap.add_argument("--ws-k", type=int, default=6)
    ap.add_argument("--ws-p", type=float, default=0.15)
    ap.add_argument("--graph-seed", type=int, default=2027)
    ap.add_argument("--beta", type=float, default=0.36, help="[network] template contagion beta.")
    ap.add_argument("--whale-frac", type=float, default=0.22)
    ap.add_argument("--neighbor-json", type=Path, default=None)
    ap.add_argument("--neighbor-weights-json", type=Path, default=None)
    ap.add_argument(
        "--edge-from",
        type=int,
        default=None,
        help="[network, axis edge_weight] tail node (directed out-edge).",
    )
    ap.add_argument(
        "--edge-to",
        type=int,
        default=None,
        help="[network, axis edge_weight] head node.",
    )
    ap.add_argument("--out", type=Path, default=Path("epsilon_sweep.json"))
    ap.add_argument("--json-stdout", action="store_true", help="Print JSON to stdout instead of --out only.")
    ap.add_argument(
        "--emit-trace",
        action="store_true",
        help="Include explanation-trace-v1 (linear path) under key 'trace' in output JSON.",
    )
    args = ap.parse_args()

    if args.mode == "aggregate":
        if args.axis != "initial_panic":
            raise SystemExit("--mode aggregate requires --axis initial_panic.")
    elif args.mode == "resource_cascade":
        if args.axis != "initial_overload":
            raise SystemExit("--mode resource_cascade requires --axis initial_overload.")
    elif args.axis == "initial_panic":
        raise SystemExit("--axis initial_panic requires --mode aggregate.")
    elif args.axis == "initial_overload":
        raise SystemExit("--axis initial_overload requires --mode resource_cascade.")
    elif args.axis == "edge_weight":
        if args.mode != "network":
            raise SystemExit("--axis edge_weight requires --mode network.")
        if args.neighbor_json is None:
            raise SystemExit("--axis edge_weight requires --neighbor-json.")
        if args.edge_from is None or args.edge_to is None:
            raise SystemExit("--axis edge_weight requires --edge-from and --edge-to.")

    vals = _parse_float_list(args.values)
    if not vals:
        raise SystemExit("Provide at least one value in --values.")

    rng = np.random.default_rng(int(args.genome_seed))
    genome = rng.uniform(size=(int(args.horizon), 2))
    cont = bool(args.continue_after_collapse)
    topo_meta: dict | None = None

    if args.mode == "aggregate":
        template = StablecoinPegWorld(
            population=default_stablecoin_population(),
            max_steps=max(int(args.horizon), 32),
        )
        payload = sweep_aggregate_initial_panic(
            genome,
            template,
            values=vals,
            rollout_seed=int(args.rollout_seed),
            continue_after_collapse=cont,
        )
    elif args.mode == "resource_cascade":
        template = ResourceCascadeWorld(
            population=default_stablecoin_population(),
            max_steps=max(int(args.horizon), 32),
        )
        payload = sweep_resource_cascade_initial_overload(
            genome,
            template,
            values=vals,
            rollout_seed=int(args.rollout_seed),
            continue_after_collapse=cont,
        )
    else:
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
                max_steps=max(int(args.horizon), 32),
            )
        except (ValueError, OSError, json.JSONDecodeError) as e:
            print(str(e), file=sys.stderr)
            raise SystemExit(2) from e

        if args.axis == "edge_weight":
            payload = sweep_network_edge_weight(
                genome,
                template,
                edge_from=int(args.edge_from),
                edge_to=int(args.edge_to),
                values=vals,
                rollout_seed=int(args.rollout_seed),
                fixed_base_panic=float(args.base_panic),
                continue_after_collapse=cont,
            )
        else:
            payload = sweep_network_scalar_axis(
                genome,
                template,
                axis=str(args.axis),
                values=vals,
                rollout_seed=int(args.rollout_seed),
                fixed_base_panic=float(args.base_panic) if args.axis == "contagion_beta" else None,
                continue_after_collapse=cont,
            )

    payload["meta"] = {
        "cli": "counterfactual_epsilon_sweep",
        "mode": args.mode,
        "genome_seed": int(args.genome_seed),
        "horizon": int(args.horizon),
        "topology": topo_meta,
    }
    if args.emit_trace:
        payload["trace"] = linear_epsilon_sweep_to_trace(payload)

    text = json.dumps(payload, indent=2)
    args.out.write_text(text, encoding="utf-8")
    if args.json_stdout:
        print(text)


if __name__ == "__main__":
    main()
