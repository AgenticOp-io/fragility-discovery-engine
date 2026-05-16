"""Canonical benchmark-manifest inventory digest for CI drift detection."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def manifest_inventory_subset(manifest: dict[str, Any]) -> dict[str, Any]:
    """Stable JSON-serializable subset: bundle list, integral bands, golden digest."""

    return {
        "schema": manifest.get("schema"),
        "bundle_ids": list(manifest.get("bundle_ids") or []),
        "bundle_count": manifest.get("bundle_count"),
        "bundle_integral_bands": manifest.get("bundle_integral_bands"),
        "golden_metrics_sha256": manifest.get("golden_metrics_sha256"),
    }


def manifest_inventory_sha256(manifest: dict[str, Any]) -> str:
    blob = json.dumps(manifest_inventory_subset(manifest), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
