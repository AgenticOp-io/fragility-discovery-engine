"""Tests for operator Intelligence Shorthand."""

from __future__ import annotations

from fragility_engine.shorthand import list_capsules, resolve_task
from fragility_engine.shorthand.resolve import export_corpus
from fragility_engine.shorthand.tiers import preferred_tier, skip_llm


def test_preferred_tier_oracle_first() -> None:
    assert preferred_tier(has_oracle=True, has_recipe=True, has_capsule=True, needs_prose=False) == "IS-T5"
    assert preferred_tier(has_oracle=False, has_recipe=True, has_capsule=True, needs_prose=False) == "IS-T4"
    assert preferred_tier(has_oracle=False, has_recipe=False, has_capsule=True, needs_prose=False) == "IS-T3"
    assert preferred_tier(has_oracle=False, has_recipe=False, has_capsule=False, needs_prose=True) == "IS-T1"


def test_resolve_validate_benchmarks() -> None:
    r = resolve_task("validate-benchmarks")
    assert r.found
    assert r.tier == "IS-T5"
    assert r.skip_llm
    assert "run_benchmark_suite" in (r.hint or "")


def test_resolve_llm_needs_prose() -> None:
    r = resolve_task("llm-prompt-bundle")
    assert r.found
    assert r.tier == "IS-T1"
    assert not r.skip_llm


def test_resolve_unknown() -> None:
    r = resolve_task("no-such-task")
    assert not r.found
    assert r.to_dict()["available_tasks"]


def test_export_corpus() -> None:
    corpus = export_corpus()
    assert corpus["kind"] == "fragility.operator.intelligence-shorthand"
    assert len(corpus["shorthands"]) == len(list_capsules())
    assert skip_llm("IS-T4")
    assert not skip_llm("IS-T1")


def test_coupled_capsules_present() -> None:
    for tid in ("coupled-validate", "coupled-regenerate", "coupled-worth-it"):
        assert resolve_task(tid).found
