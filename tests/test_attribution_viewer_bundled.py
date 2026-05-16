"""Bundled attribution viewer JSON samples."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTR = ROOT / "artifacts" / "attribution_viewer"


def test_bundled_network_chain_has_path_trace() -> None:
    p = ATTR / "sample_network_chain_contagion_base_panic.json"
    obj = json.loads(p.read_text(encoding="utf-8"))
    assert obj.get("intervention") == "network_mutation_chain"
    pt = obj.get("path_trace") or {}
    assert pt.get("schema") == "explanation-mutation-chain-path-v1"
    assert pt.get("variant_base_panic") == 0.14


def test_bundled_triple_interaction_summary() -> None:
    p = ATTR / "sample_triple_interaction_summary.json"
    obj = json.loads(p.read_text(encoding="utf-8"))
    assert obj.get("schema") == "attribution-interaction-summary-v1"
    assert obj.get("branch_count") == 3
