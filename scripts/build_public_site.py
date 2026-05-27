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
        "The best attack schedule from the benchmark — full step-by-step collapse timeline.",
    ),
    (
        "Aggregate peg",
        "replay",
        "/artifacts/replay_viewer/index.html#src=sample_replay.json",
        "A stablecoin reserve breaking under accumulated panic pressure.",
    ),
    (
        "Network contagion",
        "replay",
        "/artifacts/replay_viewer/index.html#src=sample_network_replay.json",
        "Panic spreading node to node across a connected network.",
    ),
    (
        "Resource cascade",
        "replay",
        "/artifacts/replay_viewer/index.html#src=sample_resource_cascade_replay.json",
        "Two capacity layers that fail together when overload overwhelms the safety margin.",
    ),
    (
        "Service backlog",
        "replay",
        "/artifacts/replay_viewer/index.html#src=sample_service_backlog_replay.json",
        "A work queue that fills up faster than it can be cleared.",
    ),
    (
        "Liquidity ladder",
        "replay",
        "/artifacts/replay_viewer/index.html#src=sample_liquidity_ladder_replay.json",
        "Financial margin eroding step by step until a forced sell-off begins.",
    ),
    (
        "Multi-domain comparison",
        "composite",
        "/artifacts/composite_viewer/index.html",
        "The same attack applied to five domains at once — use the Presets menu.",
    ),
    (
        "Attack trade-off curve",
        "pareto",
        "/artifacts/pareto_viewer/index.html",
        "The full range of trade-offs between attack severity and attack cost.",
    ),
    (
        "What caused the collapse?",
        "attribution",
        "/artifacts/attribution_viewer/index.html",
        "Step-by-step breakdown of which shocks led to failure.",
    ),
]


def _run_page_main() -> str:
    return r"""    <article class="fde-prose">
      <h2>Run a scenario</h2>
      <p>Choose a domain and search type. This server runs the simulation and takes you straight to the results when it finishes.</p>
      <p><a href="/docs/how-to-use.html">How to Use</a> has step-by-step tutorials for every domain. <a href="/docs/algorithms.html">Algorithms</a> explains how the search works.</p>
    </article>

    <form id="runForm" class="fde-run-form" autocomplete="off">

      <div class="fde-run-row">
        <label for="mode">Domain &amp; search type</label>
        <select id="mode" name="mode">
          <optgroup label="Find worst-case scenarios — saves a step-by-step replay">
            <option value="aggregate" selected>Aggregate peg — stablecoin reserves under panic</option>
            <option value="network">Network contagion — panic spreading across 32 connected nodes</option>
            <option value="resource_cascade">Resource cascade — two capacity layers under overload</option>
            <option value="service_backlog">Service backlog — work queue vs processing rate</option>
            <option value="liquidity_ladder">Liquidity ladder — margin eroding toward a forced sell-off</option>
            <option value="inventory_buffer">Inventory buffer — stock level under demand spikes</option>
          </optgroup>
          <optgroup label="Attacker vs. defender simulation — saves a trade-off chart">
            <option value="coevolution_aggregate">Attacker vs. defender · Aggregate peg</option>
            <option value="coevolution_network">Attacker vs. defender · Network contagion</option>
            <option value="coevolution_resource_cascade">Attacker vs. defender · Resource cascade</option>
            <option value="coevolution_service_backlog">Attacker vs. defender · Service backlog</option>
            <option value="coevolution_liquidity_ladder">Attacker vs. defender · Liquidity ladder</option>
            <option value="coevolution_inventory_buffer">Attacker vs. defender · Inventory buffer</option>
          </optgroup>
        </select>
        <p class="fde-run-help" id="modeHelp"></p>
      </div>

      <div class="fde-run-grid">
        <label>Random seed
          <input type="number" id="seed" name="seed" value="999" min="0" max="2147483647" required>
          <span class="fde-run-help">The same seed always produces the same run.</span>
        </label>
        <label id="horizonLabel">Simulation length (steps)
          <input type="number" id="horizon" name="horizon" value="24" min="4" max="48" required>
          <span class="fde-run-help" id="horizonHelp">How many steps the search can use. Max 48.</span>
        </label>
        <label id="gensLabel">Generations
          <input type="number" id="generations" name="generations" value="6" min="1" max="12" required>
          <span class="fde-run-help" id="gensHelp">Search rounds. More = better results, slower.</span>
        </label>
        <label>Population size
          <input type="number" id="population" name="population" value="16" min="4" max="32" required>
          <span class="fde-run-help">Candidate solutions per round. Max 32 on this server.</span>
        </label>
        <label id="initialLevelLabel" hidden>Starting level
          <input type="number" id="initialLevel" name="initialLevel" value="0.88" min="0" max="1" step="0.01">
          <span class="fde-run-help" id="initialLevelHelp">Domain-specific starting condition (0 = empty, 1 = full).</span>
        </label>
        <label id="apiKeyLabel" hidden>Run API key
          <input type="password" id="apiKey" name="apiKey" autocomplete="off" placeholder="Required on this server">
          <span class="fde-run-help" id="apiKeyHelp">Stored in this browser only (session). Set once via <code>?run_key=…</code> in the URL.</span>
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
        <thead><tr><th>Search type</th><th>Main output</th><th>Also saved</th></tr></thead>
        <tbody>
          <tr>
            <td>Find worst-case scenarios</td>
            <td>Replay file → opens in the <a href="/artifacts/replay_viewer/index.html">Replay viewer</a></td>
            <td>Stripped-down replay (if the system collapsed), run logs</td>
          </tr>
          <tr>
            <td>Attacker vs. defender</td>
            <td>Trade-off chart → opens in the <a href="/artifacts/pareto_viewer/index.html">Pareto viewer</a></td>
            <td>Best-round replay, run logs</td>
          </tr>
        </tbody>
      </table>
      <p>All files are saved under <code>/runs/&lt;id&gt;/</code>. A run index survives server restarts; individual run folders may be removed during maintenance.</p>
      <h3>Limits on this server</h3>
      <ul>
        <li>Maximum run time: <strong>180 seconds</strong> — the run is stopped after that.</li>
        <li>Maximum concurrent runs: <strong>2</strong>. Extra submissions get a "busy" error.</li>
        <li>Maximum <strong>12 runs per hour</strong> per client address (rate limit).</li>
        <li>Operators may require an <strong>API key</strong> for submissions (<code>X-Fragility-Run-Key</code> header).</li>
        <li>All inputs are validated; no direct server access is possible.</li>
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
        const initialLevelLabel = document.getElementById('initialLevelLabel');
        const initialLevelInput = document.getElementById('initialLevel');
        const initialLevelHelp = document.getElementById('initialLevelHelp');
        let polling = null;

        const INITIAL_MODES = {
          aggregate: { default: 0.05, label: 'Starting panic level (0 = calm, 1 = high panic)' },
          network: { default: 0.05, label: 'Starting panic on all nodes' },
          resource_cascade: { default: 0.06, label: 'Starting overload (0 = none, 1 = max)' },
          service_backlog: { default: 0.06, label: 'Starting backlog level' },
          liquidity_ladder: { default: 0.06, label: 'Starting margin utilization' },
          inventory_buffer: { default: 0.88, label: 'Starting stock level' },
          coevolution_aggregate: { default: 0.05, label: 'Starting panic level' },
          coevolution_network: { default: 0.05, label: 'Starting panic on all nodes' },
          coevolution_resource_cascade: { default: 0.05, label: 'Starting overload' },
          coevolution_service_backlog: { default: 0.05, label: 'Starting backlog level' },
          coevolution_liquidity_ladder: { default: 0.06, label: 'Starting margin utilization' },
          coevolution_inventory_buffer: { default: 0.88, label: 'Starting stock level' },
        };

        const MODE_TEXT = {
          aggregate:               'The simplest domain: a stablecoin reserve and panic level. Good starting point — fast and easy to read.',
          network:                 'Panic spreading across a randomly connected 32-node network. The replay shows which nodes triggered each other.',
          resource_cascade:        'Two capacity layers that both fail when overload overwhelms the safety margin. Fixed at 18 steps.',
          service_backlog:         'A work queue that fills up faster than it gets processed. Fails when the backlog stays too high for too long. Fixed at 18 steps.',
          liquidity_ladder:        'Financial margin that erodes under reserve losses and rumors until a forced sell-off spiral begins. Fixed at 18 steps.',
          inventory_buffer:        'A stock level that drops under demand surges and fulfillment problems until a stockout occurs. Fixed at 18 steps.',
          coevolution_aggregate:   'An attacker and a defender each evolve on the aggregate peg domain. Outputs a chart showing the full range of trade-offs between attack damage and cost.',
          coevolution_network:     'Attacker and defender both evolve on the network contagion domain. Outputs a trade-off chart.',
          coevolution_resource_cascade: 'Attacker and defender both evolve on the resource cascade domain. Outputs a trade-off chart. Fixed at 18 steps.',
          coevolution_service_backlog:  'Attacker and defender both evolve on the service backlog domain. Outputs a trade-off chart. Fixed at 18 steps.',
          coevolution_liquidity_ladder:  'Attacker and defender both evolve on the liquidity ladder domain. Outputs a trade-off chart. Fixed at 18 steps.',
          coevolution_inventory_buffer:  'Attacker and defender both evolve on the inventory buffer domain. Outputs a trade-off chart. Fixed at 18 steps.',
        };
        const FIXED_HORIZON = {
          resource_cascade: 18, service_backlog: 18, liquidity_ladder: 18,
          inventory_buffer: 18,
          coevolution_resource_cascade: 18, coevolution_service_backlog: 18,
          coevolution_liquidity_ladder: 18, coevolution_inventory_buffer: 18,
        };
        const PARETO_MODES = new Set([
          'coevolution_aggregate','coevolution_network','coevolution_resource_cascade',
          'coevolution_service_backlog','coevolution_liquidity_ladder','coevolution_inventory_buffer'
        ]);

        function updateMode() {
          const m = form.mode.value;
          modeHelp.textContent = MODE_TEXT[m] || '';
          if (m in FIXED_HORIZON) {
            horizonInput.disabled = true;
            horizonInput.value = FIXED_HORIZON[m];
            horizonHelp.textContent = 'Fixed at ' + FIXED_HORIZON[m] + ' steps for this domain.';
          } else {
            horizonInput.disabled = false;
            horizonHelp.textContent = 'How many steps the search can use. Max 48.';
          }
          if (PARETO_MODES.has(m)) {
            gensHelp.textContent = 'Attacker and defender each run this many rounds of search.';
          } else {
            gensHelp.textContent = 'Search rounds. More = better results, slower.';
          }
          const init = INITIAL_MODES[m];
          if (init) {
            initialLevelLabel.hidden = false;
            initialLevelInput.value = init.default;
            initialLevelHelp.textContent = init.label + ' (0 to 1).';
          } else {
            initialLevelLabel.hidden = true;
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
              statusEl.textContent = 'Finished.';
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
              statusEl.textContent = 'Timed out. You can check the run files at /runs/' + id + '/ directly.';
              return;
            }
            statusEl.textContent = 'Running\u2026';
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
          if (INITIAL_MODES[body.mode]) {
            body.initial_level = Number(initialLevelInput.value);
          }
          saveRunApiKey();
          if (runAuthRequired && !runApiHeaders()['X-Fragility-Run-Key']) {
            statusEl.textContent = 'This server requires a run API key (see field above).';
            if (apiKeyLabel) apiKeyLabel.hidden = false;
            return;
          }
          try {
            const r = await fetch('/api/run', {
              method: 'POST',
              headers: runApiHeaders(),
              body: JSON.stringify(body),
            });
            const s = await r.json();
            if (!r.ok) {
              statusEl.textContent = (r.status === 401 ? 'Unauthorized: ' : 'Rejected: ') + (s.error || r.statusText);
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

        // Recent runs history
        async function loadRecentRuns() {
          const el = document.getElementById('recentRuns');
          if (!el) return;
          try {
            const r = await fetch('/api/runs', { cache: 'no-store' });
            if (!r.ok) {             el.innerHTML = '<p class="fde-run-help">Run history not available.</p>'; return; }
            const runs = await r.json();
            if (!runs.length) { el.innerHTML = '<p class="fde-run-help">No runs yet on this server.</p>'; return; }
            const rows = runs.slice(0, 10).map(function(s) {
              const id    = s.id || '?';
              const mode  = (s.request && s.request.mode) || '?';
              const state = s.state || '?';
              const ts    = s.started_utc ? s.started_utc.replace('T',' ').replace('Z','') : '';
              const links = [];
              if (s.viewer_url) links.push('<a href="' + s.viewer_url + '">Replay</a>');
              if (s.pareto_url)  links.push('<a href="' + s.pareto_url  + '">Pareto</a>');
              links.push('<a href="/runs/' + id + '/">/runs/' + id + '/</a>');
              return '<tr><td><code>' + id + '</code></td><td>' + mode + '</td><td>' + state + '</td><td>' + ts + '</td><td>' + links.join(' · ') + '</td></tr>';
            });
            el.innerHTML = '<table><thead><tr><th>ID</th><th>Mode</th><th>State</th><th>Started</th><th>Results</th></tr></thead><tbody>' + rows.join('') + '</tbody></table><p class="fde-run-help"><a href="/runs.html">View all past runs →</a></p>';
          } catch (e) {
            el.innerHTML = '<p class="fde-run-help">Run history not available (engine server not running).</p>';
          }
        }
        loadRecentRuns();
      })();
    </script>

    <article class="fde-prose" style="margin-top:2rem">
      <h3>Recent runs</h3>
      <div id="recentRuns"><p class="fde-run-help">Loading\u2026</p></div>
    </article>
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

    index_main = """    <div id="fde-status" class="fde-status-bar" style="display:none"></div>

    <div class="fde-hero">
      <h1>Fragility Discovery Engine</h1>
      <p>Find the conditions that break a simulated system, then understand exactly why it broke.
         Pick a domain, set a few parameters, and this server does the rest.</p>
      <div class="fde-hero-actions">
        <a class="fde-btn-primary" href="/run.html">Run a scenario</a>
        <a class="fde-btn-secondary" href="/docs/">Read the docs</a>
      </div>
    </div>

    <p class="fde-section-title">Tools</p>
    <div class="fde-tool-grid">
      <a class="fde-tool-card" href="/run.html">
        <span class="fde-tool-icon">⚡</span>
        <div>
          <h3>Run a scenario</h3>
          <p>Pick a simulation domain, set a few parameters, and the engine searches for the conditions most likely to break the system. Results open directly in the viewer.</p>
        </div>
      </a>
      <a class="fde-tool-card" href="/artifacts/replay_viewer/index.html">
        <span class="fde-tool-icon">▶</span>
        <div>
          <h3>Replay viewer</h3>
          <p>Step through a scenario one frame at a time. See exactly how the system state changes at each step, when it crosses its breaking threshold, and what the final outcome was.</p>
        </div>
      </a>
      <a class="fde-tool-card" href="/artifacts/pareto_viewer/index.html">
        <span class="fde-tool-icon">◎</span>
        <div>
          <h3>Pareto viewer</h3>
          <p>See the full range of trade-offs between how damaging an attack is and how much it costs. Generated by attacker-vs-defender runs where both sides evolve simultaneously.</p>
        </div>
      </a>
      <a class="fde-tool-card" href="/artifacts/attribution_viewer/index.html">
        <span class="fde-tool-icon">⛓</span>
        <div>
          <h3>Attribution viewer</h3>
          <p>See which individual shocks actually caused the collapse. Remove shocks one at a time and compare what changes — so you can trace the exact path to failure.</p>
        </div>
      </a>
      <a class="fde-tool-card" href="/artifacts/composite_viewer/index.html">
        <span class="fde-tool-icon">⊞</span>
        <div>
          <h3>Composite viewer</h3>
          <p>Run the same attack through multiple domains at once and compare results side by side. Useful for stress-testing across different system types in a single view.</p>
        </div>
      </a>
      <a class="fde-tool-card" href="/docs/">
        <span class="fde-tool-icon">📖</span>
        <div>
          <h3>Documentation</h3>
          <p>Installation, tutorials for each domain, how the algorithms work, full CLI reference, and a guide to the output file formats.</p>
        </div>
      </a>
    </div>

    <p class="fde-section-title">Sample scenarios</p>
    <div class="fde-grid">
      <a class="fde-card" href="/artifacts/replay_viewer/index.html#src=../flagship/bundled/best_replay.json">
        <span class="fde-card-tag">replay · flagship</span>
        <h3>Best run — benchmark</h3>
        <p>The best attack schedule from the bundled benchmark — full step-by-step collapse timeline.</p>
      </a>
      <a class="fde-card" href="/artifacts/replay_viewer/index.html#src=sample_replay.json">
        <span class="fde-card-tag">replay</span>
        <h3>Aggregate peg</h3>
        <p>A stablecoin reserve breaking under accumulated panic pressure.</p>
      </a>
      <a class="fde-card" href="/artifacts/replay_viewer/index.html#src=sample_network_replay.json">
        <span class="fde-card-tag">replay</span>
        <h3>Network contagion</h3>
        <p>Panic spreading node to node across a 32-node network until the system collapses.</p>
      </a>
      <a class="fde-card" href="/artifacts/replay_viewer/index.html#src=sample_resource_cascade_replay.json">
        <span class="fde-card-tag">replay</span>
        <h3>Resource cascade</h3>
        <p>Two capacity layers that fail together when overload overwhelms the safety margin.</p>
      </a>
      <a class="fde-card" href="/artifacts/replay_viewer/index.html#src=sample_service_backlog_replay.json">
        <span class="fde-card-tag">replay</span>
        <h3>Service backlog</h3>
        <p>A work queue that fills up faster than it can be cleared, eventually crossing the failure threshold.</p>
      </a>
      <a class="fde-card" href="/artifacts/replay_viewer/index.html#src=sample_liquidity_ladder_replay.json">
        <span class="fde-card-tag">replay</span>
        <h3>Liquidity ladder</h3>
        <p>Financial margin eroding step by step until a forced deleveraging spiral takes hold.</p>
      </a>
      <a class="fde-card" href="/artifacts/replay_viewer/index.html#src=sample_inventory_buffer_replay.json">
        <span class="fde-card-tag">replay</span>
        <h3>Inventory buffer</h3>
        <p>Stock level dropping under demand surges and fulfillment problems until a stockout occurs.</p>
      </a>
      <a class="fde-card" href="/artifacts/pareto_viewer/index.html#src=sample_pareto_front.json">
        <span class="fde-card-tag">trade-off chart</span>
        <h3>Attack trade-off curve</h3>
        <p>Every point on this chart is an attack that is not dominated by any other — showing the full range between cheap-but-mild and expensive-but-devastating.</p>
      </a>
      <a class="fde-card" href="/artifacts/pareto_viewer/index.html#src=sample_pareto_inventory_buffer.json">
        <span class="fde-card-tag">trade-off chart</span>
        <h3>Inventory buffer trade-offs</h3>
        <p>The severity-vs-cost frontier for the inventory buffer domain.</p>
      </a>
      <a class="fde-card" href="/artifacts/pareto_viewer/index.html#src=sample_pareto_resource_cascade.json">
        <span class="fde-card-tag">trade-off chart</span>
        <h3>Resource cascade trade-offs</h3>
        <p>The severity-vs-cost frontier for the resource cascade domain.</p>
      </a>
      <a class="fde-card" href="/artifacts/attribution_viewer/index.html#src=sample_aggregate_chain_rumor_depeg.json">
        <span class="fde-card-tag">attribution</span>
        <h3>What caused the collapse?</h3>
        <p>A step-by-step breakdown of which rumor shocks led to the peg breaking — remove each one and see what changes.</p>
      </a>
      <a class="fde-card" href="/artifacts/attribution_viewer/index.html#src=sample_attribution_merge_resource_cascade.json">
        <span class="fde-card-tag">attribution</span>
        <h3>Resource cascade attribution</h3>
        <p>Two counterfactual branches compared against the same baseline — which intervention mattered more?</p>
      </a>
      <a class="fde-card" href="/artifacts/attribution_viewer/index.html#src=sample_attribution_merge_inventory_buffer.json">
        <span class="fde-card-tag">attribution</span>
        <h3>Inventory buffer — lower starting stock</h3>
        <p>Compare a baseline run against a variant with less starting stock to see how much the outcome changes.</p>
      </a>
      <a class="fde-card" href="/artifacts/attribution_viewer/index.html#src=sample_inventory_buffer_chain_demand_fulfillment.json">
        <span class="fde-card-tag">attribution · chain</span>
        <h3>Inventory buffer mutation chain</h3>
        <p>Demand spike plus fulfillment erosion applied step by step — see which mutation moves the needle.</p>
      </a>
      <a class="fde-card" href="/artifacts/composite_viewer/index.html#src=../composite_demo/sample_hexa_composite.json">
        <span class="fde-card-tag">composite</span>
        <h3>All six domains</h3>
        <p>Hexa institutional composite: the same attack genome evaluated on every reference domain at once.</p>
      </a>
      <a class="fde-card" href="/artifacts/composite_viewer/index.html">
        <span class="fde-card-tag">composite</span>
        <h3>Multi-domain comparison</h3>
        <p>The same attack applied to multiple domains at once. Use the Presets menu for twin through hexa (all six domains).</p>
      </a>
    </div>"""

    _write(
        out / "index.html",
        product_shell(
            title="Fragility Discovery Engine — Workbench",
            page_id="workbench",
            description="Find the conditions that break a simulated system, then explore exactly why it broke.",
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
        description="Platform-specific setup: Python, venv, Git configuration, and CI scripts.",
        md_filename="INSTALLATION.md",
    )
    _doc(
        filename="how-to-use.html",
        doc_id="docs-use",
        title="How to Use — Fragility Discovery Engine",
        description="Step-by-step tutorials for all six domains, viewers, counterfactuals, and benchmarks.",
        md_filename="HOW_TO_USE.md",
    )
    _doc(
        filename="architecture.html",
        doc_id="docs-arch",
        title="Architecture — Fragility Discovery Engine",
        description="How the code is organized, how a search run flows through it, and how to add new simulation domains.",
        md_filename="ARCHITECTURE.md",
    )
    _doc(
        filename="reference.html",
        doc_id="docs-ref",
        title="Reference — Fragility Discovery Engine",
        description="CLI flags, environment variables, JSON schemas, and script index.",
        md_filename="REFERENCE.md",
    )

    _doc(
        filename="scale-and-limits.html",
        doc_id="docs-scale",
        title="Scale and limits — Fragility Discovery Engine",
        description="What scales how, parallelism caveats, and honest complexity bounds.",
        md_filename="SCALE_AND_LIMITS.md",
    )
    _doc(
        filename="why-inventory-buffer.html",
        doc_id="docs-why-inv",
        title="Why inventory buffer — Fragility Discovery Engine",
        description="What the inventory buffer domain models and why it exists as the sixth reference world.",
        md_filename="WHY_INVENTORY_BUFFER.md",
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
                description="Which algorithms are original to this project, which are standard, and where each one is cited.",
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
          <p>What the engine is, what problem it solves, the six domains, and who it fits.</p>
        </a>
        <a class="fde-card" href="/docs/installation.html">
          <span class="fde-card-tag">setup</span>
          <h3>Installation</h3>
          <p>Platform-specific setup notes for Windows, Linux, macOS, and WSL. Git configuration and CI scripts for contributors.</p>
        </a>
        <a class="fde-card" href="/docs/how-to-use.html">
          <span class="fde-card-tag">tutorials</span>
          <h3>How to Use</h3>
          <p>Step-by-step for all six domains: replay, counterfactuals, co-evolution, benchmarks, and more.</p>
        </a>
        <a class="fde-card" href="/docs/architecture.html">
          <span class="fde-card-tag">internals</span>
          <h3>Architecture</h3>
          <p>How the code is organized, how a search run flows through it, and how to add new simulation domains.</p>
        </a>
        <a class="fde-card" href="/docs/reference.html">
          <span class="fde-card-tag">reference</span>
          <h3>Reference</h3>
          <p>All command-line flags, environment variables, output file formats, and a full script index.</p>
        </a>
        <a class="fde-card" href="/docs/algorithms.html">
          <span class="fde-card-tag">provenance</span>
          <h3>Algorithms</h3>
          <p>Which algorithms are original to this project, which are standard, and where each one is cited.</p>
        </a>
        <a class="fde-card" href="/docs/scale-and-limits.html">
          <span class="fde-card-tag">limits</span>
          <h3>Scale and limits</h3>
          <p>What scales how, when parallelism is safe, and honest complexity bounds for sweeps and search.</p>
        </a>
        <a class="fde-card" href="/docs/why-inventory-buffer.html">
          <span class="fde-card-tag">domain</span>
          <h3>Why inventory buffer</h3>
          <p>What the sixth simulation domain models and how it differs from the other five worlds.</p>
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
        <li><a href="/docs/how-to-use.html#install-and-verify">Install and verify</a> — Python and a virtual environment in under five minutes.</li>
        <li><a href="/docs/how-to-use.html#tutorial-paths">Tutorials</a> — first replay, search run, attacker/defender simulation, counterfactuals.</li>
        <li><a href="/docs/reference.html#simulation-modes">Simulation domains</a> — aggregate, network, resource cascade, service backlog, liquidity ladder, inventory buffer.</li>
        <li><a href="/docs/reference.html#common-json-schemas">Output file formats</a> — all schema IDs and what produces them.</li>
        <li><a href="/docs/scale-and-limits.html">Scale and limits</a> — complexity, parallelism, and sweep cost.</li>
        <li><a href="/docs/why-inventory-buffer.html">Why inventory buffer</a> — the sixth simulation domain explained.</li>
        <li><a href="/docs/algorithms.html">Algorithms</a> — what we built vs what we borrowed, with citations.</li>
        <li><a href="/run.html">Run a scenario</a> — start a search on this server right now.</li>
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
            description="Choose a domain, set a few parameters, and this server runs the search and opens the results.",
            main_html=_run_page_main(),
        ),
    )

    _write(
        out / "host.html",
        product_shell(
            title="This host — Fragility Discovery Engine",
            page_id="host",
            description="Live engine status, server configuration, and deployment notes for this installation.",
            main_html="""<article class="fde-prose">
      <h2>This deployment</h2>
      <p>The <strong>Fragility Discovery Engine</strong> on this VM serves the workbench, bundled JSON artifacts, and interactive viewers. You only need a web browser pointed at this host.</p>
      <ul>
        <li><strong>Engine clone:</strong> <code>~/fragility-discovery-engine</code> (git + venv)</li>
        <li><strong>Public web root:</strong> <code>/var/www/fragility/public</code></li>
        <li><strong>Status:</strong> <a href="/status.json">/status.json</a> (benchmark validate snapshot)</li>
      </ul>

      <h3>Live engine status</h3>
      <div id="hostHealth" class="fde-run-log" style="min-height:4rem"><p class="fde-run-help">Loading&hellip;</p></div>

      <h3>Public URL and HTTPS</h3>
      <p>This workbench is currently reachable at the VM IP. To use a branded hostname with TLS:</p>
      <ol>
        <li>Create a DNS <strong>A record</strong> (for example <code>fragility.agenticop.io</code>) pointing at this server's external IP.</li>
        <li>Open port <strong>443</strong> in the GCP firewall if it is not already allowed.</li>
        <li>From your machine (after DNS propagates): <code>powershell -File scripts/gce_enable_https.ps1</code></li>
        <li>Or on the VM: <code>sudo FRAGILITY_PUBLIC_HOST=fragility.agenticop.io bash scripts/gce_install_https.sh</code></li>
      </ol>
      <p>See <code>scripts/gce_install_https.sh</code> in the repository for details.</p>

      <h3>Updating this server</h3>
      <pre class="fde-code-block">cd ~/fragility-discovery-engine
git pull
bash scripts/gce_publish_workbench.sh</pre>
      <p>From your local machine you can trigger the same update remotely: <code>powershell -File scripts/gce_deploy_public_site.ps1</code></p>
      <p>Product by <a href="https://agenticop.io">AgenticOps</a>. Source: <a href="https://github.com/AgenticOp-io/fragility-discovery-engine">GitHub</a>.</p>
    </article>
    <script>
      (function () {
        var el = document.getElementById('hostHealth');
        fetch('/api/health', { cache: 'no-store' })
          .then(function (r) { return r.json(); })
          .then(function (h) {
            var lines = [];
            lines.push('<strong>Active runs:</strong> ' + h.active + ' of ' + h.max + ' slots in use');
            lines.push('<strong>Run timeout:</strong> ' + h.timeout_s + ' seconds');
            if (h.caps) {
              var caps = h.caps;
              lines.push('<strong>Parameter limits:</strong> seed up to ' + caps.seed[1] +
                ', generations 1–' + caps.generations[1] +
                ', population 1–' + caps.population[1] +
                ', simulation length ' + caps.horizon[0] + '–' + caps.horizon[1] + ' steps');
            }
            if (h.modes) lines.push('<strong>Simulation modes (' + h.modes.length + '):</strong> ' + h.modes.join(', '));
            if (h.pareto_modes) lines.push('<strong>Attacker/defender modes:</strong> ' + h.pareto_modes.join(', '));
            el.innerHTML = '<ul style="margin:0.5rem 0 0 0">' + lines.map(function (l) { return '<li>' + l + '</li>'; }).join('') + '</ul>';
          })
          .catch(function () {
            el.innerHTML = '<p class="fde-run-help">Engine server not reachable. Run <code>bash scripts/gce_install_run_server.sh</code> on the VM to start it.</p>';
          });
      })();
    </script>""",
        ),
    )

    _write(
        out / "runs.html",
        product_shell(
            title="Past runs — Fragility Discovery Engine",
            page_id="runs",
            description="Browse completed scenario runs and open their results in the viewer.",
            main_html="""<article class="fde-prose">
      <h2>Past runs</h2>
      <p>Completed runs on this server. Each row links to the replay or Pareto viewer for that run and its raw files under <code>/runs/&lt;id&gt;/</code>.</p>
    </article>

    <div id="runsList"><p class="fde-run-help">Loading&hellip;</p></div>

    <script>
      (function () {
        var el = document.getElementById('runsList');
        fetch('/api/runs', { cache: 'no-store' })
          .then(function (r) { return r.json(); })
          .then(function (runs) {
            if (!runs.length) {
              el.innerHTML = '<p>No runs yet. <a href="/run.html">Start one now.</a></p>';
              return;
            }
            var rows = runs.map(function (s) {
              var id    = s.id || '?';
              var mode  = (s.request && s.request.mode) || '?';
              var state = s.state || '?';
              var seed  = (s.request && s.request.seed != null) ? s.request.seed : '';
              var gens  = (s.request && s.request.generations != null) ? s.request.generations : '';
              var pop   = (s.request && s.request.population != null) ? s.request.population : '';
              var ts    = s.started_utc ? s.started_utc.replace('T', ' ').replace('Z', ' UTC') : '';
              var dur   = (s.elapsed_s != null) ? s.elapsed_s.toFixed(1) + 's' : '';
              var links = [];
              if (s.viewer_url) links.push('<a href="' + s.viewer_url + '">Replay</a>');
              if (s.pareto_url)  links.push('<a href="' + s.pareto_url  + '">Pareto</a>');
              links.push('<a href="/runs/' + id + '/">files</a>');
              var stateClass = state === 'done' ? 'color:var(--fde-green,#22c55e)' : state === 'failed' ? 'color:var(--fde-red,#ef4444)' : '';
              return '<tr><td><code>' + id + '</code></td>' +
                '<td>' + mode + '</td>' +
                '<td style="' + stateClass + '">' + state + '</td>' +
                '<td>' + seed + '</td>' +
                '<td>' + gens + ' gen / ' + pop + ' pop</td>' +
                '<td>' + ts + '</td>' +
                '<td>' + dur + '</td>' +
                '<td>' + links.join(' &middot; ') + '</td></tr>';
            });
            el.innerHTML = '<div style="overflow-x:auto"><table>' +
              '<thead><tr><th>ID</th><th>Mode</th><th>State</th><th>Seed</th><th>Params</th><th>Started</th><th>Duration</th><th>Results</th></tr></thead>' +
              '<tbody>' + rows.join('') + '</tbody>' +
              '</table></div>' +
              '<p class="fde-run-help">Showing up to 25 most recent runs. Run summaries are indexed on disk; artifact folders may be removed during maintenance.</p>';
          })
          .catch(function () {
            el.innerHTML = '<p class="fde-run-help">Run history not available — the engine server may not be running. <a href="/host.html">Check this host.</a></p>';
          });
      })();
    </script>""",
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
        out / "404.html",
        product_shell(
            title="Page not found — Fragility Discovery Engine",
            page_id="workbench",
            description="The page you requested was not found on this server.",
            main_html="""<article class="fde-prose" style="text-align:center;padding:3rem 0">
      <h2 style="font-size:4rem;margin-bottom:0.25rem">404</h2>
      <p style="font-size:1.25rem">Page not found.</p>
      <p>The URL you requested does not exist on this server. Try one of these:</p>
      <ul style="display:inline-block;text-align:left">
        <li><a href="/">Workbench</a> — the main landing page</li>
        <li><a href="/run.html">Run a scenario</a> — submit a fragility search</li>
        <li><a href="/runs.html">Past runs</a> — browse completed runs</li>
        <li><a href="/docs/">Documentation</a> — full manual</li>
      </ul>
    </article>""",
        ),
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
