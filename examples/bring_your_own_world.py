"""Thin CLI wrapper — canonical world lives in ``fragility_engine.byow.examples.capacity_pool``."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fragility_engine.adversary.encoding import decode_schedule
from fragility_engine.adversary.search import genetic_search
from fragility_engine.byow.examples.capacity_pool import make_world, rollout
from fragility_engine.explain.minimal_collapse import minimize_schedule_with_rollout
from fragility_engine.runner import rollout_to_replay_dict, summarize_findings


def main() -> None:
    p = argparse.ArgumentParser(description="BYOW tutorial: capacity pool (see docs/BRING_YOUR_OWN_WORLD.md).")
    p.add_argument("--generations", type=int, default=12)
    p.add_argument("--population-size", type=int, default=24)
    p.add_argument("--seed", type=int, default=411)
    p.add_argument("--horizon", type=int, default=16)
    p.add_argument("--export-replay", type=Path, default=None)
    args = p.parse_args()

    world = make_world()

    def evaluator(genome, seed: int):
        return rollout(world, genome, seed)

    search = genetic_search(
        evaluator,
        horizon=int(args.horizon),
        generations=int(args.generations),
        population_size=int(args.population_size),
        seed=int(args.seed),
    )

    print("=== best schedule found ===")
    print(summarize_findings(search.best_rollout))
    for t, events in sorted(decode_schedule(search.best_genome).items()):
        for e in events:
            print(f"  t={t:>2}  {e.kind:<12} mag={e.magnitude:.3f}")

    minimized, min_rollout = minimize_schedule_with_rollout(search.best_genome, evaluator, base_seed=515151)
    if min_rollout is not None:
        kept = minimized.get("minimal_events_by_timestep", {})
        print(f"minimized: {len(kept)} shock timesteps")

    if args.export_replay is not None:
        replay = rollout_to_replay_dict(search.best_rollout)
        replay["meta"] = {"cli": "examples/bring_your_own_world", "example": "capacity-pool"}
        args.export_replay.parent.mkdir(parents=True, exist_ok=True)
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")
        print(f"wrote {args.export_replay}")


if __name__ == "__main__":
    main()
