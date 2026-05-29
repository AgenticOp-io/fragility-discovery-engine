"""Contract for bundled coupled-institution Pareto sample."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PARETO = REPO / "artifacts" / "pareto_viewer" / "sample_pareto_coupled_institution.json"
DEMO_COPY = REPO / "artifacts" / "coupled_fork_demo" / "sample_coupled_pareto_front.json"


def test_bundled_coupled_pareto_schema() -> None:
    obj = json.loads(PARETO.read_text(encoding="utf-8"))
    assert obj.get("schema") == "pareto-front-v1"
    assert obj.get("domain") == "coupled_institution"
    assert obj.get("simulation_mode") == "coupled_institution_v1"
    arch = obj.get("archive")
    assert isinstance(arch, list) and len(arch) >= 1
    row = arch[0]
    assert "severity" in row and "attack_cost" in row
    assert "integral_instability" in row


def test_coupled_fork_demo_pareto_matches_viewer_sample() -> None:
    assert DEMO_COPY.is_file(), "run scripts/regenerate_coupled_fork_artifacts.py"
    a = json.loads(PARETO.read_text(encoding="utf-8"))
    b = json.loads(DEMO_COPY.read_text(encoding="utf-8"))
    assert a["schema"] == b["schema"]
    assert len(a["archive"]) == len(b["archive"])
