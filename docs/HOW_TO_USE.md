# How to use the Fragility Discovery Engine

This guide is the **hands-on entry point**: install, run your first artifacts, understand JSON outputs, and use the static viewers. Normative scope and non-goals live in [`BOUNDARIES.md`](../BOUNDARIES.md). Honest complexity and sweep costs: [`SCALE_AND_LIMITS.md`](SCALE_AND_LIMITS.md).

---

## 1. What this software does

- **Search** for shock schedules (Monte Carlo, genetic algorithms, co-evolution) over **modular worlds** (aggregate peg, network contagion, resource cascade).
- **Score** runs with explicit metrics (`integral_instability`, collapse, `attack_cost`, …).
- **Export** schema-versioned JSON: replays, Pareto archives, counterfactuals, certificates, robustness sweeps, institutional composites.
- **Explain** with minimization, counterfactuals, optional deterministic **narration** and plot hooks—without claiming market calibration or regulatory compliance.

---

## 2. Install and verify

**Requirements:** CPython **≥ 3.11**, `pip`, `git`. Core deps: `numpy`, `networkx`; optional `numba` via extras.

### Windows (recommended: real installer, not Store stubs)

```powershell
winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
cd path\to\fragility-discovery-engine
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m pytest -q
```

Optional acceleration (resource cascade): `pip install -e ".[accelerate]"` — see [`phase_k_acceleration.md`](phase_k_acceleration.md) and `scripts/install_accelerate_windows.ps1`.

### Linux / macOS

```bash
cd fragility-discovery-engine
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
```

### Minimal smoke (no full test suite)

```bash
python scripts/week1_smoke.py
```

---

## 3. Core concepts (about one minute)

| Concept | Where it lives |
|--------|----------------|
| **World** | `fragility_engine.world.*` — physics only; reset + `step`. |
| **Adversary** | `fragility_engine.adversary` — encodes schedules from genomes; MC / GA search. |
| **Rollout** | `fragility_engine.runner` — decode genome → events → trajectory → `RolloutResult`. |
| **Replay JSON** | `rollout_to_replay_dict` — `schema_version`, `trajectory`, `events_lane`, `meta`. |
| **Explain** | `fragility_engine.explain` — minimization, counterfactuals, sweeps, narration. |

Everything important is **deterministic** given published seeds and CLI flags.

---

## 4. Tutorial paths

Run commands from the **repository root** unless noted.

### 4.1 First replay (aggregate, ~1 minute)

```bash
python scripts/week1_smoke.py --export-replay replay.json
```

Open `artifacts/replay_viewer/index.html` in a browser (local HTTP server recommended: `python -m http.server 8765` from repo root, then visit `http://localhost:8765/artifacts/replay_viewer/`). Load `replay.json`. See [`artifacts/replay_viewer/README.md`](../artifacts/replay_viewer/README.md) for what JSON this viewer accepts.

**Narration (deterministic text):**

```bash
python scripts/narrate_frozen_json.py replay.json
```

### 4.2 Genetic adversary on aggregate (~2–5 minutes)

```bash
python scripts/run_ga_demo.py --export-replay best.json --generations 4 --population-size 12 --seed 42
```

Use `--export-minimized-replay` for greedy-minimized schedules. Tune `--horizon`, `--generations`, `--population-size`.

### 4.3 Reviewer-grade trail (certificate + Pareto + replay)

One scripted path: [`PAPER_APPENDIX_WORKFLOW.md`](PAPER_APPENDIX_WORKFLOW.md).

```bash
python scripts/run_flagship_demo.py
```

Outputs under `artifacts/flagship/output/` (see `artifacts/flagship/README.md`). Digest artifacts into **`fragility-certificate-v1`**:

```bash
python scripts/export_fragility_certificate.py --out cite.json --digest-json artifacts/flagship/output/best_replay.json artifacts/flagship/output/pareto_front.json
```

### 4.4 Network contagion (synthetic graph or neighbor JSON)

```bash
python scripts/run_network_demo.py --graph-kind erdos_renyi --nodes 14 --export-replay net.json
# List topology from JSON (directed out-neighbors):
python scripts/run_network_demo.py --neighbor-json path/to/topology.json --export-replay net.json
```

Counterfactuals and examples: [`network_counterfactual_example.md`](network_counterfactual_example.md).

### 4.5 Resource cascade (second reference domain)

```bash
python scripts/run_resource_cascade_ga_demo.py --export-replay rc.json --initial-overload 0.05
```

Concepts: [`phase_j_resource_cascade.md`](phase_j_resource_cascade.md), narrative: [`WHY_RESOURCE_CASCADE.md`](WHY_RESOURCE_CASCADE.md).

### 4.6 Co-evolution and Pareto viewer

```bash
python scripts/run_coevolution.py --mode aggregate --generations 2 --population-size 10 --export-replay --export-pareto-json pareto.json --json-summary summary.json
```

Open `artifacts/pareto_viewer/index.html` and load `pareto_front.json` / your `pareto.json` (see viewer folder for preset behavior).

### 4.7 Counterfactuals and ε-sweeps

```bash
python scripts/export_counterfactual.py --mode aggregate --intervention remove_steps --export-replay-dir ./cf_out
python scripts/counterfactual_epsilon_sweep.py --mode aggregate --axis initial_panic --json-out sweep.json
```

Network / cascade modes and axes vary; see `export_counterfactual.py --help` and the counterfactual cookbooks in `docs/`.

### 4.8 Benchmark harness (golden bundles)

```bash
python scripts/run_benchmark_suite.py --validate
```

Wall-clock on named bundles: `python scripts/benchmark_rollout.py --bundle aggregate_rollout_v1 --json`. Full index: [`benchmarks/README.md`](../benchmarks/README.md).

**Portable manifest (`benchmark-manifest-v2`):**

```bash
python scripts/run_benchmark_suite.py --manifest-out benchmark_manifest.json
```

Includes per-bundle topology hints, `golden_metrics_sha256`, Python/NumPy/package versions, optional `git_commit`, and pointers to **2-D minimization hypervolume** (`fragility_engine.benchmarks.hypervolume`) plus **`explanation-dag-v1`** export.

### 4.9 Robustness sweeps, mechanism design, institutional composite

All documented with copy-paste examples in [`benchmarks/README.md`](../benchmarks/README.md), including:

- `fragility_robustness_sweep.py` — ensembles, physics sweeps, GA budget modes, `--neighbor-json-list`.
- `mechanism_design_policy_sweep.py` — defender presets + inner GA.
- `institutional_composite_demo.py` — twin (**v1**) or `--triple` (**v2**) decoupled multi-kernel metrics.

**Composite JSON is not a replay timeline** — use JSON tools, narration, or downstream analytics:

```bash
python scripts/institutional_composite_demo.py --triple --out composite.json
python scripts/narrate_frozen_json.py composite.json
```

### 4.10 Hypervolume (Pareto analysis) and explanation DAG

**Hypervolume** (two objectives, both minimized): use `fragility_engine.benchmarks.hypervolume.hypervolume_2d_min(points, ref)`. The reference point must be **strictly worse** (larger on both axes) than every point on your non-dominated front.

**Mechanical explanation DAG** (`explanation-dag-v1`) — summarize structure without LLMs:

```bash
# From a counterfactual export (baseline + counterfactual + intervention)
python scripts/export_explanation_dag.py --from-counterfactual cf_bundle.json --out dag.json

# From greedy minimization report (capture sidecar when exporting minimized replay)
python scripts/export_minimized_replay.py --minimization-report-out minimize_report.json --out minimized.json
python scripts/export_explanation_dag.py --from-minimization-report minimize_report.json --out dag.json
python scripts/narrate_frozen_json.py dag.json
```

**Research frontiers** (third world beyond cascade, coupled mega-models — **not** shipped here): [`RESEARCH_FRONTIERS.md`](RESEARCH_FRONTIERS.md).

---

## 5. Static browsers (replay, Pareto, attribution)

| Viewer | Path | Loads |
|--------|------|--------|
| Replay timeline | `artifacts/replay_viewer/index.html` | Rollout replay JSON (`rollout_to_replay_dict` contract) |
| Pareto | `artifacts/pareto_viewer/index.html` | `pareto-front-v1` / `pareto_front.json` |
| Attribution | `artifacts/attribution_viewer/index.html` | `attribution-merge-v1`, path traces |

Serve the **repo root** over HTTP so relative paths and optional presets work (`python -m http.server 8765`). Bulk sample exports: `scripts/regenerate_test_exports.ps1` / `.sh` → `artifacts/test_exports/` (often gitignored); see `artifacts/README_test_exports.txt`.

---

## 6. Artifact cheat sheet

| You want | Typical schema / shape | Produced by |
|----------|------------------------|-------------|
| Timeline replay | `schema_version` + `trajectory` | `week1_smoke`, `run_ga_demo`, `export_replay`, `run_coevolution`, … |
| Pareto archive | `pareto-front-v1` | `export_pareto_front`, `run_coevolution --export-pareto-json`, … |
| Certificate | `fragility-certificate-v1` | `export_fragility_certificate`, `run_flagship_demo` |
| Robustness / GA sweep | `fragility-robustness-*` | `fragility_robustness_sweep.py --json` |
| Mechanism design | `fragility-mechanism-design-outer-v1` | `mechanism_design_policy_sweep.py --json` |
| Institutional composite | `fragility-institutional-composite-v1` / **v2** | `institutional_composite_demo.py --out` |
| Explanation DAG | `explanation-dag-v1` | `export_explanation_dag.py` |
| Benchmark manifest | `benchmark-manifest-v2` | `run_benchmark_suite.py --manifest-out` |
| Narration output | `narration-summary-v1` | `narrate_frozen_json.py --json-out` |

Robustness / composite / Pareto JSON **do not** load in the replay timeline viewer — see [`artifacts/replay_viewer/README.md`](../artifacts/replay_viewer/README.md).

---

## 7. Narration, plots, LLM prompt packs (Phase L)

- **Deterministic narration:** `scripts/narrate_frozen_json.py` — works on replay, Pareto, merge, epsilon-sweep, counterfactual bundles, **institutional composite v1/v2**, **`explanation-dag-v1`**.
- **Machine-readable summary:** `--json-out narration.json`.
- **Citation hook:** `--cite-digest` (SHA-256 of file bytes + path).
- **Plots:** `scripts/plot_*.py` require matplotlib (`pip install -e ".[dev]"` or `".[viz]"`). Index: [`phase_l_publication.md`](phase_l_publication.md).
- **LLM prompt export (optional):** `scripts/export_llm_narration_prompt.py` — external prose only; never fed back into simulation.

---

## 8. Performance, CI, and limits

- **Scale:** [`SCALE_AND_LIMITS.md`](SCALE_AND_LIMITS.md) — sweep grid sizes, GA costs, neighbor bundles.
- **CI:** root `README.md` badge; local parity with `python -m ruff check .` and `python -m pytest`.
- **Perf gate:** optional env `FRAGILITY_PERF_GATE` (see `README.md` Extending section).

---

## 9. Troubleshooting

| Problem | What to try |
|---------|-------------|
| `python` not found or wrong interpreter (Windows) | Use `py -3.12`, or full path under `%LocalAppData%\Programs\Python\`; avoid Windows Store alias. |
| `matplotlib` / plot scripts fail | `pip install -e ".[dev]"` or `".[viz]"`. |
| Viewer blank or errors on JSON | Confirm artifact type: replay viewer needs **replay** JSON, not composite or sweep payloads. |
| Heavy sweeps / GA OOM or slow | Shrink `--nodes`, horizons, sweep lists, GA populations; read [`SCALE_AND_LIMITS.md`](SCALE_AND_LIMITS.md). |

---

## 10. Further reading

| Document | Purpose |
|----------|---------|
| [`BOUNDARIES.md`](../BOUNDARIES.md) | Phases, exit criteria, non-goals |
| [`ROADMAP_NEXT.md`](../ROADMAP_NEXT.md) | Aspirational directions |
| [`benchmarks/README.md`](../benchmarks/README.md) | Bundle IDs, robustness CLIs, composites |
| [`PAPER_APPENDIX_WORKFLOW.md`](PAPER_APPENDIX_WORKFLOW.md) | One end-to-end reviewer path |
| [`GCE_DEPLOY_KEY.md`](GCE_DEPLOY_KEY.md) | VM deploy keys |
| [`RESEARCH_FRONTIERS.md`](RESEARCH_FRONTIERS.md) | Third-domain gate, coupled dynamics (non-goals) |

---

*This file is maintained as the primary **user-oriented** guide; the root [`README.md`](../README.md) stays the project overview and full script table.*
