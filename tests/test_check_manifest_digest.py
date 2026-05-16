"""Pinned golden-metrics digest guard."""

from __future__ import annotations

from pathlib import Path

from fragility_engine.benchmarks.manifest import build_benchmark_manifest

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "benchmarks" / "golden_metrics_sha256.txt"


def test_golden_metrics_sha256_matches_fixture() -> None:
    current = build_benchmark_manifest()["golden_metrics_sha256"]
    expected = FIXTURE.read_text(encoding="utf-8").strip()
    assert current == expected
