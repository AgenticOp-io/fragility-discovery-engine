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
    "coupling_sweep_viewer": "coupling",
    "coupling_comparison_viewer": "coupling_compare",
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
    "coupling_sweep_viewer",
    "coupling_comparison_viewer",
    "composite_demo",
    "flagship",
    "coupled_fork_demo",
]

def _workbench_index_main() -> str:
    """Workbench landing: server-hosted samples only (no local upload)."""

    return r"""    <div id="fde-status" class="fde-status-bar"></div>

    <article class="fde-prose fde-demo-intro">
      <h2>How this demo works</h2>
      <p>Every sample below is <strong>JSON on this server</strong>. Click a row to open the right viewer with that file already loaded. To run a new search (also saved on the server), use <a href="/run.html">Run a scenario</a> — nothing is uploaded from your computer.</p>
      <p>Full map of pages and viewers: <a href="/docs/demo-guide.html">Demo guide</a> · CLI tutorials: <a href="/docs/how-to-use.html">How to Use</a></p>
    </article>

    <div class="fde-hero fde-hero-compact">
      <h1>Fragility Discovery Engine</h1>
      <p>Search for fragile conditions in toy institutional simulations, then inspect replays, trade-off charts, and attribution paths.</p>
      <div class="fde-hero-actions">
        <a class="fde-btn-primary" href="/run.html">Run a scenario</a>
        <a class="fde-btn-secondary" href="/artifacts/replay_viewer/index.html#src=../flagship/bundled/best_replay.json">Flagship replay</a>
        <a class="fde-btn-secondary" href="/?tour=1">Guided tour</a>
        <a class="fde-btn-secondary" href="/docs/demo-guide.html">Demo guide</a>
      </div>
    </div>

    <nav class="fde-quick-nav" aria-label="Viewer tools">
      <a href="/artifacts/replay_viewer/index.html">Replay viewer</a>
      <a href="/artifacts/pareto_viewer/index.html">Pareto viewer</a>
      <a href="/artifacts/attribution_viewer/index.html">Attribution viewer</a>
      <a href="/artifacts/composite_viewer/index.html">Composite viewer</a>
      <a href="/runs.html">Past server runs</a>
    </nav>

    <section class="fde-demo-section">
      <h2>Step-by-step replays</h2>
      <p class="fde-demo-lead">Scrub timelines of collapse. Opens in the <a href="/artifacts/replay_viewer/index.html">replay viewer</a>.</p>
      <table class="fde-demo-table">
        <thead><tr><th>Sample</th><th>Domain</th><th>Open</th></tr></thead>
        <tbody>
          <tr>
            <td>Flagship benchmark</td>
            <td>Aggregate peg</td>
            <td><a href="/artifacts/replay_viewer/index.html#src=../flagship/bundled/best_replay.json">Replay</a></td>
          </tr>
          <tr>
            <td>Aggregate peg</td>
            <td>Stablecoin reserves</td>
            <td><a href="/artifacts/replay_viewer/index.html#src=sample_replay.json">Replay</a></td>
          </tr>
          <tr>
            <td>Network contagion</td>
            <td>32-node graph</td>
            <td><a href="/artifacts/replay_viewer/index.html#src=sample_network_replay.json">Replay</a></td>
          </tr>
          <tr>
            <td>Resource cascade</td>
            <td>Dual capacity layers</td>
            <td><a href="/artifacts/replay_viewer/index.html#src=sample_resource_cascade_replay.json">Replay</a></td>
          </tr>
          <tr>
            <td>Service backlog</td>
            <td>Queue vs processing</td>
            <td><a href="/artifacts/replay_viewer/index.html#src=sample_service_backlog_replay.json">Replay</a></td>
          </tr>
          <tr>
            <td>Liquidity ladder</td>
            <td>Margin stress</td>
            <td><a href="/artifacts/replay_viewer/index.html#src=sample_liquidity_ladder_replay.json">Replay</a></td>
          </tr>
          <tr>
            <td>Inventory buffer</td>
            <td>Stock level</td>
            <td><a href="/artifacts/replay_viewer/index.html#src=sample_inventory_buffer_replay.json">Replay</a></td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="fde-demo-section">
      <h2>Attack trade-off charts (Pareto)</h2>
      <p class="fde-demo-lead">Severity vs attack cost. Opens in the <a href="/artifacts/pareto_viewer/index.html">Pareto viewer</a>. Co-evolution runs on <a href="/run.html">Run a scenario</a> produce fresh charts under <code>/runs/&lt;id&gt;/</code>.</p>
      <table class="fde-demo-table">
        <thead><tr><th>Sample</th><th>Domain</th><th>Open</th></tr></thead>
        <tbody>
          <tr>
            <td>Aggregate peg frontier</td>
            <td>Charter</td>
            <td><a href="/artifacts/pareto_viewer/index.html#src=sample_pareto_front.json">Chart</a></td>
          </tr>
          <tr>
            <td>Network contagion</td>
            <td>Charter</td>
            <td><a href="/artifacts/pareto_viewer/index.html#src=sample_pareto_network.json">Chart</a></td>
          </tr>
          <tr>
            <td>Resource cascade</td>
            <td>Charter</td>
            <td><a href="/artifacts/pareto_viewer/index.html#src=sample_pareto_resource_cascade.json">Chart</a></td>
          </tr>
          <tr>
            <td>Service backlog</td>
            <td>Charter</td>
            <td><a href="/artifacts/pareto_viewer/index.html#src=sample_pareto_service_backlog.json">Chart</a></td>
          </tr>
          <tr>
            <td>Liquidity ladder</td>
            <td>Charter</td>
            <td><a href="/artifacts/pareto_viewer/index.html#src=sample_pareto_liquidity_ladder.json">Chart</a></td>
          </tr>
          <tr>
            <td>Inventory buffer</td>
            <td>Charter</td>
            <td><a href="/artifacts/pareto_viewer/index.html#src=sample_pareto_inventory_buffer.json">Chart</a></td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="fde-demo-section">
      <h2>Attribution and mutation chains</h2>
      <p class="fde-demo-lead">Counterfactuals and stepwise interventions. Opens in the <a href="/artifacts/attribution_viewer/index.html">attribution viewer</a>.</p>
      <table class="fde-demo-table">
        <thead><tr><th>Sample</th><th>Domain</th><th>Open</th></tr></thead>
        <tbody>
          <tr>
            <td>Rumor → depeg chain</td>
            <td>Aggregate peg</td>
            <td><a href="/artifacts/attribution_viewer/index.html#src=sample_aggregate_chain_rumor_depeg.json">Attribution</a></td>
          </tr>
          <tr>
            <td>Resource cascade merge</td>
            <td>Two branches</td>
            <td><a href="/artifacts/attribution_viewer/index.html#src=sample_attribution_merge_resource_cascade.json">Attribution</a></td>
          </tr>
          <tr>
            <td>Inventory buffer merge</td>
            <td>Lower starting stock</td>
            <td><a href="/artifacts/attribution_viewer/index.html#src=sample_attribution_merge_inventory_buffer.json">Attribution</a></td>
          </tr>
          <tr>
            <td>Inventory demand chain</td>
            <td>Mutation chain</td>
            <td><a href="/artifacts/attribution_viewer/index.html#src=sample_inventory_buffer_chain_demand_fulfillment.json">Attribution</a></td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="fde-demo-section">
      <h2>Multi-domain composite</h2>
      <p class="fde-demo-lead">One attack genome evaluated on several domains. Opens in the <a href="/artifacts/composite_viewer/index.html">composite viewer</a> (use Presets for twin through hexa).</p>
      <table class="fde-demo-table">
        <thead><tr><th>Sample</th><th>Domains</th><th>Open</th></tr></thead>
        <tbody>
          <tr>
            <td>Hexa composite</td>
            <td>All six charter domains</td>
            <td><a href="/artifacts/composite_viewer/index.html#src=../composite_demo/sample_hexa_composite.json">Composite</a></td>
          </tr>
          <tr>
            <td>Preset gallery</td>
            <td>Twin · triple · quad · penta · hexa</td>
            <td><a href="/artifacts/composite_viewer/index.html">Composite viewer</a></td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="fde-demo-section fde-demo-section-fork">
      <h2>Research fork — coupled institution</h2>
      <p class="fde-demo-lead">Peg panic and overload exchange signals inside one simulation step (not the six-domain charter). Policy: <a href="/docs/fork-coupling.html">Coupled fork notes</a> · raw JSON bundle: <a href="/artifacts/coupled_fork_demo/">coupled_fork_demo</a>.</p>
      <table class="fde-demo-table">
        <thead><tr><th>Sample</th><th>Viewer</th><th>Open</th></tr></thead>
        <tbody>
          <tr>
            <td>Coupled replay</td>
            <td>Replay</td>
            <td><a href="/artifacts/replay_viewer/index.html#src=sample_coupled_institution_replay.json">Replay</a></td>
          </tr>
          <tr>
            <td>Mutation chain</td>
            <td>Attribution</td>
            <td><a href="/artifacts/attribution_viewer/index.html#src=sample_coupled_mutation_chain.json">Attribution</a></td>
          </tr>
          <tr>
            <td>Coupling sweep</td>
            <td>Chart</td>
            <td><a href="/artifacts/coupling_sweep_viewer/index.html">Sweep viewer</a></td>
          </tr>
          <tr>
            <td>Coupling comparison</td>
            <td>Compare</td>
            <td><a href="/artifacts/coupling_comparison_viewer/index.html">Comparison viewer</a></td>
          </tr>
          <tr>
            <td>GA Pareto frontier</td>
            <td>Pareto</td>
            <td><a href="/artifacts/pareto_viewer/index.html#src=sample_pareto_coupled_institution.json">Chart</a></td>
          </tr>
          <tr>
            <td>LLM export bundles</td>
            <td>Manifest</td>
            <td><a href="/artifacts/llm_prompts/coupled_fork_exports/">Prompt bundles</a></td>
          </tr>
        </tbody>
      </table>
    </section>"""


def _run_page_main() -> str:
    return r"""    <article class="fde-prose">
      <h2>Run a scenario</h2>
      <p>Pick a domain and search type. The engine runs on <strong>this server</strong> and saves results under <code>/runs/&lt;id&gt;/</code> — you do not upload files. When the job finishes, links open the replay or Pareto viewer against those server paths.</p>
      <p><a href="/docs/demo-guide.html">Demo guide</a> · <a href="/docs/how-to-use.html">How to Use</a> (CLI) · <a href="/docs/algorithms.html">Algorithms</a></p>
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
            <option value="coupled_institution">Coupled institution (research fork) — peg + overload coupling</option>
          </optgroup>
          <optgroup label="Attacker vs. defender simulation — saves a trade-off chart">
            <option value="coevolution_aggregate">Attacker vs. defender · Aggregate peg</option>
            <option value="coevolution_network">Attacker vs. defender · Network contagion</option>
            <option value="coevolution_resource_cascade">Attacker vs. defender · Resource cascade</option>
            <option value="coevolution_service_backlog">Attacker vs. defender · Service backlog</option>
            <option value="coevolution_liquidity_ladder">Attacker vs. defender · Liquidity ladder</option>
            <option value="coevolution_inventory_buffer">Attacker vs. defender · Inventory buffer</option>
            <option value="coevolution_coupled_institution">Attacker vs. defender · Coupled institution (research fork)</option>
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
          <input type="number" id="horizon" name="horizon" value="20" min="4" max="32" required>
          <span class="fde-run-help" id="horizonHelp">How many steps the search can use. Max 32.</span>
        </label>
        <label id="gensLabel">Generations
          <input type="number" id="generations" name="generations" value="4" min="1" max="8" required>
          <span class="fde-run-help" id="gensHelp">Search rounds. More = better results, slower.</span>
        </label>
        <label>Population size
          <input type="number" id="population" name="population" value="12" min="4" max="20" required>
          <span class="fde-run-help">Candidate solutions per round. Max 20 on this server.</span>
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
            <td>Coupled institution (research fork)</td>
            <td>Replay + <a href="/artifacts/pareto_viewer/index.html">Pareto chart</a> for the same GA budget</td>
            <td>Run logs</td>
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
        <li>Maximum run time: <strong>150 seconds</strong> — the run is stopped after that.</li>
        <li>Maximum concurrent runs: <strong>1</strong>. Extra submissions get a "busy" error.</li>
        <li>Maximum <strong>8 runs per hour</strong> per client address (rate limit).</li>
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
        const apiKeyLabel = document.getElementById('apiKeyLabel');
        const apiKeyInput = document.getElementById('apiKey');
        const apiKeyHelp = document.getElementById('apiKeyHelp');
        const RUN_KEY_STORAGE = 'fde_run_api_key';
        let polling = null;
        let runAuthRequired = false;

        function loadRunApiKey() {
          const params = new URLSearchParams(window.location.search);
          const fromUrl = params.get('run_key');
          if (fromUrl) {
            sessionStorage.setItem(RUN_KEY_STORAGE, fromUrl);
            params.delete('run_key');
            const qs = params.toString();
            history.replaceState(null, '', window.location.pathname + (qs ? '?' + qs : ''));
          }
          const stored = sessionStorage.getItem(RUN_KEY_STORAGE) || '';
          if (apiKeyInput) apiKeyInput.value = stored;
          return stored;
        }

        function saveRunApiKey() {
          if (!apiKeyInput) return;
          const v = apiKeyInput.value.trim();
          if (v) sessionStorage.setItem(RUN_KEY_STORAGE, v);
          else sessionStorage.removeItem(RUN_KEY_STORAGE);
        }

        function runApiHeaders() {
          const h = { 'Content-Type': 'application/json' };
          const k = (apiKeyInput && apiKeyInput.value.trim()) || sessionStorage.getItem(RUN_KEY_STORAGE) || '';
          if (k) h['X-Fragility-Run-Key'] = k;
          return h;
        }

        async function loadRunnerHealth() {
          try {
            const r = await fetch('/api/health', { cache: 'no-store' });
            if (!r.ok) return;
            const h = await r.json();
            runAuthRequired = !!h.run_auth_required;
            if (runAuthRequired && apiKeyLabel) {
              apiKeyLabel.hidden = false;
              apiKeyHelp.textContent = 'This server requires a run API key. Use ?run_key=... once per browser session.';
            }
          } catch (e) { /* runner offline */ }
        }
        loadRunApiKey();
        loadRunnerHealth();
        if (apiKeyInput) apiKeyInput.addEventListener('change', saveRunApiKey);

        const INITIAL_MODES = {
          aggregate: { default: 0.05, label: 'Starting panic level (0 = calm, 1 = high panic)' },
          network: { default: 0.05, label: 'Starting panic on all nodes' },
          resource_cascade: { default: 0.06, label: 'Starting overload (0 = none, 1 = max)' },
          service_backlog: { default: 0.06, label: 'Starting backlog level' },
          liquidity_ladder: { default: 0.06, label: 'Starting margin utilization' },
          inventory_buffer: { default: 0.88, label: 'Starting stock level' },
          coupled_institution: { default: 0.3, label: 'In-step coupling strength (0 = decoupled, 1 = tight)' },
          coevolution_aggregate: { default: 0.05, label: 'Starting panic level' },
          coevolution_network: { default: 0.05, label: 'Starting panic on all nodes' },
          coevolution_resource_cascade: { default: 0.05, label: 'Starting overload' },
          coevolution_service_backlog: { default: 0.05, label: 'Starting backlog level' },
          coevolution_liquidity_ladder: { default: 0.06, label: 'Starting margin utilization' },
          coevolution_inventory_buffer: { default: 0.88, label: 'Starting stock level' },
          coevolution_coupled_institution: { default: 0.3, label: 'In-step coupling strength (research fork)' },
        };

        const MODE_TEXT = {
          aggregate:               'The simplest domain: a stablecoin reserve and panic level. Good starting point — fast and easy to read.',
          network:                 'Panic spreading across a randomly connected 32-node network. The replay shows which nodes triggered each other.',
          resource_cascade:        'Two capacity layers that both fail when overload overwhelms the safety margin. Fixed at 18 steps.',
          service_backlog:         'A work queue that fills up faster than it gets processed. Fails when the backlog stays too high for too long. Fixed at 18 steps.',
          liquidity_ladder:        'Financial margin that erodes under reserve losses and rumors until a forced sell-off spiral begins. Fixed at 18 steps.',
          inventory_buffer:        'A stock level that drops under demand surges and fulfillment problems until a stockout occurs. Fixed at 18 steps.',
          coupled_institution:     'Research fork: peg panic and overload exchange signals each simulation step. Saves a replay and a small Pareto trade-off chart.',
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
          'coevolution_service_backlog','coevolution_liquidity_ladder','coevolution_inventory_buffer',
          'coevolution_coupled_institution','coupled_institution'
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
            horizonHelp.textContent = 'How many steps the search can use. Max 32.';
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
        text = text.replace("</head>", site_chrome_head() + _public_demo_meta() + "</head>", 1)

    body_match = _BODY_OPEN_RE.search(text)
    if not body_match:
        return
    text = _BODY_OPEN_RE.sub('<body class="fde-app fde-public-demo">', text, count=1)

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
        text = (
            text[:idx]
            + "  </main>\n"
            + site_chrome_footer()
            + '  <script src="/assets/fde-workbench.js" defer></script>\n'
            + text[idx:]
        )
    text = _strip_inline_styles_in_viewer_main(text)
    html_path.write_text(text, encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _public_demo_meta() -> str:
    return '  <meta name="fde-public-demo" content="1"/>\n'


def _filter_local_presets(presets_path: Path) -> None:
    """Keep only preset paths that exist on the built public site (no test_exports)."""
    if not presets_path.is_file():
        return
    base = presets_path.parent
    cfg = json.loads(presets_path.read_text(encoding="utf-8"))
    kept: list[dict[str, str]] = []
    for entry in cfg.get("presets", []):
        rel = str(entry.get("path", "")).replace("\\", "/")
        if not rel or "test_exports" in rel:
            continue
        if not (base / rel).resolve().is_file():
            continue
        kept.append({"label": entry["label"], "path": entry["path"]})
    cfg["presets"] = kept
    cfg["note"] = (
        "Bundled demos on this server — pick a preset below. "
        "No files on your computer are required."
    )
    presets_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


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
            presets = art_root / name / "local_presets.json"
            if presets.is_file():
                _filter_local_presets(presets)

    coupled_replay = ROOT / "forks" / "coupled_institution" / "artifacts" / "sample_coupled_replay.json"
    if coupled_replay.is_file():
        shutil.copy2(coupled_replay, art_root / "replay_viewer" / "sample_coupled_institution_replay.json")
    coupled_chain = ROOT / "artifacts" / "attribution_viewer" / "sample_coupled_mutation_chain.json"
    if not coupled_chain.is_file():
        fork_chain = ROOT / "forks" / "coupled_institution" / "artifacts" / "sample_coupled_mutation_chain.json"
        if fork_chain.is_file():
            coupled_chain = fork_chain
    if coupled_chain.is_file():
        attr_dir = art_root / "attribution_viewer"
        attr_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(coupled_chain, attr_dir / "sample_coupled_mutation_chain.json")

    llm_exports = ROOT / "artifacts" / "llm_prompts" / "coupled_fork_exports"
    if llm_exports.is_dir():
        _copytree(llm_exports, out / "artifacts" / "llm_prompts" / "coupled_fork_exports")

    fork_art = ROOT / "forks" / "coupled_institution" / "artifacts"
    demo_out = art_root / "coupled_fork_demo"
    demo_src = ROOT / "artifacts" / "coupled_fork_demo"
    if demo_src.is_dir():
        _copytree(demo_src, demo_out)
    if fork_art.is_dir():
        demo_out.mkdir(parents=True, exist_ok=True)
        for name in (
            "sample_coupled_replay.json",
            "coupling_strength_sweep.json",
            "coupling_strength_sweep.png",
            "sample_coupling_comparison.json",
            "sample_coupled_mutation_chain.json",
            "sample_coupled_pareto_front.json",
            "sample_coupled_pareto_front.png",
        ):
            src = fork_art / name
            if src.is_file():
                shutil.copy2(src, demo_out / name)

    index_main = _workbench_index_main()

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
        filename="demo-guide.html",
        doc_id="docs-demo",
        title="Demo guide — Fragility Discovery Engine",
        description="How the public workbench, viewers, and server runs fit together (no local file upload).",
        md_filename="DEMO_GUIDE.md",
    )
    _doc(
        filename="overview.html",
        doc_id="docs-overview",
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
        filename="fel.html",
        doc_id="docs-fel",
        title="Fragility Evidence Language — Fragility Discovery Engine",
        description="Formal types, Δ⁻/Δ⁺ attribution, evidence constructors, and schema registry (FEL v0.1).",
        md_filename="FRAGILITY_EVIDENCE_LANGUAGE.md",
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
    _doc(
        filename="fork-coupling.html",
        doc_id="docs-fork",
        title="Coupled fork (research) — Fragility Discovery Engine",
        description="Why coupled multi-physics lives in a sibling fork, not in the six-domain workbench charter.",
        md_filename="FORK_COUPLING_RESEARCH.md",
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
        <a class="fde-card" href="/docs/demo-guide.html">
          <span class="fde-card-tag">workbench</span>
          <h3>Demo guide</h3>
          <p>Public site layout: server-hosted samples, viewers, runs, and what is not uploaded from your machine.</p>
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
        <a class="fde-card" href="/docs/fel.html">
          <span class="fde-card-tag">formal</span>
          <h3>FEL</h3>
          <p>Fragility Evidence Language — schedules, rollouts, interventions, Δ⁻/Δ⁺ attribution, and evidence schemas.</p>
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
        <a class="fde-card" href="/docs/fork-coupling.html">
          <span class="fde-card-tag">research</span>
          <h3>Coupled fork</h3>
          <p>In-step peg–overload coupling, mutation-chain attribution, and downloadable fork JSON.</p>
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
        <li><a href="/docs/fork-coupling.html">Coupled fork</a> — research physics with in-step coupling (replay, attribution chain, <a href="/artifacts/coupled_fork_demo/">JSON bundle</a>).</li>
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
        out / "tour.html",
        product_shell(
            title="First visit tour — Fragility Discovery Engine",
            page_id="workbench",
            description="A quick guided path through one replay, one run, and one attribution trace.",
            main_html="""<article class="fde-prose">
      <h2>Guided tour</h2>
      <p>A step-by-step walkthrough of the demo: replays, a live server run, attribution, the research fork, and a multi-domain composite. Each step has written explanations — read at your own pace, then press <strong>Next</strong>.</p>
      <div style="display:flex;gap:12px;flex-wrap:wrap;margin:1rem 0">
        <a class="fde-btn-primary" href="/?tour=1">Start guided tour</a>
        <a class="fde-btn-secondary" href="/?tour=1&autoplay=1&ms=8000">Autoplay (8s per step)</a>
      </div>
      <p class="fde-run-help">Use <strong>Back</strong> and <strong>Next</strong> at the bottom of each step. Exit anytime via the red <strong>Exit tour</strong> button (top-right), <strong>Esc</strong>, or the dark backdrop. All samples load from the server — see the <a href="/docs/demo-guide.html">demo guide</a>.</p>
    </article>""",
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

      <h3>Workbench validation</h3>
      <div id="hostStatus" class="fde-run-log" style="min-height:3rem;margin-bottom:1rem"><p class="fde-run-help">Loading status.json&hellip;</p></div>

      <h3>Live engine status</h3>
      <div id="hostHealth" class="fde-run-log" style="min-height:4rem"><p class="fde-run-help">Loading&hellip;</p></div>

      <h3>Demo access</h3>
      <p>This installation is meant for browser demos at the VM IP address. Custom hostnames and TLS are optional — see <a href="/docs/fork-coupling.html">coupled fork notes</a> and <code>docs/GCE_HTTPS_AND_AUTH.md</code> in the repo if you need them later.</p>

      <h3>Updating this server</h3>
      <pre class="fde-code-block">cd ~/fragility-discovery-engine
git pull
bash scripts/gce_publish_workbench.sh</pre>
      <p>From your local machine you can trigger the same update remotely: <code>powershell -File scripts/gce_deploy_public_site.ps1</code></p>
      <p>Product by <a href="https://agenticop.io">AgenticOps</a>. Source: <a href="https://github.com/AgenticOp-io/fragility-discovery-engine">GitHub</a>.</p>
    </article>
    <script>
      (function () {
        var st = document.getElementById('hostStatus');
        fetch('/status.json', { cache: 'no-store' })
          .then(function (r) { return r.json(); })
          .then(function (s) {
            var lines = [];
            lines.push('<strong>Schema:</strong> ' + (s.schema || '?'));
            lines.push('<strong>Git:</strong> ' + (s.git_head || '?') + ' · checked ' + (s.checked_utc || '?'));
            lines.push('<strong>Benchmarks:</strong> ' + (s.benchmark_validate || '?'));
            if (s.research_fork_validate) lines.push('<strong>Coupled fork bundle:</strong> ' + s.research_fork_validate);
            if (s.coupled_fork_pareto_v1) lines.push('<strong>Pareto pins:</strong> ' + s.coupled_fork_pareto_v1);
            if (s.bundled_pareto_hypervolume) lines.push('<strong>Hypervolume pins:</strong> ' + s.bundled_pareto_hypervolume);
            if (s.dns_ready != null) lines.push('<strong>DNS (' + (s.dns_host || 'hostname') + '):</strong> ' + (s.dns_ready ? 'ready' : 'pending'));
            if (s.pypi_ready) lines.push('<strong>PyPI packaging check:</strong> ' + s.pypi_ready);
            st.innerHTML = '<ul style="margin:0.5rem 0 0 0">' + lines.map(function (l) { return '<li>' + l + '</li>'; }).join('') + '</ul>';
          })
          .catch(function () {
            st.innerHTML = '<p class="fde-run-help">status.json not available (run gce_publish_workbench.sh on the VM).</p>';
          });
      })();
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
                "schema": "fragility-workbench-status-v2",
                "host": "gce",
                "release": RELEASE,
                "benchmark_validate": "pending",
                "note": "Regenerated by gce_write_workbench_status.py during gce_publish_workbench.sh",
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
        '<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0;url=/docs/installation.html"/>'
        '<title>Redirect</title></head><body><p><a href="/docs/installation.html">Installation</a></p></body></html>',
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
        '<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0;url=/docs/how-to-use.html"/>'
        '<title>Redirect</title></head><body><p><a href="/docs/how-to-use.html">How to Use</a></p></body></html>',
    )

    built = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta = {"out": str(out), "built_utc": built, "release": RELEASE, "kind": "product-workbench"}
    _write(out / "build.json", json.dumps(meta, indent=2))
    (out / ".nojekyll").write_text("", encoding="utf-8")
    return meta


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    print(json.dumps(build(args.out), indent=2))


if __name__ == "__main__":
    main()
