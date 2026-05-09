"""Alternating attacker/defender evolution (aggregate world)."""

from __future__ import annotations

import json

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution import alternating_coevolution
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=40)
    summary = alternating_coevolution(
        template,
        attacker_horizon=16,
        rounds=2,
        attacker_generations=6,
        attacker_population=14,
        defender_generations=6,
        defender_population=12,
        seed=131,
    )
    payload = {
        "rounds": summary.rounds,
        "best_attacker": summary.best_attacker.tolist() if summary.best_attacker is not None else None,
        "best_defender": summary.best_defender.tolist() if summary.best_defender is not None else None,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
