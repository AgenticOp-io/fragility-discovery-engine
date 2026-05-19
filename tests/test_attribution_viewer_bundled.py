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


def test_bundled_resource_cascade_chain_path_trace() -> None:
    p = ATTR / "sample_resource_cascade_chain_coupling_rumor.json"
    obj = json.loads(p.read_text(encoding="utf-8"))
    assert obj.get("intervention") == "resource_cascade_mutation_chain"
    assert obj["path_trace"]["schema"] == "explanation-mutation-chain-path-resource-cascade-v1"


def test_bundled_aggregate_chain_path_trace() -> None:
    p = ATTR / "sample_aggregate_chain_rumor_depeg.json"
    obj = json.loads(p.read_text(encoding="utf-8"))
    assert obj.get("intervention") == "aggregate_mutation_chain"
    assert obj["path_trace"]["schema"] == "explanation-mutation-chain-path-aggregate-v1"


def test_bundled_service_backlog_chain_path_trace() -> None:
    p = ATTR / "sample_service_backlog_chain_process_ingest.json"
    obj = json.loads(p.read_text(encoding="utf-8"))
    assert obj.get("intervention") == "service_backlog_mutation_chain"
    assert obj["path_trace"]["schema"] == "explanation-mutation-chain-path-service-backlog-v1"


def test_bundled_liquidity_ladder_chain_path_trace() -> None:
    p = ATTR / "sample_liquidity_ladder_chain_margin_haircut.json"
    obj = json.loads(p.read_text(encoding="utf-8"))
    assert obj.get("intervention") == "liquidity_ladder_mutation_chain"
    assert obj["path_trace"]["schema"] == "explanation-mutation-chain-path-liquidity-ladder-v1"


def test_bundled_liquidity_ladder_merge_attribution_schema() -> None:
    p = ATTR / "sample_attribution_merge_liquidity_ladder.json"
    obj = json.loads(p.read_text(encoding="utf-8"))
    assert obj.get("schema") == "attribution-merge-v1"
    assert obj.get("branch_count") == 2
    assert obj.get("strict_baseline") is True
