"""Deterministic sweep over base_panic or contagion_beta (network world, pinned genome + seed)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from fragility_engine.explain.sweep import sweep_network_scalar_axis
from fragility_engine.network.network_world_cli import build_stablecoin_network_world_cli


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
            "Sweep one scalar axis (base_panic or contagion_beta) with fixed genome + rollout_seed."
        ),
    )
    ap.add_argument(
        "--axis",
        choices=("base_panic", "contagion_beta"),
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
        help="For axis=contagion_beta: fixed reset panic. Ignored for base_panic axis.",
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
    ap.add_argument("--beta", type=float, default=0.36, help="Template beta (starting world).")
    ap.add_argument("--whale-frac", type=float, default=0.22)
    ap.add_argument("--neighbor-json", type=Path, default=None)
    ap.add_argument("--neighbor-weights-json", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=Path("epsilon_sweep.json"))
    ap.add_argument("--json-stdout", action="store_true", help="Print JSON to stdout instead of --out only.")
    args = ap.parse_args()

    vals = _parse_float_list(args.values)
    if not vals:
        raise SystemExit("Provide at least one value in --values.")

    rng = np.random.default_rng(int(args.genome_seed))
    genome = rng.uniform(size=(int(args.horizon), 2))

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

    payload = sweep_network_scalar_axis(
        genome,
        template,
        axis=str(args.axis),
        values=vals,
        rollout_seed=int(args.rollout_seed),
        fixed_base_panic=float(args.base_panic) if args.axis == "contagion_beta" else None,
        continue_after_collapse=bool(args.continue_after_collapse),
    )
    payload["meta"] = {
        "cli": "counterfactual_epsilon_sweep",
        "genome_seed": int(args.genome_seed),
        "horizon": int(args.horizon),
        "topology": topo_meta,
    }
    text = json.dumps(payload, indent=2)
    args.out.write_text(text, encoding="utf-8")
    if args.json_stdout:
        print(text)


if __name__ == "__main__":
    main()
