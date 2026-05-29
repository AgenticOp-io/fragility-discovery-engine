# How to use the Fragility Discovery Engine

This guide is the **hands-on entry point**: install, run your first scenarios, understand the output files, and use the browser-based viewers.

| More detail | Document |
|-------------|----------|
| Package layout and data flow | [Architecture](/docs/architecture.html) |
| CLI flags and output formats | [Reference](/docs/reference.html) |
| Cost and parallelism limits | [`SCALE_AND_LIMITS.md`](SCALE_AND_LIMITS.md) |

---

## 1. What this software does

The engine runs **step-by-step simulations** where each timestep applies a stress event to the simulated system. Search algorithms (Monte Carlo, genetic algorithms, attacker/defender co-evolution) test many possible stress sequences to find the ones that cause the most damage. All outputs are saved as JSON files you can replay, compare, and reproduce exactly.

**Simulation domains** (each is a separate world with different physics; all use the same stress encoding):

| Mode | What it models |
|------|----------------|
| `aggregate` | Stablecoin reserve and panic level |
| `network` | Panic spreading across a graph (synthetic or from a topology file) |
| `resource_cascade` | Overload cascading through two capacity layers |
| `service_backlog` | Operations queue and processing rate |
| `liquidity_ladder` | Financial margin eroding toward a forced sell-off |
| `inventory_buffer` | Stock level under demand surges and fulfillment problems |

Typical workflow:

1. Run a search → **replay file** or **trade-off chart**.
2. Run **counterfactuals** or **parameter sweeps** on fixed seeds.
3. Optional: **certificate** digest, **narration**, plots, static viewers.

This is a **research and engineering** tool: fixed seeds, explicit metrics, frozen benchmark results checked in CI. It is not a live trading stack, a calibrated macro model, or a compliance certification product.

What the engine is and when it fits your work: [Overview](/docs/overview.html).

---

## 2. Install and verify

**Requirements:** Python **≥ 3.11**, `pip`, `git`. Core dependencies: `numpy`, `networkx`; optional `numba` for acceleration.

### Windows (recommended: real installer, not the Store version)

```powershell
winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
cd path\to\fragility-discovery-engine
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m pytest -q
```

Optional acceleration (resource cascade): `pip install -e ".[accelerate]"` — see `scripts/install_accelerate_windows.ps1`.

### Linux / macOS

**CI parity:** after activating a venv from this clone, run `bash scripts/ci_local.sh` (same checks as the automated CI pipeline). See [Installation](/docs/installation.html) for platform-specific notes.

**Debian / Ubuntu:**

```bash
sudo apt update
sudo apt install -y git python3.12 python3.12-venv
cd fragility-discovery-engine
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
```

**Fedora / RHEL:** `sudo dnf install -y git python3.12` (or `python3.11`), then the same `python3.12 -m venv .venv` pattern.

**macOS:** install Python **≥ 3.11** via [python.org](https://www.python.org/downloads/) or Homebrew (`brew install python@3.12`), then create a venv with that interpreter.

Optional acceleration (resource cascade): `pip install -e ".[accelerate]"`.

### Quick smoke test (no full test suite)

```bash
python scripts/week1_smoke.py
```

---

## 3. Key concepts

| Concept | What it is |
|---------|------------|
| **World** | A simulation domain (one of six). It resets to known starting conditions, steps forward one timestep at a time, and reports metrics. Code: `fragility_engine.world.*`. |
| **Schedule** | The sequence of stress events applied to the world — one event per timestep, encoded as a NumPy array. The search layer generates and tests thousands of these. Code: `fragility_engine.adversary`. |
| **Rollout** | One complete run of a world from start to finish (or collapse). Produces a result with instability score, attack cost, collapse flag, and the full trajectory. Code: `fragility_engine.runner`. |
| **Replay file** | A JSON file packaging a rollout result so you can load it in the browser viewer. Contains the trajectory, event lane, metadata, and version. |
| **Explain** | Post-run analysis that re-runs the simulation with controlled changes to measure what caused the outcome. Code: `fragility_engine.explain`. |

Every run is **fully reproducible**: the same code, seeds, and flags always produce the same result.

---

## 4. Tutorial paths

Run commands from the **repository root** unless noted.

### 4.1 First replay (aggregate domain, ~1 minute)

```bash
python scripts/week1_smoke.py --export-replay replay.json
```

Open `artifacts/replay_viewer/index.html` in a browser (local HTTP server recommended: `python -m http.server 8765` from repo root, then visit `http://localhost:8765/artifacts/replay_viewer/`). Load `replay.json`.

**Narration (deterministic text summary):**

```bash
python scripts/narrate_frozen_json.py replay.json
```

### 4.2 Genetic search on aggregate (~2–5 minutes)

```bash
python scripts/run_ga_demo.py --export-replay best.json --generations 4 --population-size 12 --seed 42
```

Use `--export-minimized-replay` for a stripped-down version of the worst-case schedule. Tune `--horizon`, `--generations`, `--population-size`.

### 4.3 Reviewer-grade artifact trail (certificate + trade-off chart + replay)

```bash
python scripts/run_flagship_demo.py
```

Outputs under `artifacts/flagship/output/`. Bundle into a **certificate**:

```bash
python scripts/export_fragility_certificate.py --out cite.json --digest-json artifacts/flagship/output/best_replay.json artifacts/flagship/output/pareto_front.json
```

### 4.4 Network contagion (synthetic graph or topology file)

```bash
python scripts/run_network_demo.py --graph-kind erdos_renyi --nodes 14 --export-replay net.json
# Load topology from a JSON file (directed out-neighbors):
python scripts/run_network_demo.py --neighbor-json path/to/topology.json --export-replay net.json
```

### 4.5 Resource cascade

```bash
python scripts/run_resource_cascade_ga_demo.py --export-replay rc.json --initial-overload 0.05
```

### 4.6 Service backlog

```bash
python scripts/run_service_backlog_ga_demo.py --export-replay sb.json --initial-backlog 0.05
```

### 4.7 Liquidity ladder

```bash
python scripts/run_liquidity_ladder_ga_demo.py --export-replay ll.json --initial-margin 0.06
python scripts/export_replay.py --mode liquidity_ladder --initial-margin 0.07 --out ll_replay.json
python scripts/run_mc_demo.py --mode liquidity_ladder --samples 16 --export-replay ll_mc.json
```

Validate the frozen benchmark:

```bash
python scripts/run_benchmark_suite.py --validate
# includes liquidity_ladder_rollout_v1
```

### 4.8 Inventory buffer

Stock level `S` and fulfillment capacity `F` (both in `[0,1]`). Demand spikes drain stock; supplier/logistics shocks erode fulfillment. The system collapses when stock falls below the stockout threshold or fulfillment falls below the floor. Fixed horizon: 18 steps.

```bash
python scripts/run_inventory_buffer_ga_demo.py --export-replay inv.json
python scripts/run_inventory_buffer_ga_demo.py --export-replay inv.json --export-minimized-replay inv_min.json --seed 42
python scripts/export_replay.py --mode inventory_buffer --out inv_replay.json
```

Counterfactual and mutation-chain recipes: [`inventory_buffer_counterfactual_example.md`](inventory_buffer_counterfactual_example.md).

Validate the frozen benchmark:

```bash
python scripts/run_benchmark_suite.py --validate
# includes inventory_buffer_rollout_v1
```

### 4.9 Attacker/defender co-evolution and the trade-off chart

```bash
python scripts/run_coevolution.py --mode aggregate \
  --rounds 1 --attacker-generations 2 --attacker-population 10 \
  --defender-generations 2 --defender-population 8 \
  --export-replay coev.json --export-pareto-json pareto.json --json-summary summary.json
```

Use `--mode liquidity_ladder` (with `--initial-margin`) or any other domain the same way; see `run_coevolution.py --help`.

Open `artifacts/pareto_viewer/index.html` and load `pareto_front.json` or your `pareto.json`.

**Multi-domain comparison** (run the same attack through several worlds at once): `artifacts/composite_viewer/index.html` — bundled quad sample via Presets; regenerate with `scripts/regenerate_bundled_viewer_samples.py`.

### 4.10 Counterfactuals and parameter sweeps

```bash
python scripts/export_counterfactual.py --mode aggregate --intervention remove_steps --export-replay-dir ./cf_out
python scripts/counterfactual_epsilon_sweep.py --mode aggregate --axis initial_panic --json-out sweep.json
```

See `export_counterfactual.py --help` for other domains and intervention types.

### 4.11 Benchmark harness (frozen reference results)

```bash
python scripts/run_benchmark_suite.py --validate
```

Wall-clock on named bundles: `python scripts/benchmark_rollout.py --bundle aggregate_rollout_v1 --json`. Full index: [`benchmarks/README.md`](../benchmarks/README.md).

**Portable manifest:**

```bash
python scripts/run_benchmark_suite.py --manifest-out benchmark_manifest.json
```

Includes per-bundle details, checksums, Python and package versions, and an optional `git_commit` field.

### 4.12 Robustness sweeps, multi-domain runs

All documented with copy-paste examples in [`benchmarks/README.md`](../benchmarks/README.md):

- `fragility_robustness_sweep.py` — ensemble sweeps, physics parameter grids, `--neighbor-json-list`.
- `mechanism_design_policy_sweep.py` — defender presets + inner GA.
- `institutional_composite_demo.py` — run one attack through twin/triple/quad decoupled worlds.

**Composite output is not a replay timeline** — use narration or downstream analytics:

```bash
python scripts/institutional_composite_demo.py --triple --out composite.json
python scripts/narrate_frozen_json.py composite.json
```

### 4.13 Multi-domain preset sweeps

`fragility_robustness_stretch.py` provides three ready-made sweep presets covering all six domains:

```bash
python scripts/fragility_robustness_stretch.py --preset small    # fast smoke, ~1 min
python scripts/fragility_robustness_stretch.py --preset medium   # balanced sweep
python scripts/fragility_robustness_stretch.py --preset large    # full multi-domain grid
```

### 4.14 Fragility surface (2-D grid)

`fragility_surface.py` produces a CSV grid of instability over two parameter axes:

```bash
python scripts/fragility_surface.py --mode aggregate --axis1 initial_panic --axis2 horizon --out surface.csv
python scripts/plot_fragility_surface_csv.py surface.csv --out surface.png
```

### 4.15 Find cheapest collapse

`find_cheap_collapse.py` runs repeated samples and returns the lowest-cost schedule that still causes collapse:

```bash
python scripts/find_cheap_collapse.py --mode aggregate --samples 200 --seed 42 --out cheap.json
```

Useful for seeding counterfactual analysis from a minimal starting point.

### 4.16 Compare two replays

`compare_replays.py` prints or exports a JSON diff of two replay files, highlighting which steps diverged:

```bash
python scripts/compare_replays.py baseline.json counterfactual.json
python scripts/compare_replays.py baseline.json counterfactual.json --json-out diff.json
```

### 4.17 Hypervolume and explanation DAG

**Hypervolume** (measures quality of a trade-off curve, two objectives): `fragility_engine.benchmarks.hypervolume.hypervolume_2d_min(points, ref)`. The reference point must be strictly worse than every point on your curve.

**Explanation DAG** — a compact machine-readable record of "why did the system still collapse?":

```bash
# From a counterfactual export
python scripts/export_explanation_dag.py --from-counterfactual cf_bundle.json --out dag.json

# From a minimization report
python scripts/export_minimized_replay.py --minimization-report-out minimize_report.json --out minimized.json
python scripts/export_explanation_dag.py --from-minimization-report minimize_report.json --out dag.json
python scripts/narrate_frozen_json.py dag.json
```

### 4.18 Coupled institution research fork

Coupled peg–overload physics lives in **`forks/coupled_institution/`** (not a charter domain on `main`). Policy: [`FORK_COUPLING_RESEARCH.md`](FORK_COUPLING_RESEARCH.md).

```bash
pip install -e ".[dev]"
pip install -e forks/coupled_institution
python scripts/regenerate_coupled_fork_artifacts.py
python scripts/run_coupled_fork_demo.py --export-replay /tmp/coupled.json --export-pareto /tmp/coupled_pareto.json
python scripts/export_coupled_fork_llm_prompts.py --cite-digest
python scripts/check_coupled_fork_llm_bundles.py
```

| Artifact | Viewer / tool |
|----------|----------------|
| `sample_coupled_replay.json` | Replay (`coupled_institution_v1`, peg + overload series) |
| `sample_coupled_pareto_front.json` | Pareto (`pareto-front-v1`, `domain: coupled_institution`) |
| `coupling_strength_sweep.json` | [`artifacts/coupling_sweep_viewer/`](../artifacts/coupling_sweep_viewer/index.html) |
| `sample_coupling_comparison.json` | Coupling comparison viewer |
| `sample_coupled_mutation_chain.json` | Attribution viewer |

Static bundle: [`artifacts/coupled_fork_demo/`](../artifacts/coupled_fork_demo/). On the public workbench, choose **Coupled institution (research fork)** on [Run a scenario](https://agenticop-io.github.io/fragility-discovery-engine/run.html) when the server exposes that mode.

---

## 5. Static viewers (replay, Pareto, attribution)

| Viewer | Path | Loads |
|--------|------|--------|
| Replay timeline | `artifacts/replay_viewer/index.html` | Rollout replay JSON |
| Trade-off chart | `artifacts/pareto_viewer/index.html` | `pareto-front-v1` / `pareto_front.json` |
| Attribution chains | `artifacts/attribution_viewer/index.html` | `attribution-merge-v1`, path traces |
| Coupling sweep (fork) | `artifacts/coupling_sweep_viewer/index.html` | `coupled-institution-coupling-sweep-v1` |
| Coupling compare (fork) | `artifacts/coupling_comparison_viewer/index.html` | `coupled-institution-coupling-comparison-v1` |

Serve the **repo root** over HTTP so relative paths and presets work (`python -m http.server 8765`).

---

## 6. Output file reference

| You want | Typical schema | Produced by |
|----------|------------------------|-------------|
| Timeline replay | `schema_version` + `trajectory` | `week1_smoke`, `run_ga_demo`, `export_replay`, `run_coevolution`, … |
| Trade-off chart | `pareto-front-v1` | `export_pareto_front`, `run_coevolution --export-pareto-json`, … |
| Certificate | `fragility-certificate-v1` | `export_fragility_certificate`, `run_flagship_demo` |
| Robustness / GA sweep | `fragility-robustness-*` | `fragility_robustness_sweep.py --json` |
| Mechanism design | `fragility-mechanism-design-outer-v1` | `mechanism_design_policy_sweep.py --json` |
| Multi-domain comparison | `fragility-institutional-composite-v1` / **v2** / **v3** | `institutional_composite_demo.py --out` |
| Explanation DAG | `explanation-dag-v1` | `export_explanation_dag.py` |
| Benchmark manifest | `benchmark-manifest-v2` | `run_benchmark_suite.py --manifest-out` |
| Narration output | `narration-summary-v1` | `narrate_frozen_json.py --json-out` |

Robustness, composite, and trade-off chart files **do not** load in the replay timeline viewer.

---

## 7. Narration, plots, and LLM prompts

### 7.1 Deterministic narration

`scripts/narrate_frozen_json.py` produces a readable text summary from any artifact — replay, trade-off chart, merge, sweep, counterfactual bundles, composite, or explanation DAG:

```bash
python scripts/narrate_frozen_json.py best.json
python scripts/narrate_frozen_json.py best.json --json-out narration.json
python scripts/narrate_frozen_json.py best.json --cite-digest   # SHA-256 citation hook
```

### 7.2 Plot scripts

All plot scripts require matplotlib (`pip install -e ".[dev]"` or `".[viz]"`).

| Script | What it plots |
|--------|--------------|
| `plot_replay_timeline.py` | Replay timeline (peg ratio, instability, shock lane, collapse marker) |
| `plot_pareto_front.py` | Trade-off curve (severity vs attack cost) |
| `plot_counterfactual_bars.py` | Bar chart of instability change across counterfactual interventions |
| `plot_epsilon_sweep.py` | Line chart of instability / collapse probability over a parameter sweep |
| `plot_fragility_surface_csv.py` | Heatmap from a `fragility_surface.py` CSV |
| `plot_institutional_composite_bars.py` | Multi-domain scorecard bars from a composite file |
| `plot_coupling_sweep.py` | Coupled fork coupling_strength vs integral instability |
| `plot_coupled_pareto.py` | Coupled fork Pareto archive (severity vs attack cost) |

All accept `--style <path>` for a custom JSON style override and `--out <path>` to write PNG / SVG.

### 7.3 LLM prompt bundles

`scripts/export_llm_narration_prompt.py` exports structured prompt bundles for external LLM prose generation. The prompts are never fed back into the simulation engine.

```bash
python scripts/export_llm_narration_prompt.py --input best.json --bundle narration_v1 --out prompt_bundle.json
```

---

## 8. Performance, CI, and limits

- **Scale:** [`SCALE_AND_LIMITS.md`](SCALE_AND_LIMITS.md) — sweep sizes, GA costs, neighbor bundles.
- **CI:** run `python -m ruff check .` and `python -m pytest` locally.
- **Performance gate:** optional env `FRAGILITY_PERF_GATE` — see the root `README.md`.

---

## 9. Troubleshooting

| Problem | What to try |
|---------|-------------|
| `python` not found or wrong interpreter (Windows) | Use `py -3.12`, or the full path under `%LocalAppData%\Programs\Python\`. Avoid the Windows Store alias. |
| `matplotlib` / plot scripts fail | `pip install -e ".[dev]"` or `".[viz]"`. |
| Viewer blank or shows errors on JSON | Check the artifact type: the replay viewer only accepts **replay** files, not composite or sweep outputs. |
| Heavy sweeps / GA runs out of memory or is slow | Shrink `--nodes`, horizon, sweep lists, GA population. See [`SCALE_AND_LIMITS.md`](SCALE_AND_LIMITS.md). |
| `git: 'credential-manager-core' is not a git command` (Windows) | Unset the global helper: see [Installation — Git credential helper](/docs/installation.html). |
| Linux: `python3.12: command not found` | Install `python3.12` + `python3.12-venv`, or use **3.11** everywhere. See [Installation](/docs/installation.html). |

---

## 10. Further reading

| Document | Purpose |
|----------|---------|
| [Architecture](/docs/architecture.html) | How the code is organized, layers, and extension points |
| [Reference](/docs/reference.html) | All flags, environment variables, output schema IDs |
| [`benchmarks/README.md`](../benchmarks/README.md) | Bundle IDs, robustness sweeps, composites |
| [Installation](/docs/installation.html) | Git, OS packages, CI scripts |

---

*Hands-on guide. See the [Overview](/docs/overview.html) for what the engine is and who it fits.*
