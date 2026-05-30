"""Pin 2-D attack-Pareto hypervolume on bundled Pareto viewer samples (non-flagship)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fragility_engine.benchmarks.hypervolume import hypervolume_2d_attack_pareto

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
    ref_raw = meta.get("hypervolume_reference")
    ref = None
    if ref_raw is not None:
        ref = (float(ref_raw[0]), float(ref_raw[1]))
    arch = obj.get("archive") or []
    hv, ref_t, _nd = hypervolume_2d_attack_pareto(arch, ref=ref)
    return {
        "hypervolume_reference": [ref_t[0], ref_t[1]],
        "expected_hypervolume": float(hv),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--write-pins",
        action="store_true",
        help="Rewrite bundled_pareto_hypervolume_pins.json from current artifacts.",
    )
    args = ap.parse_args()

    if args.write_pins:
        out: dict[str, dict] = {}
        for name in _PINNED_SAMPLES:
            path = PARETO_VIEWER / name
            if not path.is_file():
                print(f"missing: {path}", file=sys.stderr)
                raise SystemExit(1)
            out[name] = _compute_pin(path)
        FIXTURE.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {FIXTURE.relative_to(ROOT)}")
        return

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
                f"Update with: python scripts/check_bundled_pareto_hypervolume.py --write-pins",
                file=sys.stderr,
            )
            raise SystemExit(1)
    print(f"OK: {len(_PINNED_SAMPLES)} bundled Pareto hypervolume pins")


if __name__ == "__main__":
    main()
