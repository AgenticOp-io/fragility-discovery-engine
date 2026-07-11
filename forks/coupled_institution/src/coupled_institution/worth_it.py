"""Worth-it bar: coupling interaction + order sensitivity across scalar flights."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from coupled_institution.rollout import rollout_coupled
from coupled_institution.types import ExogenousEvent
from coupled_institution.world import CoupledInstitutionWorld, CouplingContract, tetra_contract, triad_contract


@dataclass(frozen=True)
class WorthItReport:
    """Compare coupled physics against controls on one pinned schedule."""

    coupled_integral: float
    zero_coupling_integral: float
    reversed_schedule_integral: float
    asymmetric_integral: float
    lag1_integral: float
    triad_integral: float
    triad_vs_twoscalar: float
    triad_reversed_integral: float
    tetra_integral: float
    tetra_vs_triad: float
    tetra_reversed_integral: float
    delta_vs_zero: float
    delta_vs_reversed: float
    worth_it: bool
    triad_worth_it: bool
    tetra_worth_it: bool
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "coupled-worth-it-bar-v3",
            "coupled_integral": self.coupled_integral,
            "zero_coupling_integral": self.zero_coupling_integral,
            "reversed_schedule_integral": self.reversed_schedule_integral,
            "asymmetric_integral": self.asymmetric_integral,
            "lag1_integral": self.lag1_integral,
            "triad_integral": self.triad_integral,
            "triad_vs_twoscalar": self.triad_vs_twoscalar,
            "triad_reversed_integral": self.triad_reversed_integral,
            "tetra_integral": self.tetra_integral,
            "tetra_vs_triad": self.tetra_vs_triad,
            "tetra_reversed_integral": self.tetra_reversed_integral,
            "delta_vs_zero": self.delta_vs_zero,
            "delta_vs_reversed": self.delta_vs_reversed,
            "worth_it": self.worth_it,
            "triad_worth_it": self.triad_worth_it,
            "tetra_worth_it": self.tetra_worth_it,
            "rationale": self.rationale,
        }


def _integral(world: CoupledInstitutionWorld, schedule: list[tuple[ExogenousEvent, ...]], seed: int) -> float:
    return float(rollout_coupled(world, schedule, seed=seed).integral_instability)


def reverse_schedule(schedule: list[tuple[ExogenousEvent, ...]]) -> list[tuple[ExogenousEvent, ...]]:
    return list(reversed(schedule))


def evaluate_worth_it(
    schedule: list[tuple[ExogenousEvent, ...]],
    *,
    seed: int = 42,
    coupling_strength: float = 0.25,
    epsilon: float = 1e-6,
) -> WorthItReport:
    """
    Two-scalar / triad / tetra worth-it: each added coupling layer must change the
    integral vs the previous layer and remain order-sensitive under schedule reversal.
    """
    coupled = CoupledInstitutionWorld(coupling_strength=coupling_strength)
    zero = CoupledInstitutionWorld(coupling_strength=0.0)
    asymmetric = CoupledInstitutionWorld(
        coupling_strength=coupling_strength,
        contract=CouplingContract(gain_overload_to_panic=0.4, gain_panic_to_overload=0.1),
    )
    lag1 = CoupledInstitutionWorld(
        coupling_strength=coupling_strength,
        contract=CouplingContract(lag_steps=1),
    )
    triad = CoupledInstitutionWorld(coupling_strength=coupling_strength, contract=triad_contract())
    tetra = CoupledInstitutionWorld(coupling_strength=coupling_strength, contract=tetra_contract())

    rev = reverse_schedule(schedule)
    i_c = _integral(coupled, schedule, seed)
    i_z = _integral(zero, schedule, seed)
    i_r = _integral(coupled, rev, seed)
    i_a = _integral(asymmetric, schedule, seed)
    i_l = _integral(lag1, schedule, seed)
    i_t = _integral(triad, schedule, seed)
    i_tr = _integral(triad, rev, seed)
    i_q = _integral(tetra, schedule, seed)
    i_qr = _integral(tetra, rev, seed)

    d_zero = i_c - i_z
    d_rev = abs(i_c - i_r)
    worth = abs(d_zero) > epsilon and d_rev > epsilon

    triad_delta = i_t - i_c
    triad_worth = abs(triad_delta) > epsilon and abs(i_t - i_tr) > epsilon

    tetra_delta = i_q - i_t
    tetra_worth = abs(tetra_delta) > epsilon and abs(i_q - i_qr) > epsilon

    bits: list[str] = []
    bits.append("two-scalar ok" if worth else "two-scalar failed")
    bits.append("liquidity triad ok" if triad_worth else "liquidity triad failed")
    bits.append("backlog tetra ok" if tetra_worth else "backlog tetra failed")

    return WorthItReport(
        coupled_integral=i_c,
        zero_coupling_integral=i_z,
        reversed_schedule_integral=i_r,
        asymmetric_integral=i_a,
        lag1_integral=i_l,
        triad_integral=i_t,
        triad_vs_twoscalar=float(triad_delta),
        triad_reversed_integral=i_tr,
        tetra_integral=i_q,
        tetra_vs_triad=float(tetra_delta),
        tetra_reversed_integral=i_qr,
        delta_vs_zero=float(d_zero),
        delta_vs_reversed=float(d_rev),
        worth_it=worth,
        triad_worth_it=triad_worth,
        tetra_worth_it=tetra_worth,
        rationale="; ".join(bits) + ".",
    )


def demo_schedule(*, horizon: int = 10, seed: int = 7) -> list[tuple[ExogenousEvent, ...]]:
    """Front-loaded reserve then late rumor — order should matter under coupling."""
    rng = np.random.default_rng(seed)
    out: list[tuple[ExogenousEvent, ...]] = []
    for t in range(horizon):
        if t < horizon // 3:
            out.append((ExogenousEvent("reserve_loss", float(rng.uniform(0.25, 0.45))),))
        elif t >= 2 * horizon // 3:
            out.append((ExogenousEvent("rumor", float(rng.uniform(0.25, 0.45))),))
        else:
            out.append(())
    return out
