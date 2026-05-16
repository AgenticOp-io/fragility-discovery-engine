"""Bundled quad composite JSON for narration demos."""

from __future__ import annotations

import json
from pathlib import Path

from fragility_engine.explain.narration import narrate_frozen_artifact

SAMPLE = Path(__file__).resolve().parents[1] / "artifacts" / "composite_demo" / "sample_quad_composite.json"


def test_sample_quad_composite_schema_and_narration() -> None:
    data = json.loads(SAMPLE.read_text(encoding="utf-8"))
    assert data["schema"] == "fragility-institutional-composite-v3"
    for branch in ("aggregate", "network", "resource_cascade", "service_backlog"):
        assert branch in data
    text = narrate_frozen_artifact(data, source=str(SAMPLE))
    assert "institutional composite" in text
    assert "service_backlog" in text
