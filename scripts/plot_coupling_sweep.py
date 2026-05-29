#!/usr/bin/env python3
"""Plot coupled-institution coupling_strength sweep JSON (fork research artifact)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SWEEP_SCHEMA = "coupled-institution-coupling-sweep-v1"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: expected JSON object")
    if data.get("schema") != SWEEP_SCHEMA:
        raise SystemExit(f"{path}: expected schema {SWEEP_SCHEMA!r}")
    return data


def main() -> None:
    default_in = _repo_root() / "forks" / "coupled_institution" / "artifacts" / "coupling_strength_sweep.json"
    p = argparse.ArgumentParser(description="Plot coupling_strength vs integral instability.")
    p.add_argument("sweep_json", type=Path, nargs="?", default=default_in)
    p.add_argument("--out", type=Path, default=None, help="PNG path (default: sweep path with .png)")
    args = p.parse_args()

    data = _load(args.sweep_json)
    rows = data.get("rows") or []
    if not rows:
        raise SystemExit("sweep has no rows")

    xs = [float(r["coupling_strength"]) for r in rows]
    ys = [float(r["integral_instability"]) for r in rows]

    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise SystemExit("matplotlib required: pip install matplotlib") from e

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(xs, ys, marker="o", color="#6eb5f7")
    ax.set_xlabel("coupling_strength")
    ax.set_ylabel("integral_instability")
    ax.set_title("Coupled institution (pinned schedule)")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()

    out = args.out or args.sweep_json.with_suffix(".png")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=120)
    print(json.dumps({"out": str(out), "points": len(xs)}, indent=2))


if __name__ == "__main__":
    main()
