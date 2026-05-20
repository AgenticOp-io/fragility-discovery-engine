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
    docs_strip_html,
    md_to_html,
    product_shell,
    site_chrome_footer,
    site_chrome_head,
    site_chrome_header,
    viewer_strip_html,
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
    return r"""    <article class="fde-prose">
      <h2>Run a scenario</h2>
      <p>Choose a domain and search type. The engine runs on <strong>this server</strong>; when it finishes you are taken straight to the viewer with your result.</p>
      <p><a href="/docs/how-to-use.html">How to Use</a> has step-by-step tutorials for every domain. <a href="/docs/algorithms.html">Algorithms &amp; provenance</a> explains what is running under the hood.</p>
    </article>

    <form id="runForm" class="fde-run-form" autocomplete="off">

      <div class="fde-run-row">
        <label for="mode">Domain &amp; search type</label>
        <select id="mode" name="mode">
          <optgroup label="Single-adversary GA — outputs replay">
            <option value="aggregate" selected>Aggregate peg — scalar reserves vs panic</option>
            <option value="network">Network contagion — panic spreading on an ER graph (32 nodes)</option>
            <option value="resource_cascade">Resource cascade — two coupled capacity layers</option>
            <option value="service_backlog">Service backlog — ops queue vs process rate</option>
            <option value="liquidity_ladder">Liquidity ladder — margin vs funding runway</option>
            <option value="inventory_buffer">Inventory buffer — stock drain under demand spikes</option>
          </optgroup>
          <optgroup label="Attacker/defender co-evolution — outputs Pareto front">
            <option value="coevolution_aggregate">Co-evolution · Aggregate peg</option>
            <option value="coevolution_network">Co-evolution · Network contagion</option>
            <option value="coevolution_resource_cascade">Co-evolution · Resource cascade</option>
            <option value="coevolution_service_backlog">Co-evolution · Service backlog</option>
            <option value="coevolution_liquidity_ladder">Co-evolution · Liquidity ladder</option>
          </optgroup>
        </select>
        <p class="fde-run-help" id="modeHelp"></p>
      </div>

      <div class="fde-run-grid">
        <label>Random seed
          <input type="number" id="seed" name="seed" value="999" min="0" max="2147483647" required>
          <span class="fde-run-help">Same seed always reproduces the same run.</span>
        </label>
        <label id="horizonLabel">Horizon (timesteps)
          <input type="number" id="horizon" name="horizon" value="24" min="4" max="48" required>
          <span class="fde-run-help" id="horizonHelp">How many timesteps the attacker can use.</span>
        </label>
        <label id="gensLabel">Generations
          <input type="number" id="generations" name="generations" value="6" min="1" max="12" required>
          <span class="fde-run-help" id="gensHelp">Evolution rounds. More = better attacks, slower.</span>
        </label>
        <label>Population size
          <input type="number" id="population" name="population" value="16" min="4" max="32" required>
          <span class="fde-run-help">Genomes per generation. Max 32 on this host.</span>
        </label>
      </div>

      <div class="fde-run-actions">
        <button type="submit" class="fde-run-submit" id="runBtn">Run scenario</button>
        <span id="runStatus" class="fde-run-status" aria-live="polite"></span>
      </div>
    </form>

    <div id="runLog" class="fde-run-log" hidden></div>
    <div id="runLinks" hidden style="margin:1rem 0"></div>

    <article class="fde-prose" style="margin-top:2rem">
      <h3>What you get</h3>
      <table>
        <thead><tr><th>Search type</th><th>Primary output</th><th>Also produced</th></tr></thead>
        <tbody>
          <tr>
            <td>Single-adversary GA</td>
            <td>Replay JSON → opened in the <a href="/artifacts/replay_viewer/index.html">Replay viewer</a></td>
            <td>Minimized replay (if collapsed), stdout/stderr logs, status.json</td>
          </tr>
          <tr>
            <td>Co-evolution</td>
            <td>Pareto front JSON → opened in the <a href="/artifacts/pareto_viewer/index.html">Pareto viewer</a></td>
            <td>Best-round replay JSON, stdout/stderr logs, status.json</td>
          </tr>
        </tbody>
      </table>
      <p>All files persist under <code>/runs/&lt;id&gt;/</code> on this host and are accessible directly by URL for the duration of the server's uptime.</p>
      <h3>Server limits</h3>
      <ul>
        <li>Maximum run time: <strong>180 seconds</strong> (then killed).</li>
        <li>Maximum concurrent runs: <strong>2</strong>. Extra submissions are rejected with a "busy" error.</li>
        <li>Parameters are validated server-side; no shell access is possible.</li>
        <li>For longer searches, larger populations, or local use: <code>pip install fragility-engine</code> — see <a href="/docs/how-to-use.html">How to Use</a>.</li>
      </ul>
    </article>

    <script>
      (function () {
        const form   = document.getElementById('runForm');
        const statusEl = document.getElementById('runStatus');
        const logEl  = document.getElementById('runLog');
        const linksEl = document.getElementById('runLinks');
        const modeHelp = document.getElementById('modeHelp');
        const horizonHelp = document.getElementById('horizonHelp');
        const gensHelp  = document.getElementById('gensHelp');
        const horizonInput = document.getElementById('horizon');
        let polling = null;

        const MODE_TEXT = {
          aggregate:               'Smallest world: scalar reserves vs panic. Good starting point — fast and easy to interpret.',
          network:                 'Panic spreading on an Erdős–Rényi graph (32 nodes, p=0.12). Replay shows dashed contagion traces.',
          resource_cascade:        'Two coupled capacity layers with shared overload. Blue line = minimum headroom (higher is safer). Fixed horizon: 18.',
          service_backlog:         'Operations queue: backlog grows with demand, falls with process rate. Collapse when backlog threshold is crossed. Fixed horizon: 18.',
          liquidity_ladder:        'Margin utilization vs funding runway. Reserve losses and rumor shocks erode the ladder until a margin-call spiral. Fixed horizon: 18.',
          inventory_buffer:        'Stock level under demand spikes and fulfillment erosion. Sixth reference domain (Phase O). Fixed horizon: 18.',
          coevolution_aggregate:   'Attacker and defender evolve together on the aggregate peg. Outputs a severity-vs-cost Pareto front. Runs 1 round.',
          coevolution_network:     'Attacker and defender evolve together on the network contagion domain. Outputs a Pareto front.',
          coevolution_resource_cascade: 'Co-evolution on the resource cascade domain. Outputs a Pareto front. Fixed horizon: 18.',
          coevolution_service_backlog:  'Co-evolution on the service backlog domain. Outputs a Pareto front. Fixed horizon: 18.',
          coevolution_liquidity_ladder: 'Co-evolution on the liquidity ladder domain. Outputs a Pareto front. Fixed horizon: 18.',
        };
        const FIXED_HORIZON = {
          resource_cascade: 18, service_backlog: 18, liquidity_ladder: 18,
          inventory_buffer: 18,
          coevolution_resource_cascade: 18, coevolution_service_backlog: 18, coevolution_liquidity_ladder: 18,
        };
        const PARETO_MODES = new Set([
          'coevolution_aggregate','coevolution_network','coevolution_resource_cascade',
          'coevolution_service_backlog','coevolution_liquidity_ladder'
        ]);

        function updateMode() {
          const m = form.mode.value;
          modeHelp.textContent = MODE_TEXT[m] || '';
          if (m in FIXED_HORIZON) {
            horizonInput.disabled = true;
            horizonInput.value = FIXED_HORIZON[m];
            horizonHelp.textContent = 'Fixed at ' + FIXED_HORIZON[m] + ' timesteps for this domain.';
          } else {
            horizonInput.disabled = false;
            horizonHelp.textContent = 'Timesteps available to the attacker. Max 48.';
          }
          if (PARETO_MODES.has(m)) {
            gensHelp.textContent = 'Attacker and defender each run this many generations per round.';
          } else {
            gensHelp.textContent = 'Evolution rounds. More = better attacks, slower.';
          }
        }
        form.mode.addEventListener('change', updateMode);
        updateMode();

        function fmt(s) { try { return JSON.stringify(s, null, 2); } catch (e) { return String(s); } }

        function showLinks(s) {
          const links = [];
          if (s.viewer_url) links.push('<a href="' + s.viewer_url + '" class="fde-run-submit" style="text-decoration:none">Open Replay viewer →</a>');
          if (s.pareto_url)  links.push('<a href="' + s.pareto_url  + '" class="fde-run-submit" style="text-decoration:none">Open Pareto viewer →</a>');
          if (links.length) {
            linksEl.innerHTML = links.join(' &nbsp; ');
            linksEl.hidden = false;
          }
        }

        async function poll(id, deadline) {
          try {
            const r = await fetch('/api/run/' + id, { cache: 'no-store' });
            const s = await r.json();
            logEl.hidden = false;
            logEl.textContent = fmt(s);
            if (s.state === 'done') {
              statusEl.textContent = 'Done.';
              showLinks(s);
              const dest = s.pareto_url || s.viewer_url;
              if (dest) setTimeout(function () { window.location.href = dest; }, 800);
              return;
            }
            if (s.state === 'failed') {
              statusEl.textContent = 'Run failed — see log below.';
              return;
            }
            if (Date.now() > deadline) {
              statusEl.textContent = 'Timed out waiting — check /runs/' + id + '/status.json directly.';
              return;
            }
            statusEl.textContent = 'Running\u2026 (' + (s.state || 'queued') + ')';
            polling = setTimeout(function () { poll(id, deadline); }, 1500);
          } catch (e) {
            statusEl.textContent = 'Status check failed: ' + e;
          }
        }

        form.addEventListener('submit', async function (ev) {
          ev.preventDefault();
          if (polling) clearTimeout(polling);
          statusEl.textContent = 'Submitting\u2026';
          logEl.hidden = true;
          linksEl.hidden = true;
          const body = {
            mode:        form.mode.value,
            seed:        Number(form.seed.value),
            horizon:     Number(form.horizon.value),
            generations: Number(form.generations.value),
            population:  Number(form.population.value),
          };
          try {
            const r = await fetch('/api/run', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(body),
            });
            const s = await r.json();
            if (!r.ok) {
              statusEl.textContent = 'Rejected: ' + (s.error || r.statusText);
              return;
            }
            statusEl.textContent = 'Accepted (id=' + s.id + '). Polling\u2026';
            logEl.hidden = false;
            logEl.textContent = fmt(s);
            poll(s.id, Date.now() + 210000);
          } catch (e) {
            statusEl.textContent = 'Network error: ' + e;
          }
        });
      })();
    </script>
"""


def _copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


_BODY_OPEN_RE = re.compile(r"<body([^>]*)>", re.IGNORECASE)
_BODY_CLOSE_RE = re.compile(r"(</body\s*>)", re.IGNORECASE)
_VIEWER_STYLE_RE = re.compile(r"<style>.*?</style>\s*", re.DOTALL | re.IGNORECASE)
_LEGACY_CHROME_RE = re.compile(
    r"<header class=\"fde-viewer-top\".*?</header>\s*"
    r"<script>if \(window\.top !== window\.self\).*?</script>\s*",
    re.DOTALL,
)
_LEGACY_HEAD_INJECT_RE = re.compile(
    r"<link rel=\"preconnect\" href=\"https://fonts\.googleapis\.com\"/>.*?<style>\s*:root \{ color-scheme: dark; \}.*?</style>\s*",
    re.DOTALL,
)
_LEGACY_FOOTER_RE = re.compile(
    r"<footer class=\"fde-viewer-footer\".*?</footer>\s*"
    r"<script>if \(window\.top !== window\.self\).*?</script>\s*",
    re.DOTALL,
)
_INLINE_STYLE_ATTR = re.compile(r'\s+style="[^"]*"')


def _strip_inline_styles_in_viewer_main(text: str) -> str:
    """Remove per-element inline styles so global CSS controls typography."""

    marker = '<main class="fde-main fde-viewer-main">'
    start = text.find(marker)
    if start < 0:
        return text
    end = text.find("</main>", start)
    if end < 0:
        return text
    chunk = text[start:end]
    chunk = _INLINE_STYLE_ATTR.sub("", chunk)
    return text[:start] + chunk + text[end:]


def _strip_legacy_viewer_chrome(text: str) -> str:
    """Remove an older injected chrome pass so rebuilds can upgrade in place."""

    text = _LEGACY_CHROME_RE.sub("", text)
    text = _LEGACY_HEAD_INJECT_RE.sub("", text)
    text = _LEGACY_FOOTER_RE.sub("", text)
    if "<!-- fdeSiteChrome -->" in text:
        text = re.sub(
            r"<!-- fdeSiteChrome -->.*?</script>\s*",
            "",
            text,
            count=1,
            flags=re.DOTALL,
        )
        text = text.replace('<main class="fde-main fde-viewer-main">', "")
        text = text.replace("</main>\n", "", 1)
        text = _LEGACY_FOOTER_RE.sub("", text)
    return text


def _inject_viewer_chrome(html_path: Path, page_id: str) -> None:
    """Wrap a standalone viewer in the same site chrome as every other page.

    - Drops per-viewer <style> blocks; typography comes from fde-product.css.
    - Uses the shared fde-top nav (Workbench → Replay → … → Attribution → …).
    - Adds a viewer strip (Replay | Pareto | Attribution | Composite) for quick hops.
    - Header/footer hide when embedded in the workbench iframe.
    """

    if not html_path.is_file():
        return
    text = html_path.read_text(encoding="utf-8")
    text = _strip_legacy_viewer_chrome(text)
    if "<!-- fdeSiteChrome -->" in text:
        return

    text = _VIEWER_STYLE_RE.sub("", text, count=1)
    if "</head>" in text:
        text = text.replace("</head>", site_chrome_head() + "</head>", 1)

    body_match = _BODY_OPEN_RE.search(text)
    if not body_match:
        return
    text = _BODY_OPEN_RE.sub('<body class="fde-app">', text, count=1)

    body_match = _BODY_OPEN_RE.search(text)
    if not body_match:
        return
    end = body_match.end()
    chrome = site_chrome_header(page_id, release=RELEASE)
    strip = viewer_strip_html(page_id)
    text = (
        text[:end]
        + "\n"
        + chrome
        + '  <main class="fde-main fde-viewer-main">\n'
        + strip
        + "\n"
        + text[end:]
    )

    close_match = _BODY_CLOSE_RE.search(text)
    if close_match:
        idx = close_match.start()
        text = text[:idx] + "  </main>\n" + site_chrome_footer() + text[idx:]
    text = _strip_inline_styles_in_viewer_main(text)
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

    docs_dir = out / "docs"
    docs_dir.mkdir()

    def _doc(*, filename: str, doc_id: str, title: str, description: str, md_filename: str) -> None:
        """Read a markdown file and write a docs page with the shared strip nav."""
        md_path = ROOT / "docs" / md_filename
        if not md_path.is_file():
            return
        body = f'{docs_strip_html(doc_id)}\n<article class="fde-prose">{md_to_html(md_path.read_text(encoding="utf-8"))}</article>'
        _write(
            docs_dir / filename,
            product_shell(title=title, page_id="docs", description=description, main_html=body),
        )

    # Docs index is generated below; the individual section pages come first.
    _doc(
        filename="overview.html",
        doc_id="docs-index",
        title="Overview — Fragility Discovery Engine",
        description="What the engine is, what problems it solves, and who it fits.",
        md_filename="WHITEPAPER_INTRODUCTION.md",
    )
    _doc(
        filename="installation.html",
        doc_id="docs-install",
        title="Installation — Fragility Discovery Engine",
        description="Setup instructions: Python, venv, platform notes, CI parity.",
        md_filename="INSTALLATION.md",
    )
    _doc(
        filename="how-to-use.html",
        doc_id="docs-use",
        title="How to Use — Fragility Discovery Engine",
        description="Tutorials for all five domains, viewers, counterfactuals, and benchmarks.",
        md_filename="HOW_TO_USE.md",
    )
    _doc(
        filename="architecture.html",
        doc_id="docs-arch",
        title="Architecture — Fragility Discovery Engine",
        description="Package layers, rollout pipeline, simulation modes, and extension points.",
        md_filename="ARCHITECTURE.md",
    )
    _doc(
        filename="reference.html",
        doc_id="docs-ref",
        title="Reference — Fragility Discovery Engine",
        description="CLI flags, environment variables, JSON schemas, and script index.",
        md_filename="REFERENCE.md",
    )

    algo_md_path = ROOT / "docs" / "ALGORITHMS.md"
    if algo_md_path.is_file():
        algo_md = algo_md_path.read_text(encoding="utf-8")
        algo_body = f'{docs_strip_html("docs-algo")}\n<article class="fde-prose">{md_to_html(algo_md)}</article>'
        _write(
            docs_dir / "algorithms.html",
            product_shell(
                title="Algorithms & provenance — Fragility Discovery Engine",
                page_id="docs",
                description="Catalog of search, attribution, and physics algorithms with provenance.",
                main_html=algo_body,
            ),
        )

    # Legacy redirect: /docs/whitepaper.html → /docs/overview.html
    _write(
        docs_dir / "whitepaper.html",
        '<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0;url=/docs/overview.html"/>'
        '<title>Redirect</title></head><body></body></html>',
    )

    # Docs landing page — card grid linking all sections.
    docs_cards = """\
      <div class="fde-docs-index-grid">
        <a class="fde-card" href="/docs/overview.html">
          <span class="fde-card-tag">introduction</span>
          <h3>Overview</h3>
          <p>What the engine is, what problem it solves, the five domains, and who it fits.</p>
        </a>
        <a class="fde-card" href="/docs/installation.html">
          <span class="fde-card-tag">setup</span>
          <h3>Installation</h3>
          <p>Python, venv, platform notes (Windows / Linux / macOS / WSL), CI parity scripts.</p>
        </a>
        <a class="fde-card" href="/docs/how-to-use.html">
          <span class="fde-card-tag">tutorials</span>
          <h3>How to Use</h3>
          <p>Step-by-step for all five domains: replay, counterfactuals, Pareto, co-evolution, benchmarks.</p>
        </a>
        <a class="fde-card" href="/docs/architecture.html">
          <span class="fde-card-tag">internals</span>
          <h3>Architecture</h3>
          <p>Package layers, rollout pipeline, simulation modes, search mechanisms, and extension points.</p>
        </a>
        <a class="fde-card" href="/docs/reference.html">
          <span class="fde-card-tag">reference</span>
          <h3>Reference</h3>
          <p>Complete CLI flag matrix, environment variables, JSON schema IDs, and script index.</p>
        </a>
        <a class="fde-card" href="/docs/algorithms.html">
          <span class="fde-card-tag">provenance</span>
          <h3>Algorithms</h3>
          <p>Every algorithm used: what we wrote vs standard methods, with citations and code paths.</p>
        </a>
      </div>"""
    docs_index_main = f"""\
    <div class="fde-hero-compact">
      <h1>Documentation</h1>
      <p>Complete manual for the Fragility Discovery Engine — from first run to algorithm internals.</p>
    </div>
    <p class="fde-section-title">Sections</p>
{docs_cards}
    <p class="fde-section-title" style="margin-top:2rem">Quick links</p>
    <div class="fde-prose">
      <ul>
        <li><a href="/docs/how-to-use.html#install-and-verify">Install and verify</a> — Python + venv in under five minutes.</li>
        <li><a href="/docs/how-to-use.html#tutorial-paths">Tutorial paths</a> — first replay, GA search, co-evolution, counterfactuals.</li>
        <li><a href="/docs/reference.html#simulation-modes">Simulation modes at a glance</a> — aggregate, network, resource cascade, service backlog, liquidity ladder.</li>
        <li><a href="/docs/reference.html#common-json-schemas">JSON schemas</a> — all artifact schema IDs and what produces them.</li>
        <li><a href="/docs/algorithms.html">Algorithms &amp; provenance</a> — what we built vs what we borrowed.</li>
        <li><a href="/run.html">Run a scenario</a> — submit a search run on this server right now.</li>
      </ul>
    </div>"""
    _write(
        docs_dir / "index.html",
        product_shell(
            title="Documentation — Fragility Discovery Engine",
            page_id="docs",
            description="Complete manual: overview, installation, tutorials, architecture, reference, and algorithms.",
            main_html=docs_index_main,
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
      <p>Product by <a href="https://agenticops.io">AgenticOps</a>. Source: <a href="https://github.com/AgenticOp-io/fragility-discovery-engine">GitHub</a>.</p>
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
