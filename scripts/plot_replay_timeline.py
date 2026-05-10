"""Phase L — reproducible timeline figure from frozen replay JSON (matplotlib).

Style contract: ``artifacts/plot_styles/default_replay_timeline.json`` (**fragility-plot-style-v1**).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _default_style_path() -> Path:
    return _repo_root() / "artifacts" / "plot_styles" / "default_replay_timeline.json"


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
    if style.get("schema") != "fragility-plot-style-v1":
        raise SystemExit(f"{path}: expected schema fragility-plot-style-v1")
    return style


def extract_timeline(replay: dict[str, Any]) -> tuple[list[int], list[float], list[float]]:
    traj = replay.get("trajectory")
    if not isinstance(traj, list) or not traj:
        raise SystemExit("replay JSON missing non-empty trajectory")

    ts: list[int] = []
    prices: list[float] = []
    instabilities: list[float] = []
    for row in traj:
        if not isinstance(row, dict):
            continue
        t = row.get("timestep")
        m = row.get("metrics")
        if t is None or not isinstance(m, dict):
            continue
        ts.append(int(t))
        pv = m.get("price")
        iv = m.get("instability")
        prices.append(float(pv) if pv is not None else float("nan"))
        instabilities.append(float(iv) if iv is not None else float("nan"))

    if not ts:
        raise SystemExit("no trajectory rows with timestep + metrics.price / metrics.instability")
    return ts, prices, instabilities


def render_timeline_png(
    replay: dict[str, Any],
    *,
    style: dict[str, Any],
    out_path: Path,
    show_collapse_line: bool | None = None,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ts, prices, inst = extract_timeline(replay)

    fig_cfg = style.get("figure") if isinstance(style.get("figure"), dict) else {}
    w = float(fig_cfg.get("width_in", 9.0))
    h = float(fig_cfg.get("height_in", 4.5))
    dpi = float(fig_cfg.get("dpi", 120))

    rc_extra = style["matplotlib_rc"] if isinstance(style.get("matplotlib_rc"), dict) else {}

    with plt.rc_context(rc_extra):
        fig, ax_left = plt.subplots(figsize=(w, h), dpi=dpi)
        series = style.get("series") if isinstance(style.get("series"), dict) else {}

        p_style = series.get("price") if isinstance(series.get("price"), dict) else {}
        i_style = series.get("instability") if isinstance(series.get("instability"), dict) else {}

        ax_left.plot(
            ts,
            prices,
            color=str(p_style.get("color", "#1f77b4")),
            linewidth=float(p_style.get("linewidth", 1.8)),
            label="price",
            zorder=float(p_style.get("zorder", 3)),
        )
        ax_left.set_xlabel(str(style.get("xlabel", "timestep")))
        ax_left.set_ylabel(str(p_style.get("ylabel_left", "metrics.price")))

        ax_right = ax_left.twinx()
        ax_right.plot(
            ts,
            inst,
            color=str(i_style.get("color", "#d62728")),
            linewidth=float(i_style.get("linewidth", 1.6)),
            label="instability",
            zorder=float(i_style.get("zorder", 2)),
        )
        ax_right.set_ylabel(str(i_style.get("ylabel_right", "metrics.instability")))

        g = style.get("grid") if isinstance(style.get("grid"), dict) else {}
        ax_left.grid(
            True,
            alpha=float(g.get("alpha", 0.28)),
            linestyle=str(g.get("linestyle", ":")),
        )

        title_tpl = str(style.get("title_template", "{simulation_mode}"))
        title = title_tpl.format(
            simulation_mode=replay.get("simulation_mode", "?"),
            seed=replay.get("seed", "?"),
            collapsed=replay.get("collapsed", "?"),
            collapse_timestep=replay.get("collapse_timestep", ""),
        )
        ax_left.set_title(title)

        cl = style.get("collapse_line") if isinstance(style.get("collapse_line"), dict) else {}
        draw_cl = bool(cl.get("enabled", True))
        if show_collapse_line is not None:
            draw_cl = show_collapse_line

        ct = replay.get("collapse_timestep")
        if draw_cl and replay.get("collapsed") and isinstance(ct, int):
            kw = {
                "color": str(cl.get("color", "#444444")),
                "linestyle": str(cl.get("linestyle", "--")),
                "linewidth": float(cl.get("linewidth", 1.2)),
                "alpha": float(cl.get("alpha", 0.85)),
            }
            label_tpl = str(cl.get("label_template", "collapse t={collapse_timestep}"))
            ax_left.axvline(
                ct,
                label=label_tpl.format(collapse_timestep=ct),
                **kw,
            )

        h_left, l_left = ax_left.get_legend_handles_labels()
        h_right, l_right = ax_right.get_legend_handles_labels()
        ax_left.legend(
            h_left + h_right,
            l_left + l_right,
            loc=str(style.get("legend_loc", "upper right")),
        )

        fig.tight_layout()
        try:
            fig.savefig(out_path)
        except OSError as e:
            raise SystemExit(str(e)) from e
        plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Plot metrics.price and metrics.instability vs timestep from replay JSON (pinned style JSON).",
    )
    ap.add_argument("replay_json", type=Path, help="Frozen replay JSON (schema_version + trajectory).")
    ap.add_argument("--out", type=Path, required=True, help="Output image path (e.g. timeline.png).")
    ap.add_argument(
        "--style-json",
        type=Path,
        default=None,
        help=f"Plot style (default: {_default_style_path()}).",
    )
    ap.add_argument(
        "--no-collapse-line",
        action="store_true",
        help="Do not draw vertical line at collapse_timestep.",
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

    rp = _load_json(Path(args.replay_json))
    style_path = Path(args.style_json) if args.style_json is not None else _default_style_path()
    style = _load_style(style_path)

    render_timeline_png(
        rp,
        style=style,
        out_path=Path(args.out),
        show_collapse_line=False if args.no_collapse_line else None,
    )


if __name__ == "__main__":
    main()
