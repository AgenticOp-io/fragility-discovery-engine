#!/usr/bin/env python3
# ruff: noqa: E501
"""Build public product site (working viewers + bundled demos) for GCE / static hosting."""

from __future__ import annotations

import argparse
import html
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from public_site_lib import md_to_html, product_shell

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ASSETS = ROOT / "docs" / "public" / "assets"
DEFAULT_OUT = ROOT / "artifacts" / "public_site"
RELEASE = "v0.5.0"

ARTIFACT_DIRS = [
    "replay_viewer",
    "pareto_viewer",
    "attribution_viewer",
    "composite_viewer",
    "composite_demo",
    "flagship",
]

DEMOS = [
    (
        "Flagship GA replay",
        "replay",
        "/artifacts/replay_viewer/index.html#src=../flagship/bundled/best_replay.json",
        "Bundled best adversary schedule — collapse timeline.",
    ),
    (
        "Aggregate peg",
        "replay",
        "/artifacts/replay_viewer/index.html#src=sample_replay.json",
        "Scalar stablecoin peg reference domain.",
    ),
    (
        "Network contagion",
        "replay",
        "/artifacts/replay_viewer/index.html#src=sample_network_replay.json",
        "Graph shock propagation.",
    ),
    (
        "Resource cascade",
        "replay",
        "/artifacts/replay_viewer/index.html#src=sample_resource_cascade_replay.json",
        "Overload capacity cascade.",
    ),
    (
        "Service backlog",
        "replay",
        "/artifacts/replay_viewer/index.html#src=sample_service_backlog_replay.json",
        "Ops backlog reference domain.",
    ),
    (
        "Liquidity ladder",
        "replay",
        "/artifacts/replay_viewer/index.html#src=sample_liquidity_ladder_replay.json",
        "Funding ladder stress.",
    ),
    (
        "Penta composite",
        "composite",
        "/artifacts/composite_viewer/index.html",
        "Five-domain audit JSON — use Presets dropdown.",
    ),
    (
        "Pareto front",
        "pareto",
        "/artifacts/pareto_viewer/index.html",
        "Two-objective adversary archive.",
    ),
    (
        "Attribution chains",
        "attribution",
        "/artifacts/attribution_viewer/index.html",
        "Counterfactual chain viewer.",
    ),
]


def _copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build(out: Path) -> dict[str, str]:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    assets_dst = out / "assets"
    assets_dst.mkdir()
    for name in ("fde-product.css", "fde-workbench.js", "logo.svg"):
        src = PUBLIC_ASSETS / name
        if src.is_file():
            shutil.copy2(src, assets_dst / name)

    art_root = out / "artifacts"
    art_root.mkdir()
    for name in ARTIFACT_DIRS:
        src = ROOT / "artifacts" / name
        if src.is_dir():
            _copytree(src, art_root / name)

    demo_cards = "\n".join(
        f"""      <a class="fde-card" href="{href}">
        <span class="fde-card-tag">{html.escape(tag)}</span>
        <h3>{html.escape(title)}</h3>
        <p>{html.escape(desc)}</p>
      </a>"""
        for title, tag, href, desc in DEMOS
    )

    index_main = f"""    <div id="fde-status" class="fde-status-bar">Loading server status…</div>
    <div class="fde-hero-compact">
      <h1>Workbench</h1>
      <p>Everything runs on <strong>this server</strong>. Use the viewers in your browser only — no install on your machine. Open a demo or use Presets inside each tool.</p>
    </div>
    <div class="fde-live">
      <div class="fde-live-head">
        <span>Live · flagship bundled replay</span>
        <a href="/artifacts/replay_viewer/index.html#src=../flagship/bundled/best_replay.json">Open full screen</a>
      </div>
      <iframe title="Replay viewer — flagship demo" src="/artifacts/replay_viewer/index.html#src=../flagship/bundled/best_replay.json"></iframe>
    </div>
    <p class="fde-section-title">Bundled demos</p>
    <div class="fde-grid">
{demo_cards}
    </div>"""

    _write(
        out / "index.html",
        product_shell(
            title="Fragility Discovery Engine — Workbench",
            page_id="workbench",
            description="Live replay and benchmark viewers with bundled frozen demos.",
            main_html=index_main,
        ),
    )

    wp_md = (ROOT / "docs" / "WHITEPAPER_INTRODUCTION.md").read_text(encoding="utf-8")
    docs_dir = out / "docs"
    docs_dir.mkdir()
    _write(
        docs_dir / "whitepaper.html",
        product_shell(
            title="Fragility Discovery Engine — Overview",
            page_id="docs",
            description="Technical overview for researchers.",
            main_html=f'<article class="fde-prose">{md_to_html(wp_md)}</article>',
        ),
    )

    _write(
        out / "host.html",
        product_shell(
            title="This host — Fragility Discovery Engine",
            page_id="host",
            description="GCE-hosted workbench; browser-only access.",
            main_html="""<article class="fde-prose">
      <h2>This deployment</h2>
      <p>The <strong>Fragility Discovery Engine</strong> on this VM serves the workbench, bundled JSON artifacts, and interactive viewers. You only need a web browser pointed at this host.</p>
      <ul>
        <li><strong>Engine clone:</strong> <code>~/fragility-discovery-engine</code> (git + venv)</li>
        <li><strong>Public web root:</strong> <code>/var/www/fragility/public</code></li>
        <li><strong>Status:</strong> <a href="/status.json">/status.json</a> (benchmark validate snapshot)</li>
      </ul>
      <h3>Refresh workbench (operators, on the VM)</h3>
      <pre class="fde-code-block">cd ~/fragility-discovery-engine
git pull
bash scripts/gce_publish_workbench.sh</pre>
      <p>From your laptop you can trigger the same publish after sync: <code>powershell -File scripts/gce_deploy_public_site.ps1</code> (runs build + validate on the VM).</p>
      <p>Product by <a href="https://agenticop.io">AgenticOp</a>. Source: <a href="https://github.com/AgenticOp-io/fragility-discovery-engine">GitHub</a>.</p>
    </article>""",
        ),
    )

    _write(
        out / "status.json",
        json.dumps(
            {
                "schema": "fragility-workbench-status-v1",
                "host": "gce",
                "release": RELEASE,
                "benchmark_validate": "pending",
                "note": "Regenerated by gce_publish_workbench.sh on the VM",
            },
            indent=2,
        ),
    )

    _write(
        out / "dashboard.html",
        '<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0;url=/"/><title>Redirect</title></head><body><p><a href="/">Workbench</a></p></body></html>',
    )
    _write(
        out / "whitepaper.html",
        '<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0;url=/docs/whitepaper.html"/>'
        '<title>Redirect</title></head><body></body></html>',
    )
    _write(
        out / "install.html",
        '<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0;url=/host.html"/>'
        '<title>Redirect</title></head><body></body></html>',
    )
    _write(
        out / "cli.html",
        '<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0;url=/host.html"/>'
        '<title>Redirect</title></head><body></body></html>',
    )

    built = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta = {"out": str(out), "built_utc": built, "release": RELEASE, "kind": "product-workbench"}
    _write(out / "build.json", json.dumps(meta, indent=2))
    return meta


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    print(json.dumps(build(args.out), indent=2))


if __name__ == "__main__":
    main()
