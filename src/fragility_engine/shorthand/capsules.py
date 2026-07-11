"""Static operator capsules — verified procedures, not neural weights."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from fragility_engine.shorthand.tiers import Tier


@dataclass(frozen=True)
class Capsule:
    """IS-T3-style skill capsule for FDE operator tasks."""

    task_id: str
    tier: Tier
    summary: str
    verify_command: str
    tools: tuple[str, ...]
    artifact_refs: tuple[str, ...] = ()
    skip_llm: bool = True
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["tools"] = list(self.tools)
        d["artifact_refs"] = list(self.artifact_refs)
        return d


# Curated registry — extend carefully; each entry must name a real verify path.
CAPSULES: dict[str, Capsule] = {
    "validate-benchmarks": Capsule(
        task_id="validate-benchmarks",
        tier="IS-T5",
        summary="Validate frozen Phase H golden bundles against pinned metrics.",
        verify_command="python scripts/run_benchmark_suite.py --validate",
        tools=("scripts/run_benchmark_suite.py",),
        artifact_refs=("benchmarks/", "fragility_engine.benchmarks.suite"),
    ),
    "certify-flagship": Capsule(
        task_id="certify-flagship",
        tier="IS-T5",
        summary="Emit fragility-certificate-v1 via flagship demo path.",
        verify_command="fragility certify --out-dir artifacts/flagship/output",
        tools=("fragility certify", "scripts/run_flagship_demo.py"),
        artifact_refs=("artifacts/flagship/",),
    ),
    "byow-capacity-pool": Capsule(
        task_id="byow-capacity-pool",
        tier="IS-T4",
        summary="GA search on the capacity-pool BYOW tutorial world.",
        verify_command="fragility search --example capacity-pool --generations 3 --population-size 8",
        tools=("fragility search",),
        artifact_refs=("docs/BRING_YOUR_OWN_WORLD.md",),
    ),
    "falsify-ranked-store": Capsule(
        task_id="falsify-ranked-store",
        tier="IS-T4",
        summary="Falsification search on ranked-store invariant example.",
        verify_command="fragility falsify search --example ranked-store --generations 4 --population-size 10",
        tools=("fragility falsify search",),
        artifact_refs=("docs/phase_s_falsification_harness.md",),
    ),
    "narrate-frozen-json": Capsule(
        task_id="narrate-frozen-json",
        tier="IS-T4",
        summary="Deterministic narration summary from frozen JSON (prefer before LLM).",
        verify_command="python scripts/narrate_frozen_json.py --help",
        tools=("scripts/narrate_frozen_json.py",),
        artifact_refs=("fragility_engine.explain.narration",),
        notes="For prose, escalate to IS-T1 via export_llm_narration_prompt.py — never feed output into World.step.",
    ),
    "llm-prompt-bundle": Capsule(
        task_id="llm-prompt-bundle",
        tier="IS-T1",
        summary="Export llm-prompt-bundle-v1 for external prose; stdout-only if invoked.",
        verify_command="python scripts/export_llm_narration_prompt.py --help",
        tools=("scripts/export_llm_narration_prompt.py",),
        skip_llm=False,
        notes="Documentation / reviewer assist only.",
    ),
    "coupled-validate": Capsule(
        task_id="coupled-validate",
        tier="IS-T5",
        summary="Validate coupled mega-institution fork golden bundle.",
        verify_command="python scripts/validate_coupled_fork_bundle.py",
        tools=("scripts/validate_coupled_fork_bundle.py", "forks/coupled_institution"),
        artifact_refs=("forks/coupled_institution/", "docs/FORK_COUPLING_RESEARCH.md"),
    ),
    "coupled-regenerate": Capsule(
        task_id="coupled-regenerate",
        tier="IS-T4",
        summary="Regenerate coupled fork demo artifacts and copy into viewers.",
        verify_command="python scripts/regenerate_coupled_fork_artifacts.py",
        tools=("scripts/regenerate_coupled_fork_artifacts.py",),
        artifact_refs=("artifacts/coupled_fork_demo/",),
    ),
    "coupled-worth-it": Capsule(
        task_id="coupled-worth-it",
        tier="IS-T4",
        summary="Worth-it bar: coupled vs zero-coupling / order-swap on the same schedule.",
        verify_command="python scripts/run_coupled_worth_it_bar.py",
        tools=("scripts/run_coupled_worth_it_bar.py",),
        artifact_refs=("forks/coupled_institution/CHARTER.md",),
    ),
    "coupled-tetra-search": Capsule(
        task_id="coupled-tetra-search",
        tier="IS-T5",
        summary="Pinned GA+MC search under tetra_contract (liquidity+backlog).",
        verify_command="python scripts/check_coupled_fork_tetra_search.py",
        tools=(
            "scripts/check_coupled_fork_tetra_search.py",
            "forks/coupled_institution/scripts/run_coupled_ga_demo.py",
        ),
        artifact_refs=("tests/fixtures/benchmarks/coupled_fork_tetra_search_pins.json",),
    ),
    "coupled-tetra-demo": Capsule(
        task_id="coupled-tetra-demo",
        tier="IS-T4",
        summary="Run a short tetra GA demo from the repo root.",
        verify_command=(
            "python scripts/run_coupled_fork_demo.py --contract tetra --method ga "
            "--generations 2 --population-size 8 --horizon 10 --seed 62001"
        ),
        tools=("scripts/run_coupled_fork_demo.py",),
        artifact_refs=("forks/coupled_institution/CHARTER.md",),
    ),
    "ci-local": Capsule(
        task_id="ci-local",
        tier="IS-T4",
        summary="Mirror PR CI locally (ruff + pytest + benchmark validate).",
        verify_command="powershell -File scripts/ci_local.ps1",
        tools=("scripts/ci_local.ps1", "scripts/ci_local.sh"),
        artifact_refs=("docs/NEXT_STEPS.md",),
    ),
}


def list_capsules() -> list[str]:
    return sorted(CAPSULES)


def get_capsule(task_id: str) -> Capsule | None:
    return CAPSULES.get(task_id)
