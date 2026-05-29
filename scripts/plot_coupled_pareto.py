#!/usr/bin/env python3
"""Plot coupled-institution pareto-front-v1 JSON (research fork artifact)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PARETO_SCHEMA = "pareto-front-v1"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: expected JSON object")
    if data.get("schema") != PARETO_SCHEMA:
        raise SystemExit(f"{path}: expected schema {PARETO_SCHEMA!r}")
    return data


def main() -> None:
    default_in = _repo_root() / "artifacts" / "pareto_viewer" / "sample_pareto_coupled_institution.json"
    p = argparse.ArgumentParser(description="Plot coupled fork Pareto archive (severity vs attack_cost).")
    p.add_argument("pareto_json", type=Path, nargs="?", default=default_in)
    p.add_argument("--out", type=Path, default=None, help="PNG path (default: input path with .png)")
    args = p.parse_args()

    data = _load(args.pareto_json)
    arch = data.get("archive") or []
    if not arch:
        raise SystemExit("archive is empty")

    costs = [float(r["attack_cost"]) for r in arch]
    sevs = [float(r["severity"]) for r in arch]

    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise SystemExit("matplotlib required: pip install matplotlib") from e

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(costs, sevs, c="#6eb5f7", edgecolors="#fff", linewidths=0.5, s=48, zorder=3)
    ax.set_xlabel("attack_cost")
    ax.set_ylabel("severity")
    title = "Coupled institution Pareto"
    if data.get("coupling_strength") is not None:
        title += f" (c={data['coupling_strength']})"
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()

    out = args.out or args.pareto_json.with_suffix(".png")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=120)
    print(json.dumps({"out": str(out), "points": len(arch)}, indent=2))


if __name__ == "__main__":
    main()
