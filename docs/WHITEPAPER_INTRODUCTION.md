# Fragility Discovery Engine — Introduction Whitepaper

**Purpose:** A high-level picture of what the code does and how you use it as an operator or reviewer—without reading the whole repository first.

**Repository:** [github.com/AgenticOp-io/fragility-discovery-engine](https://github.com/AgenticOp-io/fragility-discovery-engine)  
**Hands-on guide:** [`HOW_TO_USE.md`](HOW_TO_USE.md) · **CLI / schema lookup:** [`REFERENCE.md`](REFERENCE.md) · **Package layout:** [`ARCHITECTURE.md`](ARCHITECTURE.md)

---

## 1. What you use this for

You pick a **simulation mode** (a reference world model), run **search** or a **single rollout**, and receive **JSON files** you can archive, diff, plot, or cite:

- **Replay JSON** — timestep trajectory, events, collapse metrics.
- **Pareto JSON** — tradeoffs between instability and attack cost after multi-objective search.
- **Counterfactual / sweep JSON** — what changes if you remove shocks, shift a reset parameter, or edit the network.
- **Certificate JSON** (optional) — SHA-256 digests of artifacts plus environment fingerprints for a paper appendix.

The engine is **deterministic**: same CLI flags and seeds produce the same outputs. It is a **research and engineering** tool—not a live market feed, a calibrated bank model, or a compliance sign-off product.

---

## 2. How the code is organized (high level)

You interact almost entirely through **`scripts/*.py`** at the repo root. Those scripts call the Python package **`fragility_engine`**, which is split so physics stays separate from search and explanation:

```
  You run:  python scripts/run_ga_demo.py  …
                 │
                 ▼
  Search:   fragility_engine.adversary   (Monte Carlo, GA, Pareto, co-evolution)
                 │
                 ▼
  Rollout:  fragility_engine.runner      (genome → shock schedule → trajectory)
                 │
                 ▼
  Physics:  fragility_engine.world.*     (peg, network, cascade, backlog, margin)
                 │
                 ▼
  Output:   replay / Pareto / counterfactual JSON  (+ optional plots, narration)
```

| Part of the package | What it does for you |
|---------------------|----------------------|
| **`world/`** | Runs the simulation: reset state, step forward, record instability. You choose the mode (`aggregate`, `network`, …). |
| **`adversary/`** | Explores **shock schedules** (encoded as genomes). Monte Carlo samples random schedules; GA evolves better ones. |
| **`runner/`** | One evaluation: decode genome → apply shocks each timestep → return metrics (`integral_instability`, `attack_cost`, `collapsed`, …). |
| **`explain/`** | Compare runs: counterfactuals, ε-sweeps, mutation chains, merged attribution graphs, deterministic narration text. |
| **`network/`** | Graph topology and contagion when `simulation_mode` is `network`. |
| **`benchmarks/`** | Frozen “golden” runs in CI; `run_benchmark_suite.py --validate` checks your install matches expected metrics. |

**Important:** worlds do **not** share state inside one timestep. A **five-domain institutional composite** JSON rolls the **same schedule** through five separate models for audit summaries—it is not coupled physics.

---

## 3. Simulation modes (what you choose)

Every mode uses the **same schedule encoding**; only the physics story changes.

| Mode | What it models | Typical first script |
|------|----------------|----------------------|
| **`aggregate`** | Scalar stablecoin peg / panic | `python scripts/week1_smoke.py` |
| **`network`** | Contagion on a graph | `python scripts/run_network_demo.py` |
| **`resource_cascade`** | Overload and capacity cascade | `python scripts/run_resource_cascade_ga_demo.py` |
| **`service_backlog`** | Ops backlog vs processing rate | `python scripts/run_service_backlog_ga_demo.py` |
| **`liquidity_ladder`** | Margin stress vs funding ladder | `python scripts/run_liquidity_ladder_ga_demo.py` |

Pass `--mode <name>` on scripts that support multiple domains (`export_replay.py`, `run_mc_demo.py`, `run_coevolution.py`, `export_counterfactual.py`, etc.). Full flag matrix: [`REFERENCE.md`](REFERENCE.md).

---

## 4. End-user workflow

### 4.1 Install

Requires **CPython ≥ 3.11**. From a clone or release tag:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Tagged release without PyPI: [`RELEASING.md`](../RELEASING.md) or `bash scripts/install_release.sh v0.4.0`. Verify: `python -m pytest -q` or `bash scripts/ci_local.sh`.

### 4.2 Run search or one rollout

**Quick smoke (aggregate, ~1 min):**

```bash
python scripts/week1_smoke.py --export-replay replay.json
```

**Genetic search (find harsh schedules):**

```bash
python scripts/run_ga_demo.py --export-replay best.json --generations 4 --population-size 12 --seed 42
```

**Other domains:** swap in `run_network_demo.py`, `run_liquidity_ladder_ga_demo.py`, etc. (see [`HOW_TO_USE.md`](HOW_TO_USE.md) §4).

**Reviewer bundle (certificate + Pareto + replay in one go):**

```bash
python scripts/run_flagship_demo.py
```

### 4.3 Inspect outputs

| Output | How you view it |
|--------|------------------|
| **Replay** | Static viewer: `artifacts/replay_viewer/index.html` (serve repo with `python -m http.server`, load your JSON). |
| **Pareto** | `artifacts/pareto_viewer/index.html` |
| **Attribution / counterfactual merges** | `artifacts/attribution_viewer/index.html` |
| **Institutional composite** | `artifacts/composite_viewer/index.html` |
| **Text summary** | `python scripts/narrate_frozen_json.py replay.json` |
| **Plots** | `python scripts/plot_replay_timeline.py replay.json --out timeline.png` |

Bundled samples ship under `artifacts/` for demos without rerunning search. Map: [`BUNDLED_ARTIFACTS.md`](BUNDLED_ARTIFACTS.md).

### 4.4 Explain a result

After you have a baseline rollout (pinned seeds):

```bash
# Remove shocks vs baseline
python scripts/export_counterfactual.py --mode aggregate --intervention remove_steps --export-replay-dir ./cf_out

# Sweep one scalar (e.g. initial panic)
python scripts/counterfactual_epsilon_sweep.py --mode aggregate --axis initial_panic --out sweep.json
```

Domain-specific cookbooks: [`network_counterfactual_example.md`](network_counterfactual_example.md), [`liquidity_ladder_counterfactual_example.md`](liquidity_ladder_counterfactual_example.md), and related files in `docs/`.

### 4.5 Reproducibility check

```bash
python scripts/run_benchmark_suite.py --validate
```

Confirms six frozen bundles match golden metrics. For citations, add digests:

```bash
python scripts/export_fragility_certificate.py --out cite.json --digest-json replay.json pareto.json
```

Step-by-step appendix path: [`PAPER_APPENDIX_WORKFLOW.md`](PAPER_APPENDIX_WORKFLOW.md).

---

## 5. Main artifacts (what files mean)

| Artifact | Schema (typical) | You use it to… |
|----------|------------------|----------------|
| Replay | `schema_version` + `trajectory` + `events_lane` | See *when* shocks hit and how instability evolved. |
| Pareto front | `pareto-front-v1` | Compare severity vs cost across search archive. |
| Counterfactual pair | baseline + variant blocks | Quantify effect of one intervention. |
| Attribution merge | `attribution-merge-v1` | Compare multiple branches on one graph. |
| Institutional composite | `fragility-institutional-composite-v4` (penta) | Summarize five domains on one schedule. |
| Certificate | `fragility-certificate-v1` | Pin file hashes and environment for a paper or audit packet. |

LLM prompt export (`scripts/export_llm_narration_prompt.py`) builds **optional** prose prompts from frozen JSON; it does **not** drive the simulator.

---

## 6. Common tasks (cheat sheet)

| I want to… | Start here |
|------------|------------|
| First run, minimal setup | `week1_smoke.py` → replay viewer |
| Stress-test schedules automatically | `run_ga_demo.py` or `run_mc_demo.py --mode …` |
| Network with custom topology | `run_network_demo.py --neighbor-json topo.json` |
| Attacker vs defender | `run_coevolution.py --mode …` |
| Multi-domain audit JSON | `institutional_composite_demo.py --penta` |
| Compare “what if” scenarios | `export_counterfactual.py` / `counterfactual_epsilon_sweep.py` |
| Publication-ready bundle | `run_flagship_demo.py` + `PAPER_APPENDIX_WORKFLOW.md` |
| Confirm install matches CI | `run_benchmark_suite.py --validate` |

---

## 7. Terminology (plain language)

| You might say… | In this repo… |
|----------------|---------------|
| Stress test / scenario | Search or rollout over **shock schedules** |
| Sensitivity analysis | **ε-sweep** or scalar counterfactual on one axis |
| Robustness search | Monte Carlo or **GA** over schedules |
| Multi-objective tradeoff | **Pareto** archive (instability vs attack cost) |
| Explanation | Rule-based **counterfactual** or mutation **chain**, not model SHAP |
| Audit trail | Versioned JSON + optional **certificate** digests |

---

## 8. Limits and non-goals

- **Toy reference domains** — pedagogical physics, not calibrated to a real institution.
- **No coupled mega-model** — worlds do not exchange mass inside one `step()`; see [`FORK_COUPLING_RESEARCH.md`](FORK_COUPLING_RESEARCH.md) for fork policy.
- **CLI-first** — viewers are static HTML over JSON; there is no hosted SaaS.
- **Charter scope** is complete on `main` ([`PROJECT_STATUS.md`](PROJECT_STATUS.md)); optional stretch ideas live in [`ROADMAP_NEXT.md`](../ROADMAP_NEXT.md).

Scale, wall-clock, and parallelism: [`SCALE_AND_LIMITS.md`](SCALE_AND_LIMITS.md). Hard rules: [`BOUNDARIES.md`](../BOUNDARIES.md).

---

## 9. Where to read next

| Document | When |
|----------|------|
| [`HOW_TO_USE.md`](HOW_TO_USE.md) | Tutorials, troubleshooting, full CLI tour |
| [`REFERENCE.md`](REFERENCE.md) | Flags, env vars, schema names |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Deeper data-flow and module boundaries |
| [`benchmarks/README.md`](../benchmarks/README.md) | Bundle IDs and manifest fields |
| [`INSTALLATION.md`](INSTALLATION.md) | Git, GCE, host-specific setup |

---

## 10. Document control

| Field | Value |
|--------|--------|
| **Version** | 2.0 |
| **Last updated** | 2026-05 — end-user / code overview rewrite |
| **Repo state** | Tracks `main`; cite commit or tag `v0.4.0` with frozen JSON. |
| **Questions** | [GitHub Issues](https://github.com/AgenticOp-io/fragility-discovery-engine/issues) |
