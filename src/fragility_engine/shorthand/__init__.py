"""Operator Intelligence Shorthand — Chrysalis-inspired tier ladder for FDE.

Prefer the lowest tier that still verifies. LLMs never enter ``World.step``.
See ``docs/INTELLIGENCE_SHORTHAND.md``.
"""

from __future__ import annotations

from fragility_engine.shorthand.capsules import CAPSULES, get_capsule, list_capsules
from fragility_engine.shorthand.resolve import Resolution, resolve_task
from fragility_engine.shorthand.tiers import TIER_ORDER, Tier, preferred_tier

__all__ = [
    "CAPSULES",
    "TIER_ORDER",
    "Resolution",
    "Tier",
    "get_capsule",
    "list_capsules",
    "preferred_tier",
    "resolve_task",
]
