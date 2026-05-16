"""Validate checked-in flagship bundled artifacts against live benchmark manifest pins."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fragility_engine.benchmarks.hypervolume import hypervolume_2d_min
from fragility_engine.benchmarks.manifest import build_benchmark_manifest
from fragility_engine.benchmarks.manifest_inventory import manifest_inventory_sha256

ROOT = Path(__file__).resolve().parents[1]
BUNDLED = ROOT / "artifacts" / "flagship" / "bundled"
_FLAGSHIP_PARETO_REF = (15.0, 15.0)
_FLAGSHIP_PARETO_HV = 162.26946916537284


def main() -> None:
    cert_path = BUNDLED / "fragility_certificate.json"
    pareto_path = BUNDLED / "pareto_front.json"
    replay_path = BUNDLED / "best_replay.json"
    for p in (cert_path, pareto_path, replay_path):
        if not p.is_file():
            print(f"missing: {p}", file=sys.stderr)
            raise SystemExit(1)

    live_gold = build_benchmark_manifest()["golden_metrics_sha256"]
    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    if cert.get("benchmark_golden_metrics_sha256") != live_gold:
        print("benchmark_golden_metrics_sha256 mismatch in bundled certificate", file=sys.stderr)
        raise SystemExit(1)
    if cert["benchmark_manifest"]["golden_metrics_sha256"] != live_gold:
        print("embedded benchmark_manifest golden digest mismatch", file=sys.stderr)
        raise SystemExit(1)
    live_manifest = build_benchmark_manifest()
    live_inv = manifest_inventory_sha256(live_manifest)
    if manifest_inventory_sha256(cert["benchmark_manifest"]) != live_inv:
        print("embedded benchmark_manifest inventory subset mismatch", file=sys.stderr)
        raise SystemExit(1)

    pareto = json.loads(pareto_path.read_text(encoding="utf-8"))
    ref = (pareto.get("meta") or {}).get("hypervolume_reference")
    if ref != [15.0, 15.0]:
        print(f"unexpected pareto hypervolume_reference: {ref}", file=sys.stderr)
        raise SystemExit(1)
    pts = [(float(e["severity"]), float(e["attack_cost"])) for e in pareto["archive"]]
    hv = hypervolume_2d_min(pts, _FLAGSHIP_PARETO_REF)
    if abs(hv - _FLAGSHIP_PARETO_HV) > 1e-6:
        print(f"flagship pareto hypervolume drift: {hv} != {_FLAGSHIP_PARETO_HV}", file=sys.stderr)
        raise SystemExit(1)

    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    if not replay.get("trajectory"):
        print("best_replay.json missing trajectory", file=sys.stderr)
        raise SystemExit(1)

    print("OK: flagship bundled certificate, pareto HV, and replay validated")


if __name__ == "__main__":
    main()
