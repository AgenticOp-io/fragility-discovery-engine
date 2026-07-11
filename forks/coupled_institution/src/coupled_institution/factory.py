"""World factory helpers for default / triad / tetra coupling profiles."""

from __future__ import annotations

from typing import Literal

from coupled_institution.world import CoupledInstitutionWorld, tetra_contract, triad_contract

ContractName = Literal["default", "triad", "tetra"]


def make_coupled_world(
    *,
    coupling_strength: float = 0.25,
    max_steps: int = 48,
    contract: ContractName = "default",
) -> CoupledInstitutionWorld:
    if contract == "default":
        return CoupledInstitutionWorld(coupling_strength=float(coupling_strength), max_steps=int(max_steps))
    if contract == "triad":
        return CoupledInstitutionWorld(
            coupling_strength=float(coupling_strength),
            max_steps=int(max_steps),
            contract=triad_contract(),
        )
    if contract == "tetra":
        return CoupledInstitutionWorld(
            coupling_strength=float(coupling_strength),
            max_steps=int(max_steps),
            contract=tetra_contract(),
        )
    raise ValueError(f"unknown contract {contract!r}; expected default|triad|tetra")


def coupling_profile_label(contract: ContractName) -> str:
    return {
        "default": "two_scalar",
        "triad": "liquidity_triad",
        "tetra": "backlog_tetra",
    }[contract]
