"""Checked-in flagship bundled artifacts."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLED = ROOT / "artifacts" / "flagship" / "bundled"


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
