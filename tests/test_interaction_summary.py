"""Additive summaries from attribution-merge-v1."""

from __future__ import annotations

import pytest

from fragility_engine.explain.interaction_summary import INTERACTION_SUMMARY_SCHEMA, summarize_attribution_merge
from fragility_engine.explain.merge_attribution import SCHEMA as MERGE_SCHEMA


def test_summarize_merge_sums_deltas():
    merge = {
        "schema": MERGE_SCHEMA,
        "strict_baseline": True,
        "branch_count": 2,
        "nodes": [],
        "edges": [
            {
                "from": "baseline",
                "to": "branch_0",
                "intervention": "a",
                "delta_integral_instability": -1.0,
                "delta_attack_cost": 0.5,
            },
            {
                "from": "baseline",
                "to": "branch_1",
                "intervention": "b",
                "delta_integral_instability": 2.0,
                "delta_attack_cost": -0.25,
            },
        ],
    }
    s = summarize_attribution_merge(merge)
    assert s["schema"] == INTERACTION_SUMMARY_SCHEMA
    assert s["sum_branch_delta_integral_instability"] == 1.0
    assert s["sum_branch_delta_attack_cost"] == 0.25
    assert "interaction" in s["interpretation_hint"].lower() or "joint" in s["interpretation_hint"].lower()


def test_summarize_merge_rejects_wrong_schema():
    with pytest.raises(ValueError, match="schema"):
        summarize_attribution_merge({"schema": "wrong"})


def test_summarize_bundled_triple_branch_merge_sample() -> None:
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    merge = json.loads(
        (
            root / "artifacts/attribution_viewer/sample_attribution_merge_resource_cascade_triple.json"
        ).read_text(encoding="utf-8")
    )
    s = summarize_attribution_merge(merge)
    assert s["branch_count"] == 3
    assert s["count_branches_with_integral_delta"] == 3
