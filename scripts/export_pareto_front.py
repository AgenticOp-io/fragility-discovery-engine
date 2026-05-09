"""Run a short GA with Pareto archiving (severity vs attack cost) and dump JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_stablecoin, rollout_to_replay_dict
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    ap = argparse.ArgumentParser(description="Pareto archive dump + optional replay export.")
    ap.add_argument("--out", type=Path, default=Path("pareto_front.json"))
    ap.add_argument("--seed", type=int, default=606)
    ap.add_argument("--export-replay", type=Path, default=None, help="Export one rollout as replay JSON.")
    ap.add_argument(
        "--replay-pareto-index",
        type=int,
        default=None,
        help="Export pareto_archive[index] rollout (re-evaluated); default is best-fitness rollout.",
    )
    args = ap.parse_args()

    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=36)

    def evaluator(genome: np.ndarray, seed: int):
        return rollout_stablecoin(template, genome, seed=seed)

    search = genetic_search(
        evaluator,
        horizon=18,
        generations=10,
        population_size=22,
        seed=args.seed,
        collect_pareto=True,
    )

    payload = {
        "schema": "pareto-front-v1",
        "best_fitness": search.best_fitness,
        "archive": [
            {
                "severity": p.severity,
                "attack_cost": p.attack_cost,
                "collapsed": p.collapsed,
                "integral_instability": p.integral_instability,
                "genome": p.genome.tolist(),
            }
            for p in search.pareto_archive
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.export_replay is not None:
        if args.replay_pareto_index is not None:
            idx = int(args.replay_pareto_index)
            arch = search.pareto_archive
            if idx < 0 or idx >= len(arch):
                raise SystemExit(f"--replay-pareto-index in [0, {len(arch) - 1}] (got {idx}).")
            rr = evaluator(arch[idx].genome, args.seed + 40_000 + idx)
            meta_extra = {"pareto_index": idx, "severity": arch[idx].severity, "attack_cost": arch[idx].attack_cost}
        else:
            rr = search.best_rollout
            meta_extra = {"source": "best_fitness"}
        replay = rollout_to_replay_dict(rr)
        replay["meta"] = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "export_pareto_front",
            "pareto_front_seed": args.seed,
            **meta_extra,
        }
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
