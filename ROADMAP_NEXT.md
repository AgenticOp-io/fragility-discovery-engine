# Next roadmap — after Phase G

This document is **aspirational and directional**. It proposes where the project can become **genuinely novel** without confusing ambition with scope creep.

**Normative law still lives in [`BOUNDARIES.md`](BOUNDARIES.md):** hard gates, exit criteria, and non-goals override enthusiasm. Treat this file as **prioritized intent**; promote sections into `BOUNDARIES.md` only when you are ready to commit engineering + tests.

---

## What “breathtaking” means here (operational)

Groundbreaking, for this codebase, is **not** a bigger dashboard or more graph models. It is:

1. **Reproducible fragility claims** — any reported collapse or frontier comes with a **frozen artifact trail** (seeds, configs, replay JSON, hashes) that a third party can rerun and reconcile.
2. **Structural explanations** — attributions tie collapse to **explicit interventions** (schedules, topology, defenses), not narrated vibes.
3. **Honest scale** — performance and realism bounds are **stated and tested**; sparse/list topology and optional backends are admitted tradeoffs, not marketing.
4. **Transfer without chaos** — a **second reference domain** proves the *engine pattern* generalizes while keeping one kernel “golden” for regression.

If a feature weakens determinism, blurs world/adversary separation, or ships without tests, it is **not** on-brand—however impressive it sounds.

---

## Strategic pillars (unchanging constraints)

| Pillar | Requirement |
|--------|-------------|
| **Evidence-first** | Schema-versioned JSON / CSV artifacts precede UI polish. |
| **Two-objective discipline** | New objectives enter as **paired** axes + archive, not a twelve-axis scorecard (see `BOUNDARIES.md` fitness discipline). |
| **Modular worlds** | Physics stays in `world/`; search stays in `adversary/`; attribution in `explain/`. |
| **Co-evolution as stress test** | Attacker–defender loops remain the **hardest integration test** for determinism and explanation quality. |

---

## Proposed phases (H onward)

Work **does not start** on a phase until prior phases are green in CI **and** `BOUNDARIES.md` is updated to adopt that phase’s gates.

**Phase H is adopted** — see **`BOUNDARIES.md` (Phase H)** for normative exit criteria. Further Phase H work (manifest JSON, hypervolume proxies, scheduled workflows) remains optional backlog.

**Phase I (network explanation grammar)** — see **`BOUNDARIES.md` (Phase I)** for shipped counterfactuals, ε-sweeps, merges, chains, and path traces.

### Phase H — Fragility certificates & benchmark harness

**Purpose:** Turn ad hoc scripts into a **portable, auditable benchmark layer**: comparable runs across machines and time.

**In scope:**

- **Benchmark bundles**: versioned directories or single manifest JSON listing topology source, neighbor JSON hashes, GA budgets, seeds, CLI invocation fingerprints.
- **Regression targets**: metric ceilings/floors on **integral instability**, collapse rate under fixed budgets, Pareto hypervolume proxies (simple, documented)—not only wall-clock (`FRAGILITY_PERF_GATE` stays auxiliary).
- **`pytest` + subprocess** coverage for “golden” bundles (small graphs, short horizons) checked into `artifacts/benchmarks/` or `tests/fixtures/benchmarks/` (small files only).

**Out of scope:**

- Claiming industry certification or regulatory compliance.

**Exit criteria (candidate):**

- [x] At least **three** frozen benchmark bundles runnable via one documented command (`python scripts/run_benchmark_suite.py`, `benchmarks/README.md`).
- [x] CI runs bundles via **`pytest`** (`tests/test_benchmark_suite.py`) with numeric golden tolerances.
- [x] Reproduction / citation notes (`benchmarks/README.md`; link from root `README.md`).

---

### Phase I — Network-native explanation grammar

**Purpose:** Counterfactuals and minimization already exist; **network worlds** need first-class **structured** comparisons (still deterministic, still modest claims).

**In scope:**

- **Counterfactual vocabulary**: e.g. remove shocks at timestep *t* conditioned on **node exposure** summaries; ε-sweeps on **base_panic** or single-edge weight scalings where JSON topology allows.
- **Explanation DAG (optional JSON)** derived mechanically from minimization + counterfactual steps—edges labeled by intervention type, not LLM prose.
- Extended replay `meta` fields **behind schema bump** with migration notes.

**Out of scope:**

- General causal identification theory or “proved necessity” without assumptions stated in machine-readable form.

**Exit criteria (candidate):**

- [x] `explain/` APIs + tests — **base_panic** + **contagion_beta** shifts (`tests/test_counterfactual_network_interventions.py`).
- [x] CLI `export_counterfactual --intervention …` + `BOUNDARIES.md` Phase I.
- [x] Worked example: [`docs/network_counterfactual_example.md`](docs/network_counterfactual_example.md).
- [x] Scalar ε-sweeps (`explain/sweep.py`, `counterfactual_epsilon_sweep.py`).
- [x] Linear explanation trace from sweeps (`explain/trace.py`, `--emit-trace`); aggregate `initial_panic` sweep; resource_cascade `initial_overload` sweep (`sweep_resource_cascade_initial_overload`).

**Phase I partial adoption** — star-merge, single-edge weights, cumulative mutation chains, and **path traces** over intermediate chain rollouts (`explanation-mutation-chain-path-v1`) are shipped.

---

### Phase J — Second reference domain (single flight)

**Purpose:** Demonstrate that the **architecture** is the product—not only the stablecoin toy.

**Scaffold shipped:** `ResourceCascadeWorld` + `rollout_resource_cascade` — see [`docs/phase_j_resource_cascade.md`](docs/phase_j_resource_cascade.md).

**Candidates (pick one when gate opens — canonical narrative still open):**

- Contagion + resource allocation on a **different** liability structure (not crypto-themed).
- Infrastructure-style **cascade** with overload + recovery (still discrete-time, still thin agents).

**Hard rules:**

- Exactly **one** new domain in flight; **max 3–5** archetypes (`BOUNDARIES.md`).
- Stablecoin kernel remains **CI oracle**: no release regresses aggregate/network parity tests already shipped.

**Exit criteria (candidate):**

- [x] New `world/` module + replay schema compatibility table — [`docs/phase_j_resource_cascade.md`](docs/phase_j_resource_cascade.md).
- [x] GA smoke + determinism tests — `scripts/run_resource_cascade_ga_demo.py`, `tests/test_resource_cascade_rollout.py`, `tests/test_replay_contract_resource_cascade.py`.
- [x] README “Why this domain” ≤ 1 page — [`docs/WHY_RESOURCE_CASCADE.md`](docs/WHY_RESOURCE_CASCADE.md) (+ root README pointer).
- [x] Co-evolution / Pareto on `ResourceCascadeWorld` — `alternating_coevolution_resource_cascade`, `scripts/run_coevolution.py --mode resource_cascade`, `scripts/export_pareto_front.py --mode resource_cascade`.
- [x] Cumulative mutation chains + path trace — `explain/counterfactual_chain_resource_cascade.py`, `scripts/export_resource_cascade_counterfactual_chain.py`, `tests/test_counterfactual_chain_resource_cascade.py`.

---

### Phase K — Honest performance & optional accelerated backends

**Purpose:** Grow **n** and budgets without lying about complexity.

**Scaffold:** [`docs/phase_k_acceleration.md`](docs/phase_k_acceleration.md) — hook points, non-goals, optional env-flag pattern.

**In scope:**

- **World protocol / ABC** (if not already explicit): swap NumPy stepper for **optional** accelerated backend **without** changing search semantics (golden tests against NumPy).
- **Batch evaluation**: independent seeds rolled out in parallel **only** where bitwise reproducibility is preserved per seed (document ordering discipline).

**Out of scope:**

- “Real-time market simulation” or implicit coupling to external feeds (`BOUNDARIES.md`).

**Exit criteria (candidate):**

- [x] Reproducible wall-clock harness on **named** Phase H bundles (`benchmark_rollout.py --bundle <id>`, table in [`docs/phase_k_acceleration.md`](docs/phase_k_acceleration.md)).
- [x] Documented **speedup measurement** for resource cascade: paired bundle benchmarks vs NumPy + reference NumPy timing snapshot ([`docs/phase_k_acceleration.md`](docs/phase_k_acceleration.md)); Numba ratio is operator-measured after `[accelerate]` install.
- [x] CI **`numba-parity`** job (Ubuntu, `[accelerate]`) runs `tests/test_resource_cascade_numba_parity.py`; main matrix stays NumPy-only.
- [x] Fallback path always available (acceleration optional dependency; default NumPy `rollout_resource_cascade`, env `FRAGILITY_RESOURCE_CASCADE_BACKEND`).
- [x] **Batch helper:** `parallel_rollouts.thread_pool_map_ordered` + ordering / shared-template caveat in [`docs/phase_k_acceleration.md`](docs/phase_k_acceleration.md); tests `tests/test_parallel_rollouts.py`.
- [x] **Optional process pool:** `eval_pool='processes'` on `monte_carlo_search` / `genetic_search` / `genetic_vector_search` when `rollout_fn` is picklable (e.g. `functools.partial(rollout_bundle_with_genome, bundle_id, isolate=True)`); `process_pool_map_ordered` + pickle preflight.
- [x] **MC across domains:** `scripts/run_mc_demo.py --mode aggregate|network|resource_cascade` + `--eval-pool` (threads default).
- [x] **Unified bench entry:** `scripts/run_benchmark_suite.py --bench-search mc|ga` (+ `--eval-workers`, `--eval-pool`, search budget flags) delegates to `run_phase_h_search_microbench` in `benchmarks/suite.py`.

---

### Phase L — Narration & publication layer (**adopted**)

**Normative detail:** [`BOUNDARIES.md`](BOUNDARIES.md) (Phase L) + CLI index [`docs/phase_l_publication.md`](docs/phase_l_publication.md).

**Shipped:**

- Deterministic narration in **`fragility_engine.explain.narration`** + [`scripts/narrate_frozen_json.py`](scripts/narrate_frozen_json.py) (`--cite-digest`, **`narration-summary-v1`**).
- Versioned LLM prompt pack (**`artifacts/llm_prompts/narration_v1/`**) + [`scripts/export_llm_narration_prompt.py`](scripts/export_llm_narration_prompt.py) (**`llm-prompt-bundle-v1`**; optional **`--invoke-openai`** via stdlib HTTP).
- Figures: replay timeline, ε-sweep, Pareto scatter, fragility-surface heatmap (`scripts/plot_*.py`, **`artifacts/plot_styles/`**).

**Follow-ups (non-gates):** extra prompt packs / plot types ship incrementally — see `artifacts/llm_prompts/*`, `scripts/plot_*.py`.

---

## Moonshots (explicitly post–Phase L or fork)

These are **not** commitments—ideas worth protecting from premature implementation:

- **Fragility robustness** (**partial / shipped slice**): deterministic **ensemble over `graph_seed`** with quantile summaries — `fragility_engine.benchmarks.ensemble`, `scripts/fragility_robustness_sweep.py`. Still to explore: GA budget sweeps, WS ensembles, neighbor-list priors, collapse-rate sensitivity grids.
- **Mechanism design loop**: outer search over **policy rules** (discrete or low-dimensional) with inner adversary—only if Phase H benchmarks exist.
- **Synthetic institutional scenarios**: composite worlds built from **composed** kernels with explicit interfaces—never as a single monolithic “mega-model.”

---

## Promotion workflow

1. Copy the **Purpose / In scope / Out of scope / Exit criteria** of an adopted phase into `BOUNDARIES.md`.
2. Open a tracking issue per exit criterion with **one acceptance test** named up front.
3. Prefer **small PRs** that close single criteria over mega-diffs.

---

## Relationship to the north star

The one-sentence north star in `BOUNDARIES.md` stays valid. This roadmap adds what comes **after** the stablecoin + topology + economics + explanation + co-evolution spine: **certification-grade reproducibility**, **richer structural attribution**, **domain transfer**, **honest scale**, and **human-facing packaging**—each gated so “breathtaking” remains **defensible**, not cosmetic.
