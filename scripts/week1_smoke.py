"""Week 1 — deterministic rollout smoke test (no UI, no GA)."""

from __future__ import annotations

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import rollout_stablecoin, summarize_findings
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    world = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=48)
    horizon = 48
    rng = np.random.default_rng(42)
    genome = rng.uniform(size=(horizon, 2))

    result = rollout_stablecoin(world, genome, seed=12345)
    print(summarize_findings(result))
    if result.trajectory:
        last = result.trajectory[-1]
        print("last_price=", round(last.metrics["price"], 6))


if __name__ == "__main__":
    main()
