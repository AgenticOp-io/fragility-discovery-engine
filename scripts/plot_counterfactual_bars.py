"""Phase L — grouped bars for ``export_counterfactual`` bundles (baseline vs counterfactual snapshots).

Expects top-level **baseline** / **counterfactual** rollout snapshots with ``integral_instability`` and ``attack_cost``.

Style: ``artifacts/plot_styles/default_counterfactual_bars.json`` (**fragility-plot-counterfactual-style-v1**).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

STYLE_SCHEMA = "fragility-plot-counterfactual-style-v1"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _default_style_path() -> Path:
    return _repo_root() / "artifacts" / "plot_styles" / "default_counterfactual_bars.json"


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as e:
        raise SystemExit(str(e)) from e
    except json.JSONDecodeError as e:
        raise SystemExit(f"{path}: {e}") from e
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: expected JSON object")
    return data


def _load_style(path: Path) -> dict[str, Any]:
    style = _load_json(path)
    if style.get("schema") != STYLE_SCHEMA:
        raise SystemExit(f"{path}: expected schema {STYLE_SCHEMA}")
    return style


def extract_counterfactual_metrics(data: dict[str, Any]) -> tuple[str, float, float, float, float]:
    bs = data.get("baseline")
    cf = data.get("counterfactual")
    if not isinstance(bs, dict) or not isinstance(cf, dict):
        raise SystemExit("JSON missing baseline/counterfactual dicts")
    iv = "integral_instability"
    ac = "attack_cost"
    for label, d in ("baseline", bs), ("counterfactual", cf):
        if iv not in d or ac not in d:
            raise SystemExit(f"{label} snapshot missing {iv!r} or {ac!r}")
    intervention = str(data.get("intervention") or "unknown_intervention")
    return (
        intervention,
        float(bs[iv]),
        float(bs[ac]),
        float(cf[iv]),
        float(cf[ac]),
    )


def render_counterfactual_bars_png(data: dict[str, Any], *, style: dict[str, Any], out_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    intervention, bi, bc, vi, vc = extract_counterfactual_metrics(data)

    fig_cfg = style.get("figure") if isinstance(style.get("figure"), dict) else {}
    w = float(fig_cfg.get("width_in", 7.0))
    h = float(fig_cfg.get("height_in", 5.0))
    dpi = float(fig_cfg.get("dpi", 120))
    rc_extra = style["matplotlib_rc"] if isinstance(style.get("matplotlib_rc"), dict) else {}
    bb = style.get("baseline_bar") if isinstance(style.get("baseline_bar"), dict) else {}
    cb = style.get("counterfactual_bar") if isinstance(style.get("counterfactual_bar"), dict) else {}

    metrics = ("integral_instability", "attack_cost")
    vals_b = np.array([bi, bc], dtype=np.float64)
    vals_v = np.array([vi, vc], dtype=np.float64)
    x = np.arange(len(metrics))
    width = 0.38

    title_tpl = str(style.get("title_template", "{intervention}"))
    title = title_tpl.format(intervention=intervention)

    with plt.rc_context(rc_extra):
        fig, ax = plt.subplots(figsize=(w, h), dpi=dpi)
        ax.bar(
            x - width / 2,
            vals_b,
            width,
            label=str(bb.get("label", "baseline")),
            color=str(bb.get("color", "#1f77b4")),
            alpha=float(bb.get("alpha", 0.88)),
            edgecolor=str(bb.get("edgecolor", "#000")),
            linewidth=float(bb.get("linewidth", 0.8)),
        )
        ax.bar(
            x + width / 2,
            vals_v,
            width,
            label=str(cb.get("label", "counterfactual")),
            color=str(cb.get("color", "#ff7f0e")),
            alpha=float(cb.get("alpha", 0.88)),
            edgecolor=str(cb.get("edgecolor", "#000")),
            linewidth=float(cb.get("linewidth", 0.8)),
        )
        ax.set_xticks(x)
        ax.set_xticklabels(list(metrics))
        ax.set_ylabel(str(style.get("ylabel", "value")))
        ax.set_title(title)
        gy = style.get("grid_axisy") if isinstance(style.get("grid_axisy"), dict) else {}
        ax.grid(
            True,
            axis="y",
            alpha=float(gy.get("alpha", 0.28)),
            linestyle=str(gy.get("linestyle", ":")),
        )
        ax.legend(loc=str(style.get("legend_loc", "upper right")))
        fig.tight_layout()
        try:
            fig.savefig(out_path)
        except OSError as e:
            raise SystemExit(str(e)) from e
        plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description="Plot baseline vs counterfactual bars from export_counterfactual JSON.")
    ap.add_argument("counterfactual_json", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--style-json", type=Path, default=None)
    args = ap.parse_args()

    try:
        import matplotlib  # noqa: F401
    except ImportError:
        print("matplotlib required: pip install matplotlib  or  pip install -e '.[dev]'", file=sys.stderr)
        raise SystemExit(2)

    raw = _load_json(Path(args.counterfactual_json))
    style_path = Path(args.style_json) if args.style_json is not None else _default_style_path()
    render_counterfactual_bars_png(raw, style=_load_style(style_path), out_path=Path(args.out))


if __name__ == "__main__":
    main()
