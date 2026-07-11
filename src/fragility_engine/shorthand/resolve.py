"""Runtime resolve: task_id → tier + capsule + skip_llm (Chrysalis protocol pattern)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fragility_engine.shorthand.capsules import Capsule, get_capsule, list_capsules
from fragility_engine.shorthand.tiers import TIER_BLURB, Tier, preferred_tier, skip_llm


@dataclass(frozen=True)
class Resolution:
    task_id: str
    found: bool
    tier: Tier | None
    skip_llm: bool
    capsule: Capsule | None
    blurb: str
    hint: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "fragility.operator.intelligence-shorthand",
            "schema_version": "fde-shorthand-v1",
            "task_id": self.task_id,
            "found": self.found,
            "tier": self.tier,
            "skip_llm": self.skip_llm,
            "blurb": self.blurb,
            "hint": self.hint,
            "capsule": self.capsule.to_dict() if self.capsule else None,
            "available_tasks": list_capsules() if not self.found else None,
        }


def resolve_task(task_id: str, *, needs_prose: bool = False) -> Resolution:
    """Resolve an operator task to the preferred shorthand tier."""
    cap = get_capsule(task_id)
    if cap is None:
        return Resolution(
            task_id=task_id,
            found=False,
            tier=None,
            skip_llm=False,
            capsule=None,
            blurb="",
            hint=f"Unknown task. Known: {', '.join(list_capsules())}",
        )

    has_oracle = cap.tier == "IS-T5"
    has_recipe = cap.tier in ("IS-T5", "IS-T4")
    has_capsule = True
    tier = preferred_tier(
        has_oracle=has_oracle,
        has_recipe=has_recipe,
        has_capsule=has_capsule,
        needs_prose=needs_prose or not cap.skip_llm,
    )
    # Capsule author tier wins when prose not forced and capsule is lower-or-equal cost
    if not needs_prose and cap.skip_llm:
        tier = cap.tier

    return Resolution(
        task_id=task_id,
        found=True,
        tier=tier,
        skip_llm=skip_llm(tier),
        capsule=cap,
        blurb=TIER_BLURB[tier],
        hint=cap.verify_command,
    )


def export_corpus() -> dict[str, Any]:
    """Export all capsules as a Chrysalis-style shorthand corpus document."""
    return {
        "kind": "fragility.operator.intelligence-shorthand",
        "schema_version": "fde-shorthand-v1",
        "provenance": [
            "Adapted from Chrysalis Intelligence Shorthand (IS-T5…T0): models propose; "
            "deterministic verify / golden dispose. Never feed LLM output into World.step."
        ],
        "tiers": {t: TIER_BLURB[t] for t in ("IS-T5", "IS-T4", "IS-T3", "IS-T2", "IS-T1", "IS-T0")},
        "shorthands": [c.to_dict() for c in (get_capsule(k) for k in list_capsules()) if c],
    }
