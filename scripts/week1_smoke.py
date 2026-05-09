"""Week 1 — deterministic rollout smoke test (no UI, no GA)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import (
    REPLAY_SCHEMA_VERSION,
    rollout_stablecoin,
    rollout_to_replay_dict,
    summarize_findings,
)
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    p = argparse.ArgumentParser(description="Deterministic rollout smoke.")
    p.add_argument("--export-replay", type=Path, default=None, help="Write this rollout as replay JSON.")
    p.add_argument("--initial-panic", type=float, default=0.05)
    p.add_argument("--continue-after-collapse", action="store_true")
    args = p.parse_args()

    world = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=48)
    horizon = 48
    rng = np.random.default_rng(42)
    genome = rng.uniform(size=(horizon, 2))

    result = rollout_stablecoin(
        world,
        genome,
        seed=12345,
        initial_panic=float(args.initial_panic),
        continue_after_collapse=bool(args.continue_after_collapse),
    )
    print(summarize_findings(result))
    if result.trajectory:
        last = result.trajectory[-1]
        print("last_price=", round(last.metrics["price"], 6))

    if args.export_replay is not None:
        replay = rollout_to_replay_dict(result)
        replay["meta"] = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "week1_smoke",
            "initial_panic": float(args.initial_panic),
        }
        if args.continue_after_collapse:
            replay["meta"]["continue_after_collapse"] = True
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
