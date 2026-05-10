"""Phase L — scatter ``pareto-front-v1`` archive (severity vs attack_cost).

Style: ``artifacts/plot_styles/default_pareto_front.json`` (**fragility-plot-pareto-style-v1**).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PARETO_SCHEMA = "pareto-front-v1"
STYLE_SCHEMA = "fragility-plot-pareto-style-v1"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _default_style_path() -> Path:
    return _repo_root() / "artifacts" / "plot_styles" / "default_pareto_front.json"


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


def extract_pareto_points(data: dict[str, Any]) -> tuple[list[float], list[float], list[bool]]:
    if data.get("schema") != PARETO_SCHEMA:
        raise SystemExit(f"expected schema {PARETO_SCHEMA!r}")
    arch = data.get("archive")
    if not isinstance(arch, list) or not arch:
        raise SystemExit("pareto JSON missing non-empty archive")
    xs: list[float] = []
    ys: list[float] = []
    collapsed: list[bool] = []
    for i, row in enumerate(arch):
        if not isinstance(row, dict):
            raise SystemExit(f"archive[{i}] must be an object")
        if row.get("severity") is None or row.get("attack_cost") is None:
            raise SystemExit(f"archive[{i}] missing severity or attack_cost")
        xs.append(float(row["severity"]))
        ys.append(float(row["attack_cost"]))
        collapsed.append(bool(row.get("collapsed")))
    return xs, ys, collapsed


def render_pareto_png(data: dict[str, Any], *, style: dict[str, Any], out_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    xs, ys, collapsed = extract_pareto_points(data)

    fig_cfg = style.get("figure") if isinstance(style.get("figure"), dict) else {}
    w = float(fig_cfg.get("width_in", 7.5))
    h = float(fig_cfg.get("height_in", 6.0))
    dpi = float(fig_cfg.get("dpi", 120))
    rc_extra = style["matplotlib_rc"] if isinstance(style.get("matplotlib_rc"), dict) else {}

    po = style.get("points_ok") if isinstance(style.get("points_ok"), dict) else {}
    pc = style.get("points_collapsed") if isinstance(style.get("points_collapsed"), dict) else {}

    ox = [x for x, c in zip(xs, collapsed, strict=True) if not c]
    oy = [y for y, c in zip(ys, collapsed, strict=True) if not c]
    cx = [x for x, c in zip(xs, collapsed, strict=True) if c]
    cy = [y for y, c in zip(ys, collapsed, strict=True) if c]

    bf = data.get("best_fitness", "?")
    title_tpl = str(style.get("title_template", "Pareto"))
    title = title_tpl.format(n=len(xs), best_fitness=bf)

    with plt.rc_context(rc_extra):
        fig, ax = plt.subplots(figsize=(w, h), dpi=dpi)
        if ox:
            ax.scatter(
                ox,
                oy,
                c=str(po.get("color", "#1f77b4")),
                marker=str(po.get("marker", "o")),
                s=float(po.get("s", 36)),
                alpha=float(po.get("alpha", 0.72)),
                edgecolors=str(po.get("edgecolors", "#000")),
                linewidths=float(po.get("linewidths", 0.6)),
                label=str(po.get("label", "not collapsed")),
                zorder=float(po.get("zorder", 3)),
            )
        if cx:
            ax.scatter(
                cx,
                cy,
                c=str(pc.get("color", "#d62728")),
                marker=str(pc.get("marker", "s")),
                s=float(pc.get("s", 42)),
                alpha=float(pc.get("alpha", 0.78)),
                edgecolors=str(pc.get("edgecolors", "#000")),
                linewidths=float(pc.get("linewidths", 0.65)),
                label=str(pc.get("label", "collapsed")),
                zorder=float(pc.get("zorder", 4)),
            )
        ax.set_xlabel(str(style.get("xlabel", "severity")))
        ax.set_ylabel(str(style.get("ylabel", "attack_cost")))
        ax.set_title(title)
        g = style.get("grid") if isinstance(style.get("grid"), dict) else {}
        ax.grid(True, alpha=float(g.get("alpha", 0.28)), linestyle=str(g.get("linestyle", ":")))
        ax.legend(loc=str(style.get("legend_loc", "upper right")))
        fig.tight_layout()
        try:
            fig.savefig(out_path)
        except OSError as e:
            raise SystemExit(str(e)) from e
        plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=f"Plot Pareto archive scatter from frozen {PARETO_SCHEMA} JSON.")
    ap.add_argument("pareto_json", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--style-json", type=Path, default=None)
    args = ap.parse_args()

    try:
        import matplotlib  # noqa: F401
    except ImportError:
        print("matplotlib required: pip install matplotlib  or  pip install -e '.[dev]'", file=sys.stderr)
        raise SystemExit(2)

    raw = _load_json(Path(args.pareto_json))
    style_path = Path(args.style_json) if args.style_json is not None else _default_style_path()
    render_pareto_png(raw, style=_load_style(style_path), out_path=Path(args.out))


if __name__ == "__main__":
    main()
