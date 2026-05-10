"""Optional Numba fast path for :func:`~fragility_engine.runner.rollout_resource_cascade`.

Only enabled when:

- ``FRAGILITY_RESOURCE_CASCADE_BACKEND`` is ``numba`` or ``auto``,
- ``numba`` is importable,
- the world's agent population matches :func:`~fragility_engine.agents.stablecoin_agents.default_stablecoin_population`
  (aggregate redemption is inlined with the same formulas).

Defender genomes are allowed — they only change scalar physics parameters and initial-overload damping,
which are threaded into the kernel.

Unset or ``numpy`` keeps the reference :class:`~fragility_engine.world.resource_cascade.ResourceCascadeWorld` loop.
"""

from __future__ import annotations

import os
from typing import Literal

import numpy as np

from fragility_engine.agents.stablecoin_agents import (
    AgentPopulation,
    PanicArchetype,
    RationalArchetype,
    WhaleArchetype,
    default_stablecoin_population,
)
from fragility_engine.types import ExogenousEvent, RolloutResult, TrajectoryStep
from fragility_engine.world.resource_cascade import ResourceCascadeWorld

_NUMBA_NJIT = None
try:  # pragma: no cover - import exercised when numba installed
    from numba import njit

    _NUMBA_NJIT = njit
except ImportError:
    njit = None  # type: ignore[misc, assignment]


def resource_cascade_backend_from_env() -> Literal["numpy", "numba", "auto"]:
    raw = os.environ.get("FRAGILITY_RESOURCE_CASCADE_BACKEND", "numpy").strip().lower()
    if raw in ("", "numpy", "ref", "reference"):
        return "numpy"
    if raw == "numba":
        return "numba"
    if raw == "auto":
        return "auto"
    return "numpy"


def population_supports_resource_cascade_numba(pop: AgentPopulation) -> bool:
    """True only when aggregate redeem matches the inlined default-population kernel."""

    ref = default_stablecoin_population()
    if len(pop.archetypes) != len(ref.archetypes):
        return False
    for (w_a, a_a), (w_b, a_b) in zip(pop.archetypes, ref.archetypes, strict=True):
        if float(w_a) != float(w_b) or type(a_a) is not type(a_b):
            return False
        if isinstance(a_a, RationalArchetype) and isinstance(a_b, RationalArchetype):
            if float(a_a.backing_trigger) != float(a_b.backing_trigger):
                return False
        elif isinstance(a_a, PanicArchetype) and isinstance(a_b, PanicArchetype):
            if float(a_a.panic_slope) != float(a_b.panic_slope):
                return False
        elif isinstance(a_a, WhaleArchetype) and isinstance(a_b, WhaleArchetype):
            if float(a_a.supply_fraction) != float(a_b.supply_fraction) or float(a_a.flee_backing) != float(
                a_b.flee_backing
            ):
                return False
        else:
            return False
    return True


def schedule_to_loss_rumor_arrays(
    schedule: dict[int, tuple[ExogenousEvent, ...]],
    max_steps: int,
) -> tuple[np.ndarray, np.ndarray]:
    loss = np.zeros(max_steps, dtype=np.float64)
    rumor = np.zeros(max_steps, dtype=np.float64)
    for t, evs in schedule.items():
        if t < 0 or t >= max_steps:
            continue
        for e in evs:
            mag = float(np.clip(e.magnitude, 0.0, 1.0))
            if e.kind == "reserve_loss":
                loss[int(t)] = mag
            elif e.kind == "rumor":
                rumor[int(t)] = mag
    return loss, rumor


if _NUMBA_NJIT is not None:

    @_NUMBA_NJIT(cache=True)
    def _default_agg_redeem_numba(headroom_price: float, overload_as_panic: float) -> float:
        price = headroom_price
        panic = overload_as_panic

        if price < 0.97:
            urgency = (0.97 - price) / 0.08
            if urgency < 0.0:
                urgency = 0.0
            elif urgency > 1.0:
                urgency = 1.0
            r_rational = 0.15 + 0.85 * urgency
            if r_rational < 0.0:
                r_rational = 0.0
            elif r_rational > 1.0:
                r_rational = 1.0
        else:
            r_rational = 0.03

        base = 1.4 * panic
        if base < 0.0:
            base = 0.0
        elif base > 1.0:
            base = 1.0
        if price < 0.99:
            base = base + 0.25
            if base < 0.0:
                base = 0.0
            elif base > 1.0:
                base = 1.0
        r_panic = base
        if r_panic < 0.0:
            r_panic = 0.0
        elif r_panic > 1.0:
            r_panic = 1.0

        if price < 0.985 or panic > 0.55:
            r_whale = 0.22 * 3.6
            if r_whale < 0.0:
                r_whale = 0.0
            elif r_whale > 1.0:
                r_whale = 1.0
        else:
            r_whale = 0.02

        return 0.62 * r_rational + 0.28 * r_panic + 0.10 * r_whale

    @_NUMBA_NJIT(cache=True)
    def _resource_cascade_rollout_numba_core(
        max_steps: int,
        initial_overload: float,
        cascade_coupling: float,
        overload_decay: float,
        rumor_gain: float,
        reserve_hit_primary: float,
        reserve_hit_secondary: float,
        redeem_damage_primary: float,
        collapse_headroom: float,
        recovery_headroom: float,
        loss_mags: np.ndarray,
        rumor_mags: np.ndarray,
        continue_after_collapse: bool,
    ) -> tuple[
        int,
        bool,
        int,
        float,
        float,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]:
        price_arr = np.zeros(max_steps, dtype=np.float64)
        inst_arr = np.zeros(max_steps, dtype=np.float64)
        redeem_arr = np.zeros(max_steps, dtype=np.float64)
        h0_arr = np.zeros(max_steps, dtype=np.float64)
        h1_arr = np.zeros(max_steps, dtype=np.float64)
        ov_arr = np.zeros(max_steps, dtype=np.float64)

        peak_instability = 0.0
        integral_instability = 0.0
        collapsed = False
        collapse_timestep = -1

        h0 = 1.0
        h1 = 1.0
        overload = initial_overload

        n_out = 0
        for wall_t in range(max_steps):
            loss = loss_mags[wall_t]
            rumor = rumor_mags[wall_t]

            if loss > 0.0:
                lm = loss
                if lm > 1.0:
                    lm = 1.0
                elif lm < 0.0:
                    lm = 0.0
                h0 = h0 * (1.0 - reserve_hit_primary * lm)
                h1 = h1 * (1.0 - reserve_hit_secondary * lm)

            if rumor > 0.0:
                rm = rumor
                if rm > 1.0:
                    rm = 1.0
                elif rm < 0.0:
                    rm = 0.0
                overload = overload + rumor_gain * rm
                if overload > 1.0:
                    overload = 1.0
                elif overload < 0.0:
                    overload = 0.0

            if h0 > 1.0:
                h0 = 1.0
            elif h0 < 0.0:
                h0 = 0.0
            if h1 > 1.0:
                h1 = 1.0
            elif h1 < 0.0:
                h1 = 0.0

            damp_arg = 1.0 - cascade_coupling * (1.0 - h0) * overload
            if damp_arg < 0.25:
                damp = 0.25
            elif damp_arg > 1.0:
                damp = 1.0
            else:
                damp = damp_arg
            h1 = h1 * damp

            headroom_price = h0 if h0 < h1 else h1

            redeem = _default_agg_redeem_numba(headroom_price, overload)
            if redeem > 1.0:
                redeem = 1.0
            elif redeem < 0.0:
                redeem = 0.0

            h0 = h0 * (1.0 - redeem_damage_primary * redeem)
            if h0 > 1.0:
                h0 = 1.0
            elif h0 < 0.0:
                h0 = 0.0

            mean_shortfall = 0.5 * ((1.0 - h0) + (1.0 - h1))
            overload = overload * overload_decay + 0.05 * mean_shortfall
            if overload > 1.0:
                overload = 1.0
            elif overload < 0.0:
                overload = 0.0

            head = h0 if h0 < h1 else h1
            instability = 0.5 * (2.0 - h0 - h1) + overload
            rh_term = recovery_headroom - head
            if rh_term > 0.0:
                instability = instability + rh_term

            price_arr[wall_t] = headroom_price
            inst_arr[wall_t] = instability
            redeem_arr[wall_t] = redeem
            h0_arr[wall_t] = h0
            h1_arr[wall_t] = h1
            ov_arr[wall_t] = overload

            if instability > peak_instability:
                peak_instability = instability
            integral_instability = integral_instability + instability

            if head < collapse_headroom:
                if collapse_timestep < 0:
                    collapse_timestep = wall_t
                    collapsed = True
                if not continue_after_collapse:
                    n_out = wall_t + 1
                    return (
                        n_out,
                        collapsed,
                        collapse_timestep,
                        peak_instability,
                        integral_instability,
                        price_arr,
                        inst_arr,
                        redeem_arr,
                        h0_arr,
                        h1_arr,
                        ov_arr,
                    )

            n_out = wall_t + 1

        return (
            n_out,
            collapsed,
            collapse_timestep,
            peak_instability,
            integral_instability,
            price_arr,
            inst_arr,
            redeem_arr,
            h0_arr,
            h1_arr,
            ov_arr,
        )


def numba_rollout_resource_cascade_available() -> bool:
    return _NUMBA_NJIT is not None


def should_attempt_resource_cascade_numba(
    backend: Literal["numpy", "numba", "auto"],
    template: ResourceCascadeWorld,
) -> bool:
    if backend == "numpy":
        return False
    if not numba_rollout_resource_cascade_available():
        return False
    return population_supports_resource_cascade_numba(template.population)


def rollout_resource_cascade_numba(
    world: ResourceCascadeWorld,
    schedule: dict[int, tuple[ExogenousEvent, ...]],
    attack_cost: float,
    *,
    seed: int,
    initial_overload: float,
    reserve_boost: float,
    continue_after_collapse: bool,
) -> RolloutResult | None:
    """
    Run the inlined kernel and assemble a :class:`~fragility_engine.types.RolloutResult`.

    Returns ``None`` if Numba is unavailable (caller falls back to the reference loop).
    """

    if _NUMBA_NJIT is None:
        return None

    boost = float(np.clip(reserve_boost, 1.0, 1.5))
    eff_overload = float(np.clip(float(initial_overload) / boost, 0.0, 1.0))
    max_steps = int(world.max_steps)
    loss_mags, rumor_mags = schedule_to_loss_rumor_arrays(schedule, max_steps)

    (
        n_out,
        collapsed,
        collapse_timestep,
        peak_instability,
        integral_instability,
        price_arr,
        inst_arr,
        redeem_arr,
        h0_arr,
        h1_arr,
        ov_arr,
    ) = _resource_cascade_rollout_numba_core(
        max_steps,
        eff_overload,
        float(world.cascade_coupling),
        float(world.overload_decay),
        float(world.rumor_gain),
        float(world.reserve_hit_primary),
        float(world.reserve_hit_secondary),
        float(world.redeem_damage_primary),
        float(world.collapse_headroom),
        float(world.recovery_headroom),
        loss_mags,
        rumor_mags,
        bool(continue_after_collapse),
    )

    trajectory: list[TrajectoryStep] = []
    for wall_t in range(n_out):
        events = schedule.get(wall_t, ())
        state_vector = np.array(
            [h0_arr[wall_t], h1_arr[wall_t], ov_arr[wall_t], float(wall_t + 1)],
            dtype=np.float64,
        )
        hp = float(price_arr[wall_t])
        trajectory.append(
            TrajectoryStep(
                timestep=wall_t,
                state_vector=state_vector,
                events=events,
                agent_actions_summary={"aggregate_redeem_fraction": float(redeem_arr[wall_t])},
                metrics={
                    "price": hp,
                    "backing_ratio": hp,
                    "redeem_fraction": float(redeem_arr[wall_t]),
                    "paid_out": 0.0,
                    "instability": float(inst_arr[wall_t]),
                },
            )
        )

    ct = int(collapse_timestep) if collapsed and collapse_timestep >= 0 else None

    return RolloutResult(
        trajectory=trajectory,
        collapsed=bool(collapsed),
        collapse_timestep=ct,
        final_instability=float(peak_instability),
        seed=int(seed),
        attack_cost=float(attack_cost),
        simulation_mode="resource_cascade",
        integral_instability=float(integral_instability),
        recovery_timestep=None,
    )
