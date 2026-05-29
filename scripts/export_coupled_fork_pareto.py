#!/usr/bin/env python3
"""Export a small GA Pareto archive for the coupled_institution research fork."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORK_ART = ROOT / "forks" / "coupled_institution" / "artifacts"
DEFAULT_OUT = ROOT / "artifacts" / "pareto_viewer" / "sample_pareto_coupled_institution.json"


def _repo_root() -> Path:
    return ROOT


def main() -> None:
    try:
        from fragility_engine.adversary.encoding import decode_schedule
        from fragility_engine.adversary.search import genetic_search
        from fragility_engine.types import ExogenousEvent as MainEvent
        from fragility_engine.types import RolloutResult as MainRollout
        from fragility_engine.types import TrajectoryStep as MainStep
    except ImportError as e:
        raise SystemExit("Install main engine: pip install -e .") from e

    try:
        from coupled_institution.rollout import rollout_coupled
        from coupled_institution.types import RolloutResult
        from coupled_institution.world import CoupledInstitutionWorld
    except ImportError as e:
        raise SystemExit("Install fork: pip install -e forks/coupled_institution") from e

    p = argparse.ArgumentParser(description="Export coupled fork pareto-front-v1 JSON.")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--coupling", type=float, default=0.3)
    p.add_argument("--horizon", type=int, default=10)
    p.add_argument("--generations", type=int, default=2)
    p.add_argument("--population-size", type=int, default=10)
    p.add_argument("--seed", type=int, default=61001)
    p.add_argument("--also-fork-artifacts", action="store_true", help="Copy to forks/.../artifacts/")
    args = p.parse_args()

    coupling = float(args.coupling)
    horizon = int(args.horizon)
    template = CoupledInstitutionWorld(coupling_strength=coupling, max_steps=48)

    def _schedule_list(genome, h: int):
        events_map = decode_schedule(genome)
        return [events_map.get(t, ()) for t in range(h)]

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

    def evaluator(genome, seed: int):
        world = CoupledInstitutionWorld(
            coupling_strength=template.coupling_strength,
            max_steps=template.max_steps,
        )
        schedule = _schedule_list(genome, horizon)
        return _to_main_rollout(rollout_coupled(world, schedule, seed=seed))

    search = genetic_search(
        evaluator,
        horizon=horizon,
        generations=int(args.generations),
        population_size=int(args.population_size),
        seed=int(args.seed),
        collect_pareto=True,
    )

    payload = {
        "schema": "pareto-front-v1",
        "domain": "coupled_institution",
        "simulation_mode": search.best_rollout.simulation_mode,
        "coupling_strength": coupling,
        "best_fitness": float(search.best_fitness),
        "archive": [
            {
                "severity": float(pt.severity),
                "attack_cost": float(pt.attack_cost),
                "collapsed": bool(pt.collapsed),
                "integral_instability": float(pt.integral_instability),
                "genome": pt.genome.tolist(),
            }
            for pt in search.pareto_archive
        ],
    }
    if not payload["archive"]:
        raise SystemExit("Pareto archive empty — increase population or generations")

    out = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    try:
        out_rel = out.resolve().relative_to(_repo_root().resolve()).as_posix()
    except ValueError:
        out_rel = str(out.resolve())
    print(json.dumps({"out": out_rel, "points": len(payload["archive"])}, indent=2))

    if args.also_fork_artifacts:
        fork_out = FORK_ART / "sample_coupled_pareto_front.json"
        fork_out.parent.mkdir(parents=True, exist_ok=True)
        fork_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"also wrote {fork_out.relative_to(_repo_root())}", file=sys.stderr)


if __name__ == "__main__":
    main()
