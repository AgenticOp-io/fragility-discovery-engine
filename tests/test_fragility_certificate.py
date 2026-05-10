from __future__ import annotations

from pathlib import Path

from fragility_engine.benchmarks.certificate import (
    FRAGILITY_CERTIFICATE_SCHEMA,
    build_fragility_certificate,
)


def test_build_fragility_certificate_schema_and_self_hash(tmp_path: Path) -> None:
    p = tmp_path / "x.json"
    p.write_text('{"a":1}', encoding="utf-8")
    c = build_fragility_certificate(artifact_paths=[p], include_benchmark_manifest=False, notes="unit test")
    assert c["schema"] == FRAGILITY_CERTIFICATE_SCHEMA
    assert len(c["artifact_sha256"]) == 1
    assert "certificate_content_sha256" in c
    assert len(c["certificate_content_sha256"]) == 64


def test_build_fragility_certificate_roundtrip_deterministic(tmp_path: Path) -> None:
    p = tmp_path / "y.json"
    p.write_text('{"k":"v"}', encoding="utf-8")
    a = build_fragility_certificate(artifact_paths=[p], include_benchmark_manifest=False)
    b = build_fragility_certificate(artifact_paths=[p], include_benchmark_manifest=False)
    assert a["certificate_content_sha256"] == b["certificate_content_sha256"]
    assert a["artifact_sha256"] == b["artifact_sha256"]
