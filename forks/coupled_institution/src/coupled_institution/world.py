"""Coupled peg panic + cascade overload + liquidity + backlog (fork; not main charter).

v0.4 adds backlog scalar ``B`` (opt-in; default off → golden preserved).
v0.3 liquidity ``L``; v0.2 CouplingContract; v0.1 two-scalar baseline.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from coupled_institution.types import ExogenousEvent, TrajectoryStep


@dataclass(frozen=True)
class CouplingContract:
    """Explicit coupling channels — gains are dimensionless toy knobs.

    Liquidity / backlog channels default to **0** so the pinned golden is unchanged.
    Use ``triad_contract()`` / ``tetra_contract()`` for mega-institution flights.

    ``lag_steps``:
      * ``0`` — sequential within step: panic → overload → liquidity → backlog.
      * ``1`` — channels read previous-timestep partner states only.
    """

    gain_overload_to_panic: float | None = None
    gain_panic_to_overload: float | None = None
    lag_steps: int = 0
    shock_reserve_to_panic: float = 0.4
    shock_rumor_to_overload: float = 0.35
    # --- liquidity (v0.3); default off ---
    gain_panic_to_liquidity: float = 0.0
    gain_overload_to_liquidity: float = 0.0
    gain_liquidity_scarce_to_panic: float = 0.0
    gain_liquidity_scarce_to_overload: float = 0.0
    shock_reserve_to_liquidity: float = 0.0
    shock_rumor_to_liquidity: float = 0.0
    include_liquidity_in_instability: bool = False
    liquidity_collapse_floor: float | None = None
    # --- backlog (v0.4); default off ---
    gain_panic_to_backlog: float = 0.0
    gain_overload_to_backlog: float = 0.0
    gain_backlog_to_panic: float = 0.0
    gain_backlog_to_overload: float = 0.0
    gain_liquidity_scarce_to_backlog: float = 0.0
    shock_rumor_to_backlog: float = 0.0
    include_backlog_in_instability: bool = False
    backlog_collapse_ceiling: float | None = None  # collapse if B >= ceiling when set

    def resolved_gains(self, coupling_strength: float) -> tuple[float, float]:
        g_op = float(self.gain_overload_to_panic if self.gain_overload_to_panic is not None else coupling_strength)
        g_po = float(self.gain_panic_to_overload if self.gain_panic_to_overload is not None else coupling_strength)
        return g_op, g_po

    def liquidity_active(self) -> bool:
        return any(
            abs(float(x)) > 0.0
            for x in (
                self.gain_panic_to_liquidity,
                self.gain_overload_to_liquidity,
                self.gain_liquidity_scarce_to_panic,
                self.gain_liquidity_scarce_to_overload,
                self.shock_reserve_to_liquidity,
                self.shock_rumor_to_liquidity,
            )
        )

    def backlog_active(self) -> bool:
        return any(
            abs(float(x)) > 0.0
            for x in (
                self.gain_panic_to_backlog,
                self.gain_overload_to_backlog,
                self.gain_backlog_to_panic,
                self.gain_backlog_to_overload,
                self.gain_liquidity_scarce_to_backlog,
                self.shock_rumor_to_backlog,
            )
        )


def triad_contract(*, lag_steps: int = 0) -> CouplingContract:
    """Non-zero liquidity channels for the v0.3 worth-it / demo path."""
    return CouplingContract(
        lag_steps=lag_steps,
        gain_panic_to_liquidity=0.15,
        gain_overload_to_liquidity=0.12,
        gain_liquidity_scarce_to_panic=0.22,
        gain_liquidity_scarce_to_overload=0.18,
        shock_reserve_to_liquidity=0.25,
        shock_rumor_to_liquidity=0.15,
        include_liquidity_in_instability=True,
        liquidity_collapse_floor=0.02,
    )


def tetra_contract(*, lag_steps: int = 0) -> CouplingContract:
    """Liquidity triad plus backlog channels (v0.4 mega-institution flight)."""
    return replace(
        triad_contract(lag_steps=lag_steps),
        gain_panic_to_backlog=0.14,
        gain_overload_to_backlog=0.16,
        gain_backlog_to_panic=0.12,
        gain_backlog_to_overload=0.15,
        gain_liquidity_scarce_to_backlog=0.2,
        shock_rumor_to_backlog=0.22,
        include_backlog_in_instability=True,
        backlog_collapse_ceiling=1.0,
    )


@dataclass
class CoupledInstitutionWorld:
    """
    Four scalars: panic ``P``, overload ``O``, liquidity ``L``, backlog ``B``.

    Toy coupling — not calibrated. Liquidity/backlog channels default off.
    """

    coupling_strength: float = 0.25
    max_steps: int = 20
    contract: CouplingContract | None = None
    _P: float = 0.05
    _O: float = 0.05
    _L: float = 1.0
    _B: float = 0.05
    _t: int = 0
    _P_prev: float = 0.05
    _O_prev: float = 0.05
    _L_prev: float = 1.0
    _B_prev: float = 0.05

    def __post_init__(self) -> None:
        if self.contract is None:
            self.contract = CouplingContract()

    def reset(
        self,
        *,
        initial_panic: float = 0.05,
        initial_overload: float = 0.05,
        initial_liquidity: float = 1.0,
        initial_backlog: float = 0.05,
    ) -> None:
        self._P = float(initial_panic)
        self._O = float(initial_overload)
        self._L = float(initial_liquidity)
        self._B = float(initial_backlog)
        self._P_prev = float(initial_panic)
        self._O_prev = float(initial_overload)
        self._L_prev = float(initial_liquidity)
        self._B_prev = float(initial_backlog)
        self._t = 0

    def state_vector(self) -> np.ndarray:
        return np.array(
            [self._P, self._O, self._L, self._B, 0.5 * (self._P + self._O), float(self._t)],
            dtype=np.float64,
        )

    def instability_score(self) -> float:
        assert self.contract is not None
        c = self.contract
        if c.include_liquidity_in_instability or c.include_backlog_in_instability:
            scarce = max(0.0, 1.0 - self._L)
            w_p, w_o, w_s, w_b = 0.35, 0.35, 0.15, 0.15
            if not c.include_liquidity_in_instability:
                w_s = 0.0
                w_p, w_o = 0.425, 0.425
            if not c.include_backlog_in_instability:
                w_b = 0.0
                if c.include_liquidity_in_instability:
                    w_p, w_o, w_s = 0.4, 0.4, 0.2
                else:
                    return float(0.5 * self._P + 0.5 * self._O)
            return float(w_p * self._P + w_o * self._O + w_s * scarce + w_b * self._B)
        return float(0.5 * self._P + 0.5 * self._O)

    def is_collapsed(self) -> bool:
        assert self.contract is not None
        if self._P >= 1.0 or self._O >= 1.0:
            return True
        floor = self.contract.liquidity_collapse_floor
        if floor is not None and self._L <= float(floor):
            return True
        ceil = self.contract.backlog_collapse_ceiling
        if ceil is not None and self._B >= float(ceil):
            return True
        return False

    def step(self, events: tuple[ExogenousEvent, ...], rng: np.random.Generator) -> TrajectoryStep:
        assert self.contract is not None
        reserve_loss = 0.0
        rumor = 0.0
        for ev in events:
            if ev.kind == "reserve_loss":
                reserve_loss += float(np.clip(ev.magnitude, 0.0, 1.0))
            elif ev.kind == "rumor":
                rumor += float(np.clip(ev.magnitude, 0.0, 1.0))

        g_op, g_po = self.contract.resolved_gains(self.coupling_strength)
        lag = int(self.contract.lag_steps)
        c = self.contract

        p_before = self._P
        o_before = self._O
        l_before = self._L
        b_before = self._B

        if lag <= 0:
            scarce = max(0.0, 1.0 - l_before)
            coupling_to_p = (
                g_op * o_before
                + float(c.gain_liquidity_scarce_to_panic) * scarce
                + float(c.gain_backlog_to_panic) * b_before
            )
            self._P = p_before + c.shock_reserve_to_panic * reserve_loss + coupling_to_p
            coupling_to_o = (
                g_po * self._P
                + float(c.gain_liquidity_scarce_to_overload) * scarce
                + float(c.gain_backlog_to_overload) * b_before
            )
            self._O = o_before + c.shock_rumor_to_overload * rumor + coupling_to_o
            drain = (
                float(c.gain_panic_to_liquidity) * self._P
                + float(c.gain_overload_to_liquidity) * self._O
                + float(c.shock_reserve_to_liquidity) * reserve_loss
                + float(c.shock_rumor_to_liquidity) * rumor
            )
            coupling_to_l = -drain
            self._L = l_before + coupling_to_l
            scarce_after = max(0.0, 1.0 - self._L)
            coupling_to_b = (
                float(c.gain_panic_to_backlog) * self._P
                + float(c.gain_overload_to_backlog) * self._O
                + float(c.gain_liquidity_scarce_to_backlog) * scarce_after
                + float(c.shock_rumor_to_backlog) * rumor
            )
            self._B = b_before + coupling_to_b
        else:
            scarce = max(0.0, 1.0 - self._L_prev)
            coupling_to_p = (
                g_op * self._O_prev
                + float(c.gain_liquidity_scarce_to_panic) * scarce
                + float(c.gain_backlog_to_panic) * self._B_prev
            )
            coupling_to_o = (
                g_po * self._P_prev
                + float(c.gain_liquidity_scarce_to_overload) * scarce
                + float(c.gain_backlog_to_overload) * self._B_prev
            )
            self._P = p_before + c.shock_reserve_to_panic * reserve_loss + coupling_to_p
            self._O = o_before + c.shock_rumor_to_overload * rumor + coupling_to_o
            drain = (
                float(c.gain_panic_to_liquidity) * self._P_prev
                + float(c.gain_overload_to_liquidity) * self._O_prev
                + float(c.shock_reserve_to_liquidity) * reserve_loss
                + float(c.shock_rumor_to_liquidity) * rumor
            )
            coupling_to_l = -drain
            self._L = l_before + coupling_to_l
            coupling_to_b = (
                float(c.gain_panic_to_backlog) * self._P_prev
                + float(c.gain_overload_to_backlog) * self._O_prev
                + float(c.gain_liquidity_scarce_to_backlog) * scarce
                + float(c.shock_rumor_to_backlog) * rumor
            )
            self._B = b_before + coupling_to_b

        self._P += 0.02 * float(rng.normal())
        self._O += 0.02 * float(rng.normal())
        if c.liquidity_active():
            self._L += 0.01 * float(rng.normal())
        if c.backlog_active():
            self._B += 0.01 * float(rng.normal())
        self._P = float(np.clip(self._P, 0.0, 2.0))
        self._O = float(np.clip(self._O, 0.0, 2.0))
        self._L = float(np.clip(self._L, 0.0, 2.0))
        self._B = float(np.clip(self._B, 0.0, 2.0))

        self._P_prev = self._P
        self._O_prev = self._O
        self._L_prev = self._L
        self._B_prev = self._B

        metrics = {
            "price": self._P,
            "backing_ratio": 1.0 - 0.5 * self._O,
            "panic": self._P,
            "overload": self._O,
            "liquidity": self._L,
            "backlog": self._B,
            "liquidity_scarce": float(max(0.0, 1.0 - self._L)),
            "instability": self.instability_score(),
            "coupling_strength": float(self.coupling_strength),
            "gain_overload_to_panic": float(g_op),
            "gain_panic_to_overload": float(g_po),
            "gain_panic_to_liquidity": float(c.gain_panic_to_liquidity),
            "gain_overload_to_liquidity": float(c.gain_overload_to_liquidity),
            "gain_liquidity_scarce_to_panic": float(c.gain_liquidity_scarce_to_panic),
            "gain_liquidity_scarce_to_overload": float(c.gain_liquidity_scarce_to_overload),
            "gain_panic_to_backlog": float(c.gain_panic_to_backlog),
            "gain_overload_to_backlog": float(c.gain_overload_to_backlog),
            "gain_backlog_to_panic": float(c.gain_backlog_to_panic),
            "gain_backlog_to_overload": float(c.gain_backlog_to_overload),
            "coupling_lag_steps": float(lag),
            "coupling_contrib_to_panic": float(coupling_to_p),
            "coupling_contrib_to_overload": float(coupling_to_o),
            "coupling_contrib_to_liquidity": float(coupling_to_l),
            "coupling_contrib_to_backlog": float(coupling_to_b),
            "shock_contrib_to_panic": float(c.shock_reserve_to_panic * reserve_loss),
            "shock_contrib_to_overload": float(c.shock_rumor_to_overload * rumor),
            "shock_contrib_to_liquidity": float(
                -(c.shock_reserve_to_liquidity * reserve_loss + c.shock_rumor_to_liquidity * rumor)
            ),
            "shock_contrib_to_backlog": float(c.shock_rumor_to_backlog * rumor),
            "liquidity_channels_active": 1.0 if c.liquidity_active() else 0.0,
            "backlog_channels_active": 1.0 if c.backlog_active() else 0.0,
        }
        t = self._t
        self._t += 1
        return TrajectoryStep(
            timestep=t,
            state_vector=self.state_vector(),
            events=events,
            agent_actions_summary={"redeem_fraction": 0.0},
            metrics=metrics,
        )

    def step_shocks(self, reserve_loss: float = 0.0, rumor: float = 0.0) -> dict[str, float]:
        events: tuple[ExogenousEvent, ...] = ()
        if reserve_loss > 0:
            events += (ExogenousEvent("reserve_loss", float(reserve_loss)),)
        if rumor > 0:
            events += (ExogenousEvent("rumor", float(rumor)),)
        row = self.step(events, np.random.default_rng(0))
        return {
            "timestep": float(row.timestep),
            "panic": self._P,
            "overload": self._O,
            "liquidity": self._L,
            "backlog": self._B,
            "instability": float(row.metrics["instability"]),
            "coupling_contrib_to_panic": float(row.metrics["coupling_contrib_to_panic"]),
            "coupling_contrib_to_overload": float(row.metrics["coupling_contrib_to_overload"]),
            "coupling_contrib_to_liquidity": float(row.metrics["coupling_contrib_to_liquidity"]),
            "coupling_contrib_to_backlog": float(row.metrics["coupling_contrib_to_backlog"]),
        }


def coupled_rollout_snapshot(*, steps: int = 8, seed: int = 0) -> dict[str, object]:
    from coupled_institution.rollout import random_schedule, rollout_coupled

    world = CoupledInstitutionWorld()
    sched = random_schedule(steps, seed=seed)
    result = rollout_coupled(world, sched, seed=seed)
    out = result.to_replay_dict()
    out["collapsed"] = result.collapsed
    return out
