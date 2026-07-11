"""Checked-in flagship bundled artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fragility_engine.benchmarks.hypervolume import hypervolume_2d_attack_pareto

ROOT = Path(__file__).resolve().parents[1]
BUNDLED = ROOT / "artifacts" / "flagship" / "bundled"

# Pinned after attack-Pareto hypervolume fix (ref 15,15 on (-severity, attack_cost)).
_FLAGSHIP_PARETO_HV = 367.7198452205493
_FLAGSHIP_PARETO_REF = (15.0, 15.0)


def test_flagship_bundled_replay_and_pareto_exist() -> None:
    replay = BUNDLED / "best_replay.json"
    pareto = BUNDLED / "pareto_front.json"
    cert = BUNDLED / "fragility_certificate.json"
    assert replay.is_file() and pareto.is_file() and cert.is_file()
    r = json.loads(replay.read_text(encoding="utf-8"))
    p = json.loads(pareto.read_text(encoding="utf-8"))
    assert r.get("trajectory")
    assert p.get("schema") == "pareto-front-v1"
    assert p.get("archive")


def test_flagship_bundled_pareto_hypervolume() -> None:
    raw = json.loads((BUNDLED / "pareto_front.json").read_text(encoding="utf-8"))
    meta = raw.get("meta") or {}
    ref = meta.get("hypervolume_reference")
    assert ref is not None
    hv, ref_used, _nd = hypervolume_2d_attack_pareto(raw["archive"], ref=_FLAGSHIP_PARETO_REF)
    assert ref_used == _FLAGSHIP_PARETO_REF
    assert (float(ref[0]), float(ref[1])) == _FLAGSHIP_PARETO_REF
    assert hv == pytest.approx(_FLAGSHIP_PARETO_HV)


def test_flagship_bundled_certificate_manifest_digest_matches_live() -> None:
    from fragility_engine.benchmarks.manifest import build_benchmark_manifest

    cert = json.loads((BUNDLED / "fragility_certificate.json").read_text(encoding="utf-8"))
    live = build_benchmark_manifest()["golden_metrics_sha256"]
    assert cert.get("benchmark_golden_metrics_sha256") == live


def test_flagship_bundled_certificate_manifest_digest_link() -> None:
    cert = json.loads((BUNDLED / "fragility_certificate.json").read_text(encoding="utf-8"))
    assert cert.get("benchmark_golden_metrics_sha256") == cert["benchmark_manifest"]["golden_metrics_sha256"]
    assert cert.get("benchmark_bundle_ids") == cert["benchmark_manifest"]["bundle_ids"]


def test_flagship_bundled_certificate_includes_research_fork_when_present() -> None:
    cert = json.loads((BUNDLED / "fragility_certificate.json").read_text(encoding="utf-8"))
    rf = cert.get("research_fork_validation")
    if rf is None:
        return
    assert rf["status"] == "passed"
    assert rf["bundle_id"] == "coupled_institution_rollout_v1"
    assert rf.get("tetra_bundle_id") == "coupled_institution_tetra_rollout_v1"
    rows = cert.get("research_fork_artifact_sha256") or []
    assert len(rows) >= 6
    paths = {r.get("path", "") for r in rows}
    assert any(p.endswith("sample_coupled_tetra_replay.json") for p in paths)
    assert any(p.endswith("sample_coupled_pareto_tetra.json") for p in paths)
