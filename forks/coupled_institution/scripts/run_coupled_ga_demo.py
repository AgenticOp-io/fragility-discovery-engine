#!/usr/bin/env python3
"""GA or MC adversary on CoupledInstitutionWorld (fork; requires editable fragility-engine)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from fragility_engine.adversary.encoding import decode_schedule
    from fragility_engine.adversary.search import genetic_search, monte_carlo_search
    from fragility_engine.types import ExogenousEvent as MainEvent
    from fragility_engine.types import RolloutResult as MainRollout
    from fragility_engine.types import TrajectoryStep as MainStep
except ImportError:
    print("Install main engine: pip install -e ../../", file=sys.stderr)
    raise SystemExit(1) from None

from coupled_institution.factory import ContractName, coupling_profile_label, make_coupled_world
from coupled_institution.rollout import rollout_coupled
from coupled_institution.types import RolloutResult


def _schedule_list(genome, horizon: int):
    events_map = decode_schedule(genome)
    return [events_map.get(t, ()) for t in range(horizon)]


def _to_main_rollout(result: RolloutResult) -> MainRollout:
    traj: list[MainStep] = []
    for s in result.trajectory:
        traj.append(
            MainStep(
                timestep=s.timestep,
                state_vector=s.state_vector,
                events=tuple(MainEvent(e.kind, e.magnitude) for e in s.events),
                agent_actions_summary=dict(s.agent_actions_summary),
                metrics=dict(s.metrics),
            )
        )
    return MainRollout(
        trajectory=traj,
        collapsed=result.collapsed,
        collapse_timestep=result.collapse_timestep,
        final_instability=result.final_instability,
        seed=result.seed,
        attack_cost=result.attack_cost,
        simulation_mode=result.simulation_mode,
        integral_instability=result.integral_instability,
    )


def main() -> None:
    p = argparse.ArgumentParser(description="GA/MC on coupled_institution fork world.")
    p.add_argument("--export-replay", type=Path, default=None, help="Fork replay JSON.")
    p.add_argument("--method", choices=("ga", "mc"), default="ga")
    p.add_argument("--contract", choices=("default", "triad", "tetra"), default="default")
    p.add_argument("--generations", type=int, default=8)
    p.add_argument("--population-size", type=int, default=16)
    p.add_argument("--samples", type=int, default=40, help="MC sample count")
    p.add_argument("--seed", type=int, default=1201)
    p.add_argument("--coupling", type=float, default=0.3)
    p.add_argument("--horizon", type=int, default=14)
    args = p.parse_args()

    contract: ContractName = args.contract  # type: ignore[assignment]
    horizon = int(args.horizon)
    coupling = float(args.coupling)

    def evaluator(genome, seed: int):
        world = make_coupled_world(coupling_strength=coupling, max_steps=48, contract=contract)
        schedule = _schedule_list(genome, horizon)
        return _to_main_rollout(rollout_coupled(world, schedule, seed=seed))

    if args.method == "ga":
        search = genetic_search(
            evaluator,
            horizon=horizon,
            generations=int(args.generations),
            population_size=int(args.population_size),
            seed=int(args.seed),
        )
    else:
        search = monte_carlo_search(
            evaluator,
            horizon=horizon,
            samples=int(args.samples),
            seed=int(args.seed),
        )

    best = search.best_rollout
    payload = {
        "simulation_mode": best.simulation_mode,
        "coupling_profile": coupling_profile_label(contract),
        "contract": contract,
        "method": args.method,
        "best_fitness": float(search.best_fitness),
        "integral_instability": float(best.integral_instability),
        "collapsed": bool(best.collapsed),
        "attack_cost": float(best.attack_cost),
        "coupling_strength": coupling,
        "seed": int(args.seed),
        "horizon": horizon,
    }
    if args.method == "ga":
        payload["generations"] = int(args.generations)
        payload["population_size"] = int(args.population_size)
    else:
        payload["samples"] = int(args.samples)
    print(json.dumps(payload, indent=2))

    if args.export_replay:
        fork_result = rollout_coupled(
            make_coupled_world(coupling_strength=coupling, contract=contract),
            _schedule_list(search.best_genome, horizon),
            seed=int(args.seed) + 99,
        )
        replay = fork_result.to_replay_dict()
        replay["coupling_profile"] = coupling_profile_label(contract)
        replay["search_method"] = args.method
        args.export_replay.parent.mkdir(parents=True, exist_ok=True)
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")
        print(f"wrote {args.export_replay}", file=sys.stderr)


if __name__ == "__main__":
    main()
