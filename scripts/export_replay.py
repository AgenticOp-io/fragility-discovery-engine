"""Emit `replay.json` from a deterministic rollout (engine-first artifact)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_stablecoin, rollout_to_replay_dict
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    p = argparse.ArgumentParser(description="Export rollout JSON for replay UI / tooling.")
    p.add_argument("--out", type=Path, default=Path("replay.json"))
    p.add_argument("--seed", type=int, default=12345)
    p.add_argument("--horizon", type=int, default=32)
    p.add_argument("--genome-seed", type=int, default=42, help="RNG seed constructing random genome.")
    args = p.parse_args()

    rng = np.random.default_rng(args.genome_seed)
    genome = rng.uniform(size=(args.horizon, 2))

    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=max(args.horizon, 48))
    result = rollout_stablecoin(template, genome, seed=args.seed)
    payload = rollout_to_replay_dict(result)
    payload["meta"] = {"replay_schema": REPLAY_SCHEMA_VERSION, "cli": "export_replay"}
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
