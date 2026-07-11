"""Replay JSON for coupled fork (schema bump; not main-engine composite v*)."""

from __future__ import annotations

from typing import Any

from coupled_institution.types import RolloutResult, TrajectoryStep

REPLAY_SCHEMA_VERSION = "coupled-fork-0.4.0"


def rollout_to_replay_dict(result: RolloutResult) -> dict[str, Any]:
    def _step_dict(s: TrajectoryStep) -> dict[str, Any]:
        return {
            "timestep": s.timestep,
            "state_vector": [float(x) for x in s.state_vector.tolist()],
            "events": [{"kind": e.kind, "magnitude": float(e.magnitude)} for e in s.events],
            "agent_actions_summary": dict(s.agent_actions_summary),
            "metrics": {k: float(v) if isinstance(v, (int, float)) else v for k, v in s.metrics.items()},
        }

    steps = len(result.trajectory)
    integral = float(result.integral_instability)
    recovery_latency = None
    if result.recovery_timestep is not None and result.collapse_timestep is not None:
        recovery_latency = int(result.recovery_timestep - result.collapse_timestep)

    return {
        "schema_version": REPLAY_SCHEMA_VERSION,
        "simulation_mode": result.simulation_mode,
        "attack_cost": float(result.attack_cost),
        "integral_instability": integral,
        "mean_instability": integral / steps if steps else 0.0,
        "steps_recorded": steps,
        "recovery_latency_steps": recovery_latency,
        "recovery_timestep": result.recovery_timestep,
        "collapsed": bool(result.collapsed),
        "collapse_timestep": result.collapse_timestep,
        "final_instability": float(result.final_instability),
        "seed": int(result.seed),
        "coupling_strength": float(result.trajectory[0].metrics.get("coupling_strength", 0.0))
        if result.trajectory
        else 0.0,
        "coupling_contract": {
            "gain_overload_to_panic": float(result.trajectory[0].metrics.get("gain_overload_to_panic", 0.0))
            if result.trajectory
            else 0.0,
            "gain_panic_to_overload": float(result.trajectory[0].metrics.get("gain_panic_to_overload", 0.0))
            if result.trajectory
            else 0.0,
            "lag_steps": int(result.trajectory[0].metrics.get("coupling_lag_steps", 0.0))
            if result.trajectory
            else 0,
            "liquidity_channels_active": bool(
                result.trajectory[0].metrics.get("liquidity_channels_active", 0.0)
            )
            if result.trajectory
            else False,
            "gain_panic_to_liquidity": float(result.trajectory[0].metrics.get("gain_panic_to_liquidity", 0.0))
            if result.trajectory
            else 0.0,
            "gain_overload_to_liquidity": float(
                result.trajectory[0].metrics.get("gain_overload_to_liquidity", 0.0)
            )
            if result.trajectory
            else 0.0,
            "gain_liquidity_scarce_to_panic": float(
                result.trajectory[0].metrics.get("gain_liquidity_scarce_to_panic", 0.0)
            )
            if result.trajectory
            else 0.0,
            "gain_liquidity_scarce_to_overload": float(
                result.trajectory[0].metrics.get("gain_liquidity_scarce_to_overload", 0.0)
            )
            if result.trajectory
            else 0.0,
            "backlog_channels_active": bool(
                result.trajectory[0].metrics.get("backlog_channels_active", 0.0)
            )
            if result.trajectory
            else False,
            "gain_panic_to_backlog": float(result.trajectory[0].metrics.get("gain_panic_to_backlog", 0.0))
            if result.trajectory
            else 0.0,
            "gain_overload_to_backlog": float(result.trajectory[0].metrics.get("gain_overload_to_backlog", 0.0))
            if result.trajectory
            else 0.0,
            "gain_backlog_to_panic": float(result.trajectory[0].metrics.get("gain_backlog_to_panic", 0.0))
            if result.trajectory
            else 0.0,
            "gain_backlog_to_overload": float(result.trajectory[0].metrics.get("gain_backlog_to_overload", 0.0))
            if result.trajectory
            else 0.0,
        },
        "trajectory": [_step_dict(s) for s in result.trajectory],
    }
