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
from public_site_lib import (
    md_to_html,
    product_shell,
    viewer_chrome_footer,
    viewer_chrome_head,
    viewer_chrome_header,
)

import re

VIEWER_PAGE_IDS = {
    "replay_viewer": "replay",
    "pareto_viewer": "pareto",
    "attribution_viewer": "attribution",
    "composite_viewer": "composite",
}

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


def _run_page_main() -> str:
    return """    <article class="fde-prose">
      <h2>Run a scenario</h2>
      <p>Pick a domain, set the search budget, and submit. The engine runs the search <strong>on this server</strong>; when it finishes, the replay viewer opens with your result.</p>
      <p style="font-size:13px;opacity:0.85">Want to know what is actually running? See <a href="/docs/algorithms.html">Algorithms &amp; provenance</a>.</p>
    </article>

    <form id="runForm" class="fde-run-form" autocomplete="off">
      <div class="fde-run-row">
        <label for="mode">Domain</label>
        <select id="mode" name="mode">
          <option value="aggregate" selected>Aggregate peg — scalar reserves vs panic</option>
          <option value="network">Network contagion — panic spreading on an ER graph (32 nodes)</option>
          <option value="resource_cascade">Resource cascade — two coupled capacity layers</option>
          <option value="service_backlog">Service backlog — ops queue vs process rate</option>
          <option value="liquidity_ladder">Liquidity ladder — margin vs funding runway</option>
        </select>
        <p class="fde-run-help" id="modeHelp">The aggregate peg is the smallest reference world: scalar reserves, scalar panic, redemption pressure. Good first run.</p>
      </div>
      <div class="fde-run-grid">
        <label>Random seed
          <input type="number" id="seed" name="seed" value="999" min="0" max="2147483647" required>
          <span class="fde-run-help">Pins all RNGs — same seed reproduces this run exactly.</span>
        </label>
        <label>Horizon (timesteps)
          <input type="number" id="horizon" name="horizon" value="24" min="4" max="48" required>
          <span class="fde-run-help" id="horizonHelp">How many timesteps the attacker can shock. Capped at 48 on this host.</span>
        </label>
        <label>GA generations
          <input type="number" id="generations" name="generations" value="6" min="1" max="12" required>
          <span class="fde-run-help">How many evolution rounds the genetic algorithm runs. More = better attacks, slower.</span>
        </label>
        <label>Population size
          <input type="number" id="population" name="population" value="18" min="4" max="32" required>
          <span class="fde-run-help">Genomes per generation. Capped at 32 on this host.</span>
        </label>
      </div>
      <div class="fde-run-actions">
        <button type="submit" class="fde-run-submit">Run scenario</button>
        <span id="runStatus" class="fde-run-status" aria-live="polite"></span>
      </div>
    </form>

    <div id="runLog" class="fde-run-log" hidden></div>

    <article class="fde-prose" style="margin-top:32px">
      <h3>What you get back</h3>
      <ul>
        <li><strong>Best replay</strong> — the worst attack the GA found, opened in the replay viewer.</li>
        <li><strong>Minimized replay</strong> (if the best run collapsed) — the smallest subset of shocks that still breaks the world.</li>
        <li><strong>status.json</strong> — request, exit code, artifact list. All files stay under <code>/runs/&lt;id&gt;/</code> on this host.</li>
      </ul>
      <h3>Limits</h3>
      <p>This host caps each run at 180 seconds, with at most 2 concurrent runs across the server. The runner accepts only the parameters shown above — no shell access. For longer searches, larger populations, or other domains, run the engine yourself: <code>pip install fragility-engine</code> and see <a href="https://github.com/AgenticOp-io/fragility-discovery-engine/blob/main/docs/HOW_TO_USE.md">HOW_TO_USE.md</a>.</p>
    </article>

    <script>
      (function () {
        const form = document.getElementById('runForm');
        const status = document.getElementById('runStatus');
        const log = document.getElementById('runLog');
        const modeHelp = document.getElementById('modeHelp');
        const horizonHelp = document.getElementById('horizonHelp');
        const horizonInput = document.getElementById('horizon');
        let polling = null;

        const MODE_TEXT = {
          aggregate: 'Smallest reference world: scalar reserves, scalar panic, redemption pressure. Good first run.',
          network: 'Panic spreading on an Erdős–Rényi graph (32 nodes, p=0.12). Adds dashed panic-spread lines to the replay.',
          resource_cascade: 'Two coupled capacity layers with shared overload. Blue line in the replay is minimum headroom (higher = safer).',
          service_backlog: 'Operations queue: backlog grows with demand, shrinks with process rate. Collapse when backlog crosses threshold.',
          liquidity_ladder: 'Margin utilization vs funding runway. Reserve losses and rumor shocks erode the ladder until a margin-call spiral.',
        };
        const FIXED_HORIZON = { resource_cascade: 18, service_backlog: 18, liquidity_ladder: 18 };

        function updateMode() {
          const m = form.mode.value;
          modeHelp.textContent = MODE_TEXT[m] || '';
          if (m in FIXED_HORIZON) {
            horizonInput.disabled = true;
            horizonInput.value = FIXED_HORIZON[m];
            horizonHelp.textContent = 'This domain uses a fixed horizon of ' + FIXED_HORIZON[m] + ' timesteps; the field is locked.';
          } else {
            horizonInput.disabled = false;
            horizonHelp.textContent = 'How many timesteps the attacker can shock. Capped at 48 on this host.';
          }
        }
        form.mode.addEventListener('change', updateMode);
        updateMode();

        function fmt(s) { try { return JSON.stringify(s, null, 2); } catch (e) { return String(s); } }

        async function poll(id, deadline) {
          try {
            const r = await fetch('/api/run/' + id, { cache: 'no-store' });
            const s = await r.json();
            log.hidden = false;
            log.textContent = fmt(s);
            if (s.state === 'done') {
              status.textContent = 'Done. Opening replay…';
              if (s.viewer_url) {
                setTimeout(function () { window.location.href = s.viewer_url; }, 600);
              }
              return;
            }
            if (s.state === 'failed') {
              status.textContent = 'Run failed.';
              return;
            }
            if (Date.now() > deadline) {
              status.textContent = 'Timed out waiting for the run.';
              return;
            }
            status.textContent = 'Running… (' + (s.state || 'queued') + ')';
            polling = setTimeout(function () { poll(id, deadline); }, 1500);
          } catch (e) {
            status.textContent = 'Status check failed: ' + e;
          }
        }

        form.addEventListener('submit', async function (ev) {
          ev.preventDefault();
          if (polling) clearTimeout(polling);
          status.textContent = 'Submitting…';
          log.hidden = true;
          const body = {
            mode: form.mode.value,
            seed: Number(form.seed.value),
            horizon: Number(form.horizon.value),
            generations: Number(form.generations.value),
            population: Number(form.population.value),
          };
          try {
            const r = await fetch('/api/run', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(body),
            });
            const s = await r.json();
            if (!r.ok) {
              status.textContent = 'Rejected: ' + (s.error || r.statusText);
              return;
            }
            status.textContent = 'Accepted (id=' + s.id + '). Polling…';
            log.hidden = false;
            log.textContent = fmt(s);
            poll(s.id, Date.now() + 200000);
          } catch (e) {
            status.textContent = 'Network error: ' + e;
          }
        });
      })();
    </script>
"""


def _copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


_BODY_OPEN_RE = re.compile(r"(<body[^>]*>)", re.IGNORECASE)
_BODY_CLOSE_RE = re.compile(r"(</body\s*>)", re.IGNORECASE)


def _inject_viewer_chrome(html_path: Path, page_id: str) -> None:
    """Wrap a standalone viewer in the product palette + brand chrome + footer.

    Idempotent: if the chrome marker is already present, do nothing. The
    injected header and footer hide themselves when the page is loaded inside
    an iframe (so the workbench live-replay embed stays clean).
    """

    if not html_path.is_file():
        return
    text = html_path.read_text(encoding="utf-8")
    if "fdeViewerTop" in text:
        return
    head_inject = viewer_chrome_head()
    if "</head>" in text:
        text = text.replace("</head>", head_inject + "</head>", 1)
    body_match = _BODY_OPEN_RE.search(text)
    if not body_match:
        return
    end = body_match.end()
    text = text[:end] + "\n" + viewer_chrome_header(page_id, release=RELEASE) + text[end:]
    close_match = _BODY_CLOSE_RE.search(text)
    if close_match:
        idx = close_match.start()
        text = text[:idx] + viewer_chrome_footer() + text[idx:]
    html_path.write_text(text, encoding="utf-8")


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
            page_id = VIEWER_PAGE_IDS.get(name)
            if page_id:
                _inject_viewer_chrome(art_root / name / "index.html", page_id)

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

    algo_md_path = ROOT / "docs" / "ALGORITHMS.md"
    if algo_md_path.is_file():
        algo_md = algo_md_path.read_text(encoding="utf-8")
        _write(
            docs_dir / "algorithms.html",
            product_shell(
                title="Algorithms & provenance — Fragility Discovery Engine",
                page_id="algorithms",
                description="Catalog of search, attribution, and physics algorithms with provenance.",
                main_html=f'<article class="fde-prose">{md_to_html(algo_md)}</article>',
            ),
        )

    _write(
        out / "run.html",
        product_shell(
            title="Run a scenario — Fragility Discovery Engine",
            page_id="run",
            description="Submit a fragility-search scenario; the GCE host runs it and returns a replay.",
            main_html=_run_page_main(),
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
