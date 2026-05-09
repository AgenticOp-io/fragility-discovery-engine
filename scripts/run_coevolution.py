"""Alternating attacker/defender evolution (aggregate world)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution import alternating_coevolution
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_to_replay_dict
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def main() -> None:
    p = argparse.ArgumentParser(description="Alternating attacker/defender GA on aggregate peg world.")
    p.add_argument(
        "--export-replay",
        type=Path,
        default=None,
        help="Write final probe rollout as replay JSON (same seed stack as last training round).",
    )
    args = p.parse_args()

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

    if args.export_replay is not None:
        if summary.last_rollout is None:
            raise SystemExit("Coevolution produced no rollout (try rounds >= 1).")
        replay = rollout_to_replay_dict(summary.last_rollout)
        replay["meta"] = {
            "replay_schema": REPLAY_SCHEMA_VERSION,
            "cli": "run_coevolution",
            "coevolution_rounds": len(summary.rounds),
        }
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
