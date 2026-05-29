"""Pin 2-D minimization hypervolume on bundled Pareto viewer samples (non-flagship)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fragility_engine.benchmarks.hypervolume import hypervolume_2d_min, nondominated_points_min

ROOT = Path(__file__).resolve().parents[1]
PARETO_VIEWER = ROOT / "artifacts" / "pareto_viewer"
FIXTURE = ROOT / "tests" / "fixtures" / "benchmarks" / "bundled_pareto_hypervolume_pins.json"

_PINNED_SAMPLES = (
    "sample_pareto_front.json",
    "sample_pareto_resource_cascade.json",
    "sample_pareto_service_backlog.json",
    "sample_pareto_network.json",
    "sample_pareto_liquidity_ladder.json",
    "sample_pareto_coupled_institution.json",
)


def _compute_pin(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    meta = obj.get("meta") or {}
    ref = meta.get("hypervolume_reference")
    arch = obj.get("archive") or []
    pts = [(float(e["severity"]), float(e["attack_cost"])) for e in arch]
    nd = nondominated_points_min(pts)
    if not nd:
        raise ValueError(f"empty archive: {path}")
    if ref is None:
        ref = [
            max(s for s, _ in nd) * 1.15 + 0.01,
            max(a for _, a in nd) * 1.15 + 0.01,
        ]
    ref_t = (float(ref[0]), float(ref[1]))
    hv = hypervolume_2d_min(nd, ref_t)
    return {
        "hypervolume_reference": [ref_t[0], ref_t[1]],
        "expected_hypervolume": float(hv),
    }


def main() -> None:
    if not FIXTURE.is_file():
        print(f"missing fixture: {FIXTURE}", file=sys.stderr)
        raise SystemExit(1)
    expected_all = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for name in _PINNED_SAMPLES:
        rel = f"artifacts/pareto_viewer/{name}"
        path = PARETO_VIEWER / name
        if not path.is_file():
            print(f"missing: {rel}", file=sys.stderr)
            raise SystemExit(1)
        current = _compute_pin(path)
        expected = expected_all.get(name)
        if expected is None:
            print(f"missing pin entry for {name}", file=sys.stderr)
            raise SystemExit(1)
        if current != expected:
            print(
                f"hypervolume pin mismatch for {name}:\n"
                f"  expected: {expected}\n"
                f"  current:  {current}\n"
                f"Update {FIXTURE.relative_to(ROOT)} if intentional.",
                file=sys.stderr,
            )
            raise SystemExit(1)
    print(f"OK: {len(_PINNED_SAMPLES)} bundled Pareto hypervolume pins")


if __name__ == "__main__":
    main()
