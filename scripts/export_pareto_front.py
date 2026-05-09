"""Run a short GA with Pareto archiving (severity vs attack cost) and dump JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import rollout_stablecoin
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("pareto_front.json"))
    ap.add_argument("--seed", type=int, default=606)
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
                "genome": p.genome.tolist(),
            }
            for p in search.pareto_archive
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
