#!/usr/bin/env python3
"""Build AgenticOps-branded public site bundle for GCE / static hosting."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from public_site_lib import md_to_html, page_shell

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SRC = ROOT / "docs" / "public"
DEFAULT_OUT = ROOT / "artifacts" / "public_site"

ARTIFACT_DIRS = [
    "replay_viewer",
    "pareto_viewer",
    "attribution_viewer",
    "composite_viewer",
    "composite_demo",
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

    assets_src = PUBLIC_SRC / "assets"
    assets_dst = out / "assets"
    _copytree(assets_src, assets_dst)
    shutil.copy2(assets_src / "agenticops.css", out / "agenticops.css")
    shutil.copy2(assets_src / "logo.svg", out / "logo.svg")

    art_root = out / "artifacts"
    art_root.mkdir()
    for name in ARTIFACT_DIRS:
        src = ROOT / "artifacts" / name
        if src.is_dir():
            _copytree(src, art_root / name)

    wp_md = (ROOT / "docs" / "WHITEPAPER_INTRODUCTION.md").read_text(encoding="utf-8")
    wp_body = md_to_html(wp_md)
    _write(
        out / "whitepaper.html",
        page_shell(
            title="Fragility Discovery Engine — Whitepaper",
            page_id="whitepaper",
            description="What the engine is, six domains, reproducibility.",
            main_html=f"""    <section class="ao-section">
      <div class="ao-wrap ao-md">
        <p class="ao-kicker">Technical overview</p>
        {wp_body}
      </div>
    </section>""",
        ),
    )

    viewers = [
        ("Replay timeline", "/artifacts/replay_viewer/index.html", "Load replay JSON; scrub timelines."),
        ("Pareto front", "/artifacts/pareto_viewer/index.html", "2-D adversary objectives."),
        ("Attribution / chains", "/artifacts/attribution_viewer/index.html", "Counterfactual chains."),
        ("Institutional composite", "/artifacts/composite_viewer/index.html", "Hexa / penta audit JSON."),
    ]
    cards = "\n".join(
        f"""        <a class="ao-viewer-card" href="{href}">
          <h3>{title}</h3>
          <p>{desc}</p>
        </a>"""
        for title, href, desc in viewers
    )

    _write(
        out / "dashboard.html",
        page_shell(
            title="Fragility Engine — Interactive dashboard",
            page_id="dashboard",
            description="Static viewers for replay, Pareto, attribution, composite.",
            main_html=f"""    <section class="ao-hero ao-hero--fragility">
      <div class="ao-wrap ao-hero-inner">
        <p class="ao-eyebrow"><span class="ao-pulse"></span> Evidence-first · Deterministic JSON</p>
        <h1 class="ao-title">Interactive <span class="ao-grad">dashboard</span></h1>
        <p class="ao-lead">Bundled static viewers — open a preset or drop your own artifact JSON.</p>
      </div>
    </section>
    <section class="ao-section">
      <div class="ao-wrap">
        <p class="ao-kicker">Viewers</p>
        <div class="ao-viewer-grid">
{cards}
        </div>
      </div>
    </section>"""
        ),
    )

    cli_rows = [
        ("Install (dev)", "pip install -e \".[dev]\""),
        ("CI parity", "bash scripts/ci_local.sh"),
        ("Benchmark validate", "python scripts/run_benchmark_suite.py --validate"),
        ("Flagship demo", "python scripts/run_flagship_demo.py"),
        ("GCE sync", "powershell -File scripts/gce_sync_vm.ps1"),
        ("Deploy public site", "powershell -File scripts/gce_deploy_public_site.ps1"),
        ("Build site only", "python scripts/build_public_site.py"),
    ]
    table = "\n".join(
        f"<tr><td>{a}</td><td><code>{b}</code></td></tr>" for a, b in cli_rows
    )

    _write(
        out / "cli.html",
        page_shell(
            title="Fragility Engine — CLI reference",
            page_id="cli",
            description="Common commands for install, CI, benchmarks, GCE deploy.",
            main_html=f"""    <section class="ao-section">
      <div class="ao-wrap">
        <p class="ao-kicker">Operator CLI</p>
        <h2 class="ao-h2">Commands at the repo root</h2>
        <p class="ao-sub">Full matrix: <code>docs/REFERENCE.md</code> on GitHub.</p>
        <table class="ao-cli-table">
          <thead><tr><th>Task</th><th>Command</th></tr></thead>
          <tbody>
{table}
          </tbody>
        </table>
      </div>
    </section>""",
        ),
    )

    _write(
        out / "index.html",
        page_shell(
            title="Fragility Discovery Engine | AgenticOps",
            page_id="home",
            description="Open-source fragility benchmarks — six domains, deterministic replay.",
            main_html="""    <section class="ao-hero ao-hero--fragility ao-hero--home">
      <div class="ao-wrap ao-hero-inner">
        <div class="ao-hero-logo-wrap">
          <img class="ao-hero-logo" src="/logo.svg" alt="AgenticOps" width="160" height="160" />
        </div>
        <p class="ao-eyebrow"><span class="ao-pulse"></span> AgenticOps research · Macro-scale fragility</p>
        <h1 class="ao-title">
          Find when systems
          <span class="ao-grad">break</span>
          — with proof.
        </h1>
        <p class="ao-lead">
          The <strong>Fragility Discovery Engine</strong> searches shock schedules over modular simulations,
          exports versioned JSON you can replay and cite, and ships <strong>six reference domains</strong>
          plus frozen benchmark bundles in CI.
        </p>
        <div class="ao-hero-ctas">
          <a class="ao-btn ao-btn-primary" href="/dashboard.html">Open dashboard</a>
          <a class="ao-btn ao-btn-ghost" href="/whitepaper.html">Read whitepaper</a>
          <a class="ao-btn ao-btn-link" href="/cli.html">CLI deploy  →</a>
          <a class="ao-btn ao-btn-link" href="https://agenticop.io" target="_blank" rel="noopener">agenticop.io  →</a>
        </div>
        <ul class="ao-hero-stats" aria-label="Release">
          <li><strong>v0.5.0</strong><span>seven bundles</span></li>
          <li><strong>481</strong><span>tests in CI</span></li>
          <li><strong>6</strong><span>reference domains</span></li>
          <li><strong>JSON</strong><span>replay contract</span></li>
        </ul>
      </div>
    </section>
    <section class="ao-section ao-section-alt">
      <div class="ao-wrap">
        <p class="ao-kicker">Explore</p>
        <h2 class="ao-h2">Public artifacts &amp; docs</h2>
        <div class="ao-hub-grid">
          <a class="ao-hub-card" href="/dashboard.html">
            <span class="ao-hub-card-num">01</span>
            <h3>Dashboard</h3>
            <p>Replay, Pareto, attribution, composite viewers.</p>
            <span class="ao-hub-card-go">Open →</span>
          </a>
          <a class="ao-hub-card" href="/whitepaper.html">
            <span class="ao-hub-card-num">02</span>
            <h3>Whitepaper</h3>
            <p>Fit, domains, reproducibility bar.</p>
            <span class="ao-hub-card-go">Open →</span>
          </a>
          <a class="ao-hub-card" href="https://github.com/AgenticOp-io/fragility-discovery-engine">
            <span class="ao-hub-card-num">03</span>
            <h3>GitHub</h3>
            <p>Source, issues, releases.</p>
            <span class="ao-hub-card-go">Open →</span>
          </a>
        </div>
      </div>
    </section>"""
        ),
    )

    built = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta = {"out": str(out), "built_utc": built, "pages": ["index", "dashboard", "whitepaper", "cli"]}
    _write(out / "build.json", json.dumps(meta, indent=2))
    return meta


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    print(json.dumps(build(args.out), indent=2))


if __name__ == "__main__":
    main()
