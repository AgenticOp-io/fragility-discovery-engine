"""PROV-lite evidence packs wrapping fragility certificates and artifact digests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fragility_engine.benchmarks.certificate import (
    FRAGILITY_CERTIFICATE_SCHEMA,
    build_fragility_certificate,
    digest_json_files,
    sha256_bytes,
)
from fragility_engine.fel.conventions import FEL_VERSION

EVIDENCE_PACK_SCHEMA = "evidence-pack-v1"


def build_evidence_pack(
    *,
    artifact_paths: list[Path] | None = None,
    certificate: dict[str, Any] | None = None,
    include_benchmark_manifest: bool = True,
    activity_label: str = "fragility_evidence_assembly",
    notes: str = "",
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Assemble a PROV-lite pack: entities (artifacts) + one activity + optional certificate."""

    paths = list(artifact_paths or [])
    if certificate is None:
        certificate = build_fragility_certificate(
            artifact_paths=paths or None,
            include_benchmark_manifest=include_benchmark_manifest,
            repo_root=repo_root,
            notes=notes or "Evidence pack auto-built certificate.",
        )
    digests = digest_json_files(paths, repo_root=repo_root) if paths else list(
        certificate.get("artifact_sha256") or []
    )

    entities: list[dict[str, Any]] = []
    for i, row in enumerate(digests):
        path = str(row.get("path", f"artifact_{i}"))
        schema_guess = _schema_guess(path)
        entities.append(
            {
                "id": f"entity-{i + 1}",
                "prov:type": "Entity",
                "path": path,
                "sha256": row.get("sha256"),
                "schema": schema_guess,
            }
        )

    cert_id = "entity-certificate"
    entities.append(
        {
            "id": cert_id,
            "prov:type": "Entity",
            "schema": FRAGILITY_CERTIFICATE_SCHEMA,
            "sha256": certificate.get("certificate_content_sha256"),
        }
    )

    activity = {
        "id": "activity-1",
        "prov:type": "Activity",
        "label": activity_label,
        "generated": [e["id"] for e in entities],
        "used": [e["id"] for e in entities if e["id"] != cert_id],
    }

    pack: dict[str, Any] = {
        "schema": EVIDENCE_PACK_SCHEMA,
        "fel_version": FEL_VERSION,
        "prov_profile": "prov-lite-v1",
        "entities": entities,
        "activities": [activity],
        "certificate": certificate,
    }
    if notes.strip():
        pack["notes"] = notes.strip()
    body = {k: v for k, v in pack.items() if k != "pack_content_sha256"}
    pack["pack_content_sha256"] = sha256_bytes(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    return pack


def _schema_guess(path: str) -> str:
    p = path.replace("\\", "/").lower()
    if "pareto" in p:
        return "pareto-front-v1"
    if "scenario-archive" in p or "scenario_archive" in p:
        return "scenario-archive-v1"
    if "differential" in p:
        return "differential-stress-v1"
    if "certificate" in p:
        return FRAGILITY_CERTIFICATE_SCHEMA
    if "replay" in p:
        return "replay"
    return "json-artifact"
