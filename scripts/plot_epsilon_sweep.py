"""Phase L — plot ``counterfactual-epsilon-sweep-v1`` JSON (axis vs integral instability).

Style contract: ``artifacts/plot_styles/default_epsilon_sweep.json`` (**fragility-plot-epsilon-sweep-style-v1**).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SWEEP_SCHEMA = "counterfactual-epsilon-sweep-v1"
STYLE_SCHEMA = "fragility-plot-epsilon-sweep-style-v1"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _default_style_path() -> Path:
    return _repo_root() / "artifacts" / "plot_styles" / "default_epsilon_sweep.json"


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


def extract_sweep_series(data: dict[str, Any]) -> tuple[str, list[float], list[float], list[bool]]:
    if data.get("schema") != SWEEP_SCHEMA:
        raise SystemExit(f"expected schema {SWEEP_SCHEMA!r}")
    axis = data.get("axis")
    if not isinstance(axis, str) or not axis:
        raise SystemExit("sweep JSON missing string axis")
    runs = data.get("runs")
    if not isinstance(runs, list) or not runs:
        raise SystemExit("sweep JSON missing non-empty runs")

    xs: list[float] = []
    ys: list[float] = []
    collapsed: list[bool] = []
    for i, row in enumerate(runs):
        if not isinstance(row, dict):
            raise SystemExit(f"runs[{i}] must be an object")
        if axis not in row:
            raise SystemExit(f"runs[{i}] missing axis field {axis!r}")
        iv = row.get("integral_instability")
        if iv is None:
            raise SystemExit(f"runs[{i}] missing integral_instability")
        xs.append(float(row[axis]))
        ys.append(float(iv))
        collapsed.append(bool(row.get("collapsed")))

    order = sorted(range(len(xs)), key=lambda k: (xs[k], k))
    xs = [xs[i] for i in order]
    ys = [ys[i] for i in order]
    collapsed = [collapsed[i] for i in order]
    return axis, xs, ys, collapsed


def render_epsilon_sweep_png(
    sweep: dict[str, Any],
    *,
    style: dict[str, Any],
    out_path: Path,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    axis, xs, ys, collapsed = extract_sweep_series(sweep)

    fig_cfg = style.get("figure") if isinstance(style.get("figure"), dict) else {}
    w = float(fig_cfg.get("width_in", 8.5))
    h = float(fig_cfg.get("height_in", 4.5))
    dpi = float(fig_cfg.get("dpi", 120))
    rc_extra = style["matplotlib_rc"] if isinstance(style.get("matplotlib_rc"), dict) else {}

    lc = style.get("integral_curve") if isinstance(style.get("integral_curve"), dict) else {}
    co = style.get("collapse_overlay") if isinstance(style.get("collapse_overlay"), dict) else {}

    mode = sweep.get("mode", "?")
    rseed = sweep.get("rollout_seed", "?")

    title_tpl = str(style.get("title_template", "{axis}"))
    title = title_tpl.format(
        mode=mode,
        axis=axis,
        n=len(xs),
        rollout_seed=rseed,
    )

    with plt.rc_context(rc_extra):
        fig, ax = plt.subplots(figsize=(w, h), dpi=dpi)
        ax.plot(
            xs,
            ys,
            color=str(lc.get("color", "#1f77b4")),
            linewidth=float(lc.get("linewidth", 1.8)),
            marker=str(lc.get("marker", "o")),
            markersize=float(lc.get("markersize", 6)),
            markerfacecolor=str(lc.get("markerfacecolor", lc.get("color", "#1f77b4"))),
            markeredgecolor=str(lc.get("markeredgecolor", "#000000")),
            markeredgewidth=float(lc.get("markeredgewidth", 0.8)),
            label=str(lc.get("label", "integral_instability")),
            zorder=float(lc.get("zorder", 2)),
        )

        cx = [x for x, c in zip(xs, collapsed, strict=True) if c]
        cy = [y for y, c in zip(ys, collapsed, strict=True) if c]
        if cx:
            ax.scatter(
                cx,
                cy,
                color=str(co.get("color", "#d62728")),
                marker=str(co.get("marker", "X")),
                s=float(co.get("scatter_s", 96)),
                linewidths=float(co.get("linewidths", 0.9)),
                edgecolors=str(co.get("color", "#d62728")),
                label=str(co.get("label", "collapsed run")),
                zorder=float(co.get("zorder", 4)),
            )

        ax.set_xlabel(axis)
        ax.set_ylabel(str(style.get("ylabel", "integral_instability")))
        ax.set_title(title)
        g = style.get("grid") if isinstance(style.get("grid"), dict) else {}
        ax.grid(True, alpha=float(g.get("alpha", 0.28)), linestyle=str(g.get("linestyle", ":")))
        ax.legend(loc=str(style.get("legend_loc", "best")))
        fig.tight_layout()
        try:
            fig.savefig(out_path)
        except OSError as e:
            raise SystemExit(str(e)) from e
        plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=f"Plot axis vs integral_instability from frozen {SWEEP_SCHEMA} JSON.",
    )
    ap.add_argument("sweep_json", type=Path, help="Path to epsilon-sweep JSON.")
    ap.add_argument("--out", type=Path, required=True, help="Output image path (e.g. sweep.png).")
    ap.add_argument(
        "--style-json",
        type=Path,
        default=None,
        help=f"Plot style (default: {_default_style_path()}).",
    )
    args = ap.parse_args()

    try:
        import matplotlib  # noqa: F401
    except ImportError:
        print(
            "matplotlib is required. Install with: pip install matplotlib  or  pip install -e '.[dev]'",
            file=sys.stderr,
        )
        raise SystemExit(2)

    sweep = _load_json(Path(args.sweep_json))
    style_path = Path(args.style_json) if args.style_json is not None else _default_style_path()
    style = _load_style(style_path)
    render_epsilon_sweep_png(sweep, style=style, out_path=Path(args.out))


if __name__ == "__main__":
    main()
