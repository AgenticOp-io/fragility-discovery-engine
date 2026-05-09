from __future__ import annotations

from typing import Any

import numpy as np

from fragility_engine.adversary.encoding import decode_schedule, schedule_attack_cost
from fragility_engine.types import RolloutResult, TrajectoryStep
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld

REPLAY_SCHEMA_VERSION = "0.2.0"


def rollout_stablecoin(
    world_template: StablecoinPegWorld,
    genome: np.ndarray,
    *,
    seed: int,
    initial_reserves: float = 1_000_000.0,
    initial_supply: float = 1_000_000.0,
    initial_panic: float = 0.05,
) -> RolloutResult:
    """
    Deterministic given seed: clones behavioral RNG each step from master sequence.

    World + agents are reset per evaluation so searches remain side-effect free.
    """

    world = StablecoinPegWorld(
        population=world_template.population,
        depeg_threshold=world_template.depeg_threshold,
        panic_decay=world_template.panic_decay,
        rumor_panic_gain=world_template.rumor_panic_gain,
        max_steps=world_template.max_steps,
    )
    world.reset(initial_reserves=initial_reserves, initial_supply=initial_supply, initial_panic=initial_panic)
    world.population.reset(initial_supply=initial_supply, rng=np.random.default_rng(seed ^ 0x9E3779B9))

    schedule = decode_schedule(genome)
    attack_cost = schedule_attack_cost(schedule)

    trajectory: list[TrajectoryStep] = []
    collapsed = False
    collapse_timestep: int | None = None
    peak_instability = 0.0

    for t in range(world.max_steps):
        events = schedule.get(t, ())
        step_rng = np.random.default_rng(seed + 17 * (t + 1))
        step = world.step(events, step_rng)
        trajectory.append(step)
        inst = world.instability_score()
        peak_instability = max(peak_instability, inst)
        if world.is_collapsed():
            collapsed = True
            collapse_timestep = t
            break

    return RolloutResult(
        trajectory=trajectory,
        collapsed=collapsed,
        collapse_timestep=collapse_timestep,
        final_instability=peak_instability,
        seed=seed,
        attack_cost=attack_cost,
        simulation_mode="aggregate",
    )


def rollout_stablecoin_network(
    world_template: StablecoinNetworkWorld,
    genome: np.ndarray,
    *,
    seed: int,
    initial_reserves: float = 1_000_000.0,
    initial_supply: float = 1_000_000.0,
    base_panic: float = 0.05,
) -> RolloutResult:
    """Graph contagion variant — panic vector diffuses before redemption aggregation."""

    world = StablecoinNetworkWorld(
        population=world_template.population,
        adjacency=world_template.adjacency,
        node_weights=world_template.node_weights,
        contagion_beta=world_template.contagion_beta,
        depeg_threshold=world_template.depeg_threshold,
        panic_decay=world_template.panic_decay,
        rumor_panic_gain=world_template.rumor_panic_gain,
        max_steps=world_template.max_steps,
    )
    world.reset(initial_reserves=initial_reserves, initial_supply=initial_supply, base_panic=base_panic)
    world.population.reset(initial_supply=initial_supply, rng=np.random.default_rng(seed ^ 0x9E3779B9))

    schedule = decode_schedule(genome)
    attack_cost = schedule_attack_cost(schedule)

    trajectory: list[TrajectoryStep] = []
    collapsed = False
    collapse_timestep: int | None = None
    peak_instability = 0.0

    for t in range(world.max_steps):
        events = schedule.get(t, ())
        step_rng = np.random.default_rng(seed + 17 * (t + 1))
        step = world.step(events, step_rng)
        trajectory.append(step)
        inst = world.instability_score()
        peak_instability = max(peak_instability, inst)
        if world.is_collapsed():
            collapsed = True
            collapse_timestep = t
            break

    return RolloutResult(
        trajectory=trajectory,
        collapsed=collapsed,
        collapse_timestep=collapse_timestep,
        final_instability=peak_instability,
        seed=seed,
        attack_cost=attack_cost,
        simulation_mode="network",
    )


def rollout_to_replay_dict(result: RolloutResult) -> dict[str, Any]:
    """Serializable artifact for a future timeline UI."""

    def _step_dict(s: TrajectoryStep) -> dict[str, Any]:
        return {
            "timestep": s.timestep,
            "state_vector": s.state_vector.tolist(),
            "events": [{"kind": e.kind, "magnitude": e.magnitude} for e in s.events],
            "agent_actions_summary": dict(s.agent_actions_summary),
            "metrics": dict(s.metrics),
        }

    return {
        "schema_version": REPLAY_SCHEMA_VERSION,
        "simulation_mode": result.simulation_mode,
        "attack_cost": result.attack_cost,
        "collapsed": result.collapsed,
        "collapse_timestep": result.collapse_timestep,
        "final_instability": result.final_instability,
        "seed": result.seed,
        "trajectory": [_step_dict(s) for s in result.trajectory],
    }


def summarize_findings(result: RolloutResult) -> str:
    lines = [
        f"mode={result.simulation_mode}",
        f"attack_cost={result.attack_cost:.4f}",
        f"collapsed={result.collapsed}",
        f"collapse_timestep={result.collapse_timestep}",
        f"peak_instability={result.final_instability:.4f}",
        f"horizon_steps={len(result.trajectory)}",
    ]
    return "\n".join(lines)
