"""Phase L — heatmap of ``integral_instability`` from ``fragility_surface.py`` CSV (uniform grid).

Expects columns **panic0**, **depeg_threshold**, **integral_instability** (from ``fragility_surface`` linspace grid).

Style: ``artifacts/plot_styles/default_fragility_surface.json`` (**fragility-plot-surface-style-v1**).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

STYLE_SCHEMA = "fragility-plot-surface-style-v1"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _default_style_path() -> Path:
    return _repo_root() / "artifacts" / "plot_styles" / "default_fragility_surface.json"


def _load_style(path: Path) -> dict[str, Any]:
    try:
        style = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit(str(e)) from e
    if not isinstance(style, dict) or style.get("schema") != STYLE_SCHEMA:
        raise SystemExit(f"{path}: expected schema {STYLE_SCHEMA}")
    return style


def load_surface_rows(csv_path: Path) -> list[dict[str, str]]:
    try:
        with csv_path.open(newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            if not r.fieldnames:
                raise SystemExit(f"{csv_path}: missing header row")
            need = {"panic0", "depeg_threshold", "integral_instability"}
            if not need.issubset(set(r.fieldnames)):
                raise SystemExit(f"{csv_path}: need columns {sorted(need)}")
            rows = list(r)
    except OSError as e:
        raise SystemExit(str(e)) from e
    if len(rows) < 3:
        raise SystemExit("need at least 3 grid rows for contour plot")
    return rows


def _uniform_edges(centers: list[float]):
    import numpy as np

    c = np.asarray(centers, dtype=np.float64)
    if c.size < 2:
        span = 0.05
        return np.array([float(c[0]) - span / 2, float(c[0]) + span / 2], dtype=np.float64)
    step = float(c[1] - c[0])
    if not np.allclose(np.diff(c), step, rtol=1e-5, atol=1e-9):
        raise SystemExit("panic0 and depeg_threshold axes must be uniform (fragility_surface linspace grid).")
    return np.linspace(float(c[0] - step / 2), float(c[-1] + step / 2), int(c.size) + 1)


def render_surface_png(
    rows: list[dict[str, str]],
    *,
    style: dict[str, Any],
    out_path: Path,
    title_override: str | None,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    panics = sorted({float(row["panic0"]) for row in rows})
    depegs = sorted({float(row["depeg_threshold"]) for row in rows})
    zi = {(float(r["panic0"]), float(r["depeg_threshold"])): float(r["integral_instability"]) for r in rows}
    need = len(panics) * len(depegs)
    if len(zi) != need:
        raise SystemExit(f"expected full Cartesian grid ({need} cells), got {len(zi)} rows")

    Z = np.zeros((len(panics), len(depegs)), dtype=np.float64)
    for i, p in enumerate(panics):
        for j, d in enumerate(depegs):
            Z[i, j] = zi[(p, d)]

    fig_cfg = style.get("figure") if isinstance(style.get("figure"), dict) else {}
    w = float(fig_cfg.get("width_in", 8.0))
    h = float(fig_cfg.get("height_in", 6.0))
    dpi = float(fig_cfg.get("dpi", 120))
    rc_extra = style["matplotlib_rc"] if isinstance(style.get("matplotlib_rc"), dict) else {}
    cf = style.get("contourf") if isinstance(style.get("contourf"), dict) else {}

    title = title_override or str(style.get("title_template", "Fragility surface"))

    px = _uniform_edges(panics)
    dx = _uniform_edges(depegs)

    with plt.rc_context(rc_extra):
        fig, ax = plt.subplots(figsize=(w, h), dpi=dpi)
        # X = panic axis, Y = depeg axis (matches fragility_surface row semantics).
        pcm = ax.pcolormesh(
            px,
            dx,
            Z.T,
            shading="flat",
            cmap=str(cf.get("cmap", "viridis")),
            alpha=float(cf.get("alpha", 0.95)),
        )
        fig.colorbar(pcm, ax=ax, label=str(style.get("colorbar_label", "integral_instability")))
        ax.set_xlabel(str(style.get("xlabel", "panic0")))
        ax.set_ylabel(str(style.get("ylabel", "depeg_threshold")))
        ax.set_title(title)
        g = style.get("grid") if isinstance(style.get("grid"), dict) else {}
        ax.grid(True, alpha=float(g.get("alpha", 0.2)), linestyle=str(g.get("linestyle", ":")))
        fig.tight_layout()
        try:
            fig.savefig(out_path)
        except OSError as e:
            raise SystemExit(str(e)) from e
        plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description="Contour plot integral_instability from fragility_surface CSV.")
    ap.add_argument("csv_path", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--style-json", type=Path, default=None)
    ap.add_argument("--title", type=str, default=None)
    args = ap.parse_args()

    try:
        import matplotlib  # noqa: F401
    except ImportError:
        print("matplotlib required: pip install matplotlib  or  pip install -e '.[dev]'", file=sys.stderr)
        raise SystemExit(2)

    rows = load_surface_rows(Path(args.csv_path))
    style_path = Path(args.style_json) if args.style_json is not None else _default_style_path()
    render_surface_png(rows, style=_load_style(style_path), out_path=Path(args.out), title_override=args.title)


if __name__ == "__main__":
    main()
