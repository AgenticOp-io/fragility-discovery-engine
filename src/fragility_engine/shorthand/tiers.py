"""FDE Intelligence Shorthand tiers (adapted from Chrysalis IS-T5…T0)."""

from __future__ import annotations

from typing import Literal

Tier = Literal["IS-T5", "IS-T4", "IS-T3", "IS-T2", "IS-T1", "IS-T0"]

TIER_ORDER: tuple[Tier, ...] = ("IS-T5", "IS-T4", "IS-T3", "IS-T2", "IS-T1", "IS-T0")

TIER_BLURB: dict[Tier, str] = {
    "IS-T5": "Oracle / golden — frozen bundle or certificate; no LLM",
    "IS-T4": "Deterministic policy — CLI recipe / script; no LLM",
    "IS-T3": "Skill capsule — verify-gated procedure digest; no LLM when hit",
    "IS-T2": "Domain adapter (reserved; not used on main)",
    "IS-T1": "Optional LLM narration of frozen JSON only",
    "IS-T0": "General model — last resort; never drives simulation",
}


def preferred_tier(*, has_oracle: bool, has_recipe: bool, has_capsule: bool, needs_prose: bool) -> Tier:
    """Selection rule: lowest tier that covers the task."""
    if has_oracle and not needs_prose:
        return "IS-T5"
    if has_recipe and not needs_prose:
        return "IS-T4"
    if has_capsule and not needs_prose:
        return "IS-T3"
    if needs_prose:
        return "IS-T1"
    return "IS-T0"


def skip_llm(tier: Tier) -> bool:
    return tier in ("IS-T5", "IS-T4", "IS-T3")
