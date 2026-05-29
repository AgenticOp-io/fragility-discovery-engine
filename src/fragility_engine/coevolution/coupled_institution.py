"""Alternating co-evolution on the coupled_institution research fork (optional install)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from fragility_engine.adversary.encoding import decode_schedule
from fragility_engine.coevolution.alternating import CoevolutionSummary, alternating_coevolution_rollout
from fragility_engine.types import ExogenousEvent, RolloutResult, TrajectoryStep

if TYPE_CHECKING:
    from coupled_institution.world import CoupledInstitutionWorld


def _require_coupled_fork() -> None:
    try:
        import coupled_institution  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "coupled_institution fork not installed; run: pip install -e forks/coupled_institution"
        ) from e


def coupling_from_defender(base: float, defender_genome: np.ndarray | None) -> float:
    """Defender slot 0 dampens effective coupling (tighter defense = lower coupling)."""

    if defender_genome is None or len(defender_genome) == 0:
        return float(base)
    damp = float(np.clip(defender_genome[0], 0.0, 1.0))
    return float(np.clip(base * (1.0 - 0.35 * damp), 0.05, 0.95))


def rollout_coupled_institution(
    template: "CoupledInstitutionWorld",
    genome: np.ndarray,
    *,
    seed: int,
    defender_genome: np.ndarray | None = None,
    horizon: int = 14,
    initial_panic: float = 0.05,
    initial_overload: float = 0.05,
) -> RolloutResult:
    """Reference rollout for co-evolution — same schedule decoding as main charter domains."""

    _require_coupled_fork()
    from coupled_institution.rollout import rollout_coupled
    from coupled_institution.world import CoupledInstitutionWorld as ForkWorld

    coupling = coupling_from_defender(float(template.coupling_strength), defender_genome)
    world = ForkWorld(coupling_strength=coupling, max_steps=int(template.max_steps))
    world.reset(initial_panic=float(initial_panic), initial_overload=float(initial_overload))
    events_map = decode_schedule(genome)
    schedule = [events_map.get(t, ()) for t in range(int(horizon))]
    fork_result = rollout_coupled(world, schedule, seed=int(seed))

    traj: list[TrajectoryStep] = []
    for s in fork_result.trajectory:
        traj.append(
            TrajectoryStep(
                timestep=s.timestep,
                state_vector=s.state_vector,
                events=tuple(ExogenousEvent(e.kind, e.magnitude) for e in s.events),
                agent_actions_summary=dict(s.agent_actions_summary),
                metrics=dict(s.metrics),
            )
        )
    return RolloutResult(
        trajectory=traj,
        collapsed=fork_result.collapsed,
        collapse_timestep=fork_result.collapse_timestep,
        final_instability=fork_result.final_instability,
        seed=int(fork_result.seed),
        attack_cost=float(fork_result.attack_cost),
        simulation_mode="coupled_institution_v1",
        integral_instability=float(fork_result.integral_instability),
    )


def thread_safe_coupled_clone(template: "CoupledInstitutionWorld") -> "CoupledInstitutionWorld":
    _require_coupled_fork()
    from coupled_institution.world import CoupledInstitutionWorld as ForkWorld

    return ForkWorld(
        coupling_strength=float(template.coupling_strength),
        max_steps=int(template.max_steps),
    )


def alternating_coevolution_coupled_institution(
    template: "CoupledInstitutionWorld",
    *,
    coupling: float | None = None,
    initial_panic: float = 0.05,
    initial_overload: float = 0.05,
    horizon: int = 14,
    collect_attacker_pareto: bool = False,
    attacker_horizon: int | None = None,
    defender_genome_size: int = 4,
    rounds: int = 3,
    attacker_generations: int = 8,
    attacker_population: int = 18,
    defender_generations: int = 8,
    defender_population: int = 16,
    seed: int = 4242,
    baseline_seed_offset: int = 50_000,
    eval_workers: int = 1,
) -> CoevolutionSummary:
    """Alternating attacker/defender loop on :class:`coupled_institution.world.CoupledInstitutionWorld`."""

    _require_coupled_fork()
    from coupled_institution.world import CoupledInstitutionWorld as ForkWorld

    if coupling is not None:
        template = ForkWorld(
            coupling_strength=float(coupling),
            max_steps=int(template.max_steps),
        )
    h = int(attacker_horizon if attacker_horizon is not None else horizon)
    ew = max(1, int(eval_workers))

    def rollout_fn(g: np.ndarray, s: int, d: np.ndarray) -> RolloutResult:
        world = thread_safe_coupled_clone(template) if ew > 1 else template
        return rollout_coupled_institution(
            world,
            g,
            seed=s,
            defender_genome=d,
            horizon=h,
            initial_panic=float(initial_panic),
            initial_overload=float(initial_overload),
        )

    return alternating_coevolution_rollout(
        rollout_fn,
        attacker_horizon=h,
        defender_genome_size=defender_genome_size,
        rounds=rounds,
        attacker_generations=attacker_generations,
        attacker_population=attacker_population,
        defender_generations=defender_generations,
        defender_population=defender_population,
        seed=seed,
        baseline_seed_offset=baseline_seed_offset,
        simulation_mode="coupled_institution_v1",
        collect_attacker_pareto=collect_attacker_pareto,
        eval_workers=ew,
    )
