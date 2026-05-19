"""Phase L — bar chart of per-branch integral instability from institutional composite JSON (v1–v3)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

STYLE_SCHEMA = "fragility-plot-institutional-composite-style-v1"
BRANCH_ORDER = ("aggregate", "network", "resource_cascade", "service_backlog", "liquidity_ladder")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _default_style_path() -> Path:
    return _repo_root() / "artifacts" / "plot_styles" / "default_institutional_composite_bars.json"


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: expected JSON object")
    return data


def extract_branch_integrals(data: dict[str, Any]) -> list[tuple[str, float, bool]]:
    schema = str(data.get("schema", ""))
    if not schema.startswith("fragility-institutional-composite-v"):
        raise SystemExit(f"unsupported composite schema {schema!r}")
    rows: list[tuple[str, float, bool]] = []
    for key in BRANCH_ORDER:
        branch = data.get(key)
        if not isinstance(branch, dict):
            continue
        rows.append((key, float(branch.get("integral_instability", 0.0)), bool(branch.get("collapsed"))))
    if not rows:
        raise SystemExit("no branch metrics found in composite JSON")
    return rows


def render_composite_bars_png(data: dict[str, Any], *, style: dict[str, Any], out_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = extract_branch_integrals(data)
    labels = [r[0] for r in rows]
    values = [r[1] for r in rows]
    colors = [style.get("collapsed_color", "#c44") if r[2] else style.get("bar_color", "#48a") for r in rows]

    fig, ax = plt.subplots(figsize=(float(style.get("width", 8)), float(style.get("height", 4.5))))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel(str(style.get("y_label", "integral_instability")))
    ax.set_title(str(style.get("title", "Institutional composite branches")))
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=int(style.get("dpi", 120)))
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("composite_json", type=Path, help="fragility-institutional-composite-v1/v2/v3 JSON.")
    ap.add_argument("--out", type=Path, default=Path("composite_branches.png"))
    ap.add_argument("--style", type=Path, default=None)
    args = ap.parse_args()

    style_path = args.style or _default_style_path()
    style = _load_json(style_path)
    if style.get("schema") != STYLE_SCHEMA:
        raise SystemExit(f"{style_path}: expected schema {STYLE_SCHEMA}")
    data = _load_json(args.composite_json)
    render_composite_bars_png(data, style=style, out_path=args.out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
