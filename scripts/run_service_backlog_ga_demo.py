"""Phase M — tiny GA + minimization on ServiceBacklogWorld (same schedule encoding as stablecoin / cascade)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution.thread_safe_template import thread_safe_service_backlog_clone
from fragility_engine.explain.minimal_collapse import minimize_schedule_with_rollout
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_service_backlog, rollout_to_replay_dict
from fragility_engine.world.service_backlog import ServiceBacklogWorld


def main() -> None:
    p = argparse.ArgumentParser(description="GA adversary on ServiceBacklogWorld (Phase M third domain).")
    p.add_argument("--export-replay", type=Path, default=None, help="Write best-rollout replay JSON.")
    p.add_argument(
        "--export-minimized-replay",
        type=Path,
        default=None,
        help="Greedy-minimized replay if best collapses.",
    )
    p.add_argument("--generations", type=int, default=10)
    p.add_argument("--population-size", type=int, default=20)
    p.add_argument("--seed", type=int, default=808)
    p.add_argument("--initial-backlog", type=float, default=0.06, help="Reset backlog (non-negative).")
    p.add_argument(
        "--eval-workers",
        type=int,
        default=1,
        help="Thread pool size for GA fitness evaluation (clone per eval when >1).",
    )
    args = p.parse_args()

    template = ServiceBacklogWorld(population=default_stablecoin_population(), max_steps=36)
    horizon = 18
    ew = max(1, int(args.eval_workers))

    def ga_evaluator(genome, seed: int):
        world = thread_safe_service_backlog_clone(template) if ew > 1 else template
        return rollout_service_backlog(
            world,
            genome,
            seed=seed,
            initial_backlog=float(args.initial_backlog),
        )

    def minimize_evaluator(genome, seed: int):
        return rollout_service_backlog(
            template,
            genome,
            seed=seed,
            initial_backlog=float(args.initial_backlog),
        )

    search = genetic_search(
        ga_evaluator,
        horizon=horizon,
        generations=int(args.generations),
        population_size=int(args.population_size),
        seed=int(args.seed),
        eval_workers=ew,
    )

    print("best_fitness=", round(search.best_fitness, 5))
    print("attack_cost=", round(search.best_rollout.attack_cost, 5))
    print("collapsed=", search.best_rollout.collapsed, "at", search.best_rollout.collapse_timestep)

    min_seed = 515151
    minimized, min_rollout = minimize_schedule_with_rollout(search.best_genome, minimize_evaluator, base_seed=min_seed)
    print("minimization=", json.dumps(minimized, indent=2)[:1200])

    replay = rollout_to_replay_dict(search.best_rollout)
    print("replay_steps=", len(replay["trajectory"]), "mode=", replay["simulation_mode"])

    common_meta = {
        "replay_schema": REPLAY_SCHEMA_VERSION,
        "cli": "run_service_backlog_ga_demo",
        "domain": "service_backlog",
        "generations": int(args.generations),
        "population_size": int(args.population_size),
        "horizon": horizon,
        "ga_seed": int(args.seed),
        "initial_backlog": float(args.initial_backlog),
        "eval_workers": ew,
    }

    if args.export_replay is not None:
        replay["meta"] = {**common_meta, "variant": "best_ga"}
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")

    if args.export_minimized_replay is not None:
        if min_rollout is None:
            print(
                "Skipping --export-minimized-replay: baseline did not collapse.",
                file=sys.stderr,
            )
        else:
            mr = rollout_to_replay_dict(min_rollout)
            mr["meta"] = {
                **common_meta,
                "variant": "greedy_minimized_schedule",
                "minimize_base_seed": min_seed,
            }
            args.export_minimized_replay.write_text(json.dumps(mr, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
