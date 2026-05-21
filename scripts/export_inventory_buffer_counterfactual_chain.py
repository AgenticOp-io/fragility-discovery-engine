"""Export inventory-buffer counterfactual JSON.

Supports two intervention types:

``remove_steps``   Zero out specified shock timesteps (default when no shift flags given).
``initial_stock``  Re-run with a different starting stock level (--variant-initial-stock).
``demand_spike``   Re-run with a different demand-spike gain (--variant-demand-spike-gain).

At most one physics-shift variant is applied; if both shift flags are supplied the script exits
with an error.  For mutation-chain path traces across multiple cumulative physics mutations, use
the domain-specific chain modules (not yet available for inventory_buffer; use service backlog or
resource cascade as a reference for how to add one).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.explain.counterfactual import (
    compare_rollouts,
    counterfactual_bundle_to_jsonable,
    counterfactual_remove_steps_with_rollouts,
)
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_inventory_buffer, rollout_to_replay_dict
from fragility_engine.world.inventory_buffer import InventoryBufferWorld


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__ or "")
    ap.add_argument("--out", type=Path, default=Path("counterfactual_inventory_buffer.json"))
    ap.add_argument("--seed", type=int, default=424244, help="Rollout RNG seed.")
    ap.add_argument("--genome-seed", type=int, default=7)
    ap.add_argument("--horizon", type=int, default=18)
    ap.add_argument(
        "--remove-timesteps",
        type=str,
        default="",
        help="Comma-separated 0-based timestep indices to zero out (remove_steps intervention).",
    )
    ap.add_argument("--initial-stock", type=float, default=0.88, help="Baseline reset stock level [0, 1].")
    ap.add_argument(
        "--variant-initial-stock",
        type=float,
        default=None,
        help="If set, re-run counterfactual with this reset stock (initial_stock_shift intervention).",
    )
    ap.add_argument(
        "--variant-demand-spike-gain",
        type=float,
        default=None,
        help="If set, re-run counterfactual with this demand_spike_gain (demand_spike_shift intervention).",
    )
    ap.add_argument("--continue-after-collapse", action="store_true")
    ap.add_argument("--max-steps", type=int, default=40)
    ap.add_argument("--export-replay-dir", type=Path, default=None)
    args = ap.parse_args()

    if args.variant_initial_stock is not None and args.variant_demand_spike_gain is not None:
        print("Error: supply at most one of --variant-initial-stock / --variant-demand-spike-gain.", file=sys.stderr)
        raise SystemExit(2)

    rng = np.random.default_rng(int(args.genome_seed))
    genome = rng.uniform(size=(int(args.horizon), 2))
    cont = bool(args.continue_after_collapse)
    ms = max(int(args.horizon), int(args.max_steps))
    template = InventoryBufferWorld(population=default_stablecoin_population(), max_steps=ms)
    base_stock = float(args.initial_stock)

    def _rollout(g: np.ndarray, s: int) -> object:
        return rollout_inventory_buffer(
            template, g, seed=s, initial_stock=base_stock, continue_after_collapse=cont
        )

    # ── choose intervention ──────────────────────────────────────────────────
    if args.variant_initial_stock is not None:
        # Physics shift: different initial stock level.
        baseline = _rollout(genome, int(args.seed))
        variant_stock = float(args.variant_initial_stock)

        def _rollout_variant(g: np.ndarray, s: int) -> object:
            return rollout_inventory_buffer(
                template, g, seed=s, initial_stock=variant_stock, continue_after_collapse=cont
            )

        variant = _rollout_variant(genome, int(args.seed))
        report = compare_rollouts(baseline, variant, label_base="baseline", label_variant="counterfactual")
        report["intervention"] = "initial_stock_shift"
        report["baseline_initial_stock"] = base_stock
        report["variant_initial_stock"] = variant_stock
        baseline_rr, variant_rr = baseline, variant

    elif args.variant_demand_spike_gain is not None:
        # Physics shift: different demand-spike gain.
        baseline = _rollout(genome, int(args.seed))
        variant_gain = float(args.variant_demand_spike_gain)

        def _rollout_demand(g: np.ndarray, s: int) -> object:
            t = InventoryBufferWorld(
                population=default_stablecoin_population(),
                demand_spike_gain=variant_gain,
                max_steps=ms,
            )
            return rollout_inventory_buffer(t, g, seed=s, initial_stock=base_stock, continue_after_collapse=cont)

        variant = _rollout_demand(genome, int(args.seed))
        report = compare_rollouts(baseline, variant, label_base="baseline", label_variant="counterfactual")
        report["intervention"] = "demand_spike_shift"
        report["baseline_demand_spike_gain"] = template.demand_spike_gain
        report["variant_demand_spike_gain"] = variant_gain
        baseline_rr, variant_rr = baseline, variant

    else:
        # Remove steps (default): zero-out specified timesteps.
        remove_ts = [int(x.strip()) for x in args.remove_timesteps.split(",") if x.strip()]
        if not remove_ts:
            remove_ts = list(range(min(3, int(args.horizon))))  # default: first 3 steps
        report, baseline_rr, variant_rr = counterfactual_remove_steps_with_rollouts(
            genome,
            _rollout,
            remove_timesteps=remove_ts,
            base_seed=int(args.seed),
        )
        report["intervention"] = "remove_steps"

    payload = counterfactual_bundle_to_jsonable(report)
    payload["meta"] = {
        "cli": "export_inventory_buffer_counterfactual_chain",
        "base_seed": int(args.seed),
        "genome_seed": int(args.genome_seed),
        "horizon": int(args.horizon),
        "initial_stock": base_stock,
        "continue_after_collapse": cont,
    }

    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")

    if args.export_replay_dir is not None:
        args.export_replay_dir.mkdir(parents=True, exist_ok=True)
        common_meta: dict = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "export_inventory_buffer_counterfactual_chain",
            "base_seed": int(args.seed),
            "initial_stock": base_stock,
            "intervention": report.get("intervention", "remove_steps"),
            "continue_after_collapse": cont,
        }
        br = rollout_to_replay_dict(baseline_rr)
        br["meta"] = {**common_meta, "variant": "baseline"}
        vr = rollout_to_replay_dict(variant_rr)
        vr["meta"] = {**common_meta, "variant": "counterfactual"}
        (args.export_replay_dir / "baseline.json").write_text(json.dumps(br, indent=2), encoding="utf-8")
        (args.export_replay_dir / "counterfactual.json").write_text(json.dumps(vr, indent=2), encoding="utf-8")
        print(f"Wrote replays to {args.export_replay_dir}/")


if __name__ == "__main__":
    main()
