# Next roadmap — after the H–M spine

This document is **aspirational and directional**: what to do **after** certificates, frozen benchmarks, network explanations, two extra reference worlds, acceleration hooks, narration, and the third domain are **shipped**—without turning wish lists into scope creep.

**Normative law still lives in [`BOUNDARIES.md`](BOUNDARIES.md):** hard gates, exit criteria, and non-goals override enthusiasm. Treat this file as **prioritized intent**; promote sections into `BOUNDARIES.md` only when you are ready to commit engineering + tests.

---

## What counts as a strong outcome (operational)

For this codebase, progress is **not** measured by a bigger dashboard or more graph models. It is:

1. **Reproducible fragility claims** — any reported collapse or frontier comes with a **frozen artifact trail** (seeds, configs, replay JSON, hashes) that a third party can rerun and reconcile.
2. **Explanations tied to explicit changes** — results link to **named interventions** (schedules, topology, defenses), not free-form story alone.
3. **Honest scale** — performance and realism bounds are **stated and tested**; sparse/list topology and optional backends are admitted tradeoffs, not marketing.
4. **Transfer without chaos** — **second and third** reference domains prove the *engine pattern* generalizes while **aggregate + network + cascade + backlog** bundles stay frozen **regression oracles** unless the charter explicitly revises them.

If a feature weakens determinism, blurs world/adversary separation, or ships without tests, it is **outside the project rules**—however impressive it sounds.

---

**Operator guide:** step-by-step install, CLI walkthroughs, static viewers, and artifact map — [`docs/HOW_TO_USE.md`](docs/HOW_TO_USE.md).

**Research frontiers (third domain, coupling — explicit non-goals vs shipped tooling):** [`docs/RESEARCH_FRONTIERS.md`](docs/RESEARCH_FRONTIERS.md).

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

**Phase N (fourth reference domain)** is drafted **below** as a named slot only—it is **not** normative until a matching section lands in `BOUNDARIES.md`.

**Phase H is adopted** — see **`BOUNDARIES.md` (Phase H)** for normative exit criteria. Further Phase H work (scheduled CI, richer manifest fields, Pareto hypervolume on frozen search exports) remains optional backlog; the portable manifest already carries **golden digest**, **topology**, **provenance**, an **artifact schema index**, and a **frozen 2-D hypervolume regression fixture** (`build_benchmark_manifest`).

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

- [x] Reproducible wall-clock harness on **named** frozen suite bundles (`benchmark_rollout.py --bundle <id>`; Phase H charter, table in [`docs/phase_k_acceleration.md`](docs/phase_k_acceleration.md)).
- [x] Documented **speedup measurement** for resource cascade: paired bundle benchmarks vs NumPy + reference NumPy timing snapshot ([`docs/phase_k_acceleration.md`](docs/phase_k_acceleration.md)); Numba ratio is operator-measured after `[accelerate]` install.
- [x] CI **`numba-parity`** job (Ubuntu, `[accelerate]`) runs `tests/test_resource_cascade_numba_parity.py`; main matrix stays NumPy-only.
- [x] Fallback path always available (acceleration optional dependency; default NumPy `rollout_resource_cascade`, env `FRAGILITY_RESOURCE_CASCADE_BACKEND`).
- [x] **Batch helper:** `parallel_rollouts.thread_pool_map_ordered` + ordering / shared-template caveat in [`docs/phase_k_acceleration.md`](docs/phase_k_acceleration.md); tests `tests/test_parallel_rollouts.py`.
- [x] **Optional process pool:** `eval_pool='processes'` on `monte_carlo_search` / `genetic_search` / `genetic_vector_search` when `rollout_fn` is picklable (e.g. `functools.partial(rollout_bundle_with_genome, bundle_id, isolate=True)`); `process_pool_map_ordered` + pickle preflight.
- [x] **MC across domains:** `scripts/run_mc_demo.py --mode aggregate|network|resource_cascade` + `--eval-pool` (threads default).
- [x] **Unified bench entry:** `scripts/run_benchmark_suite.py --bench-search mc|ga` (+ `--eval-workers`, `--eval-pool`, search budget flags) delegates to `run_phase_h_search_microbench` in `benchmarks/suite.py`.
- [x] **Citable artifact trail:** `fragility-certificate-v1` (`fragility_engine.benchmarks.certificate`), `scripts/export_fragility_certificate.py`, `scripts/run_flagship_demo.py`, plus reviewer path [`docs/PAPER_APPENDIX_WORKFLOW.md`](docs/PAPER_APPENDIX_WORKFLOW.md) and [`docs/SCALE_AND_LIMITS.md`](docs/SCALE_AND_LIMITS.md).

---

### Phase L — Narration & publication layer (**adopted**)

**Normative detail:** [`BOUNDARIES.md`](BOUNDARIES.md) (Phase L) + CLI index [`docs/phase_l_publication.md`](docs/phase_l_publication.md).

**Shipped:**

- Deterministic narration in **`fragility_engine.explain.narration`** + [`scripts/narrate_frozen_json.py`](scripts/narrate_frozen_json.py) (`--cite-digest`, **`narration-summary-v1`**).
- Versioned LLM prompt pack (**`artifacts/llm_prompts/narration_v1/`**) + [`scripts/export_llm_narration_prompt.py`](scripts/export_llm_narration_prompt.py) (**`llm-prompt-bundle-v1`**; optional **`--invoke-openai`** via stdlib HTTP).
- Figures: replay timeline, ε-sweep, Pareto scatter, fragility-surface heatmap (`scripts/plot_*.py`, **`artifacts/plot_styles/`**).

**Follow-ups (non-gates):** extra prompt packs / plot types ship incrementally — see `artifacts/llm_prompts/*`, `scripts/plot_*.py`.

---

### Phase M — Third reference domain (**adopted / shipped**)

**Purpose:** Ship a **third** thin `World` that reuses the existing shock schedule encoding, exports replay JSON under a documented contract, and lands a **frozen benchmark bundle** under the Phase H gate — proving another physics story on the same engine spine without coupling worlds.

**Normative gate:** [`BOUNDARIES.md`](BOUNDARIES.md) (Phase M) + checklist [`docs/phase_m_third_reference_domain.md`](docs/phase_m_third_reference_domain.md).

**Status:** **Shipped** — `ServiceBacklogWorld` / `service_backlog` / `service_backlog_rollout_v1` + GA demo `scripts/run_service_backlog_ga_demo.py` + co-evolution / Pareto / MC / counterfactual / ε-sweep wiring (see [`docs/phase_m_third_reference_domain.md`](docs/phase_m_third_reference_domain.md) §4).

**Hard rules:**

- Exactly **one** Phase M physics line in flight; **max 3–5** archetypes.
- Aggregate + network + **Phase J** cascade + **Phase M** backlog remain default **CI golden anchors** unless charter is explicitly revised.
- No **coupled** mega-institution `World` (cross-domain state in one `step`) under Phase M — that is out of charter (`docs/RESEARCH_FRONTIERS.md`).

**Exit criteria (Phase M v1):**

- [x] `world/` module + `runner` rollout + `rollout_to_replay_dict` row in compatibility doc.
- [x] Determinism + replay contract tests.
- [x] GA smoke CLI `run_service_backlog_ga_demo.py`.
- [x] Frozen suite bundle `service_backlog_rollout_v1` + `GOLDEN_METRICS` + `tests/test_benchmark_suite.py` (Phase H charter).
- [x] “Why this domain” doc — [`docs/WHY_SERVICE_BACKLOG.md`](docs/WHY_SERVICE_BACKLOG.md).
- [x] Co-evolution / Pareto / counterfactuals / MC / ε-sweeps for `service_backlog` mode.

**Follow-ups (non-gates):**

- Narration / plot parity for **quad** institutional composite JSON where gaps remain (same rule as other artifacts: deterministic summaries only).
- Optional **preset packs** for static viewers so flagship + composite demos load without hand-picking paths (still HTTP-served; no new runtime coupling to worlds). **Partial:** attribution viewer presets + `artifacts/composite_demo/sample_quad_composite.json`; regenerate via `scripts/regenerate_bundled_viewer_samples.py`.

---

## Near-term backlog (no new phase letter yet)

Concrete improvements that **reuse** existing phases—promote into `BOUNDARIES.md` only when you want them **normative**.

**Local CI parity (shipped):** [`scripts/ci_local.sh`](../scripts/ci_local.sh) (Linux / macOS / WSL) and [`scripts/ci_local.ps1`](../scripts/ci_local.ps1) (Windows) mirror the default **test** job (**ruff** + **pytest** + perf gate env) and run **`python scripts/run_benchmark_suite.py --validate`**. Optional **`FRAGILITY_CI_LOCAL_BUILD=1`** runs **`python -m build`** (CI **build** job). Quick checklist: [`docs/NEXT_STEPS.md`](NEXT_STEPS.md).

### Benchmark layer (Phase H charter)

| Track | Intent | Notes |
|--------|--------|--------|
| **Regression metrics beyond wall-clock** | Optional **floors / ceilings** on shipped scalars (e.g. integral instability bands) for one or two bundles | **`BUNDLE_INTEGRAL_BANDS`** + `validate_benchmark_suite()`; manifest **`bundle_integral_bands`**; digest pin via **`check_manifest_digest.py`** |
| **Manifest as review artifact** | Treat `benchmark-manifest-v2` as the **inventory** for a paper appendix: schema index, golden digest, topology hints | **`python scripts/run_benchmark_suite.py --manifest-summary`** prints a log-friendly excerpt; **`--manifest-out`** unchanged |
| **Pareto on frozen search exports** | Pin **one** small GA/MC export + **2-D hypervolume** expectation alongside replay bundles | Fits existing `hypervolume_2d_min` + pinned fixtures; avoid unbounded archive sizes |
| **Scheduled job coverage** | Align **weekly** workflow artifacts with the same validation path as PR CI | Reduces “green locally, stale scheduled” surprises |

### Explanation grammar (Phase I charter)

| Track | Intent | Notes |
|--------|--------|--------|
| **Aggregate / network multi-knob chains** | Extend **cumulative** mutation chains where a single scalar shift is not enough—**still** behind explicit CLI and tests | **Aggregate:** `aggregate-mutation-chain-spec-v1`, `export_aggregate_counterfactual_chain.py`, path trace `explanation-mutation-chain-path-aggregate-v1` |
| **Interaction summaries** | More **merge** shapes (e.g. triple-branch institutional summaries) **without** claiming Shapley identification | Keep **`attribution-interaction-summary-v1`**-style disclaimers |

### Narration & figures (Phase L charter)

| Track | Intent | Notes |
|--------|--------|--------|
| **Prompt packs** | Additional **`llm-prompt-bundle-v1`** packs for **reviewer memo** / **appendix** variants | **`institution_composite_v1`** for quad/triple composite JSON |
| **Plot types** | One new **plot script + style JSON** per PR where possible | **`plot_institutional_composite_bars.py`** + `fragility-plot-institutional-composite-style-v1` |

---

### Phase N — Fourth reference domain (**charter slot — not open**)

**Status:** **Not adopted** — there is **no** Phase N section in [`BOUNDARIES.md`](BOUNDARIES.md) yet. Draft admission memo: [`docs/phase_n_fourth_domain_admission.md`](docs/phase_n_fourth_domain_admission.md).

**Purpose:** If the project needs **another** thin `World` (same shock-schedule encoding, new physics story, new frozen bundle), **Phase N** would be the umbrella—**not** a silent expansion of Phase M.

**Hard rules (draft — must be copied into `BOUNDARIES.md` before work starts):**

- At most **one** new `world/` physics experiment under **Phase N** at a time; **max 3–5** archetypes (`BOUNDARIES.md` immutable principles).
- Existing bundles (`aggregate_rollout_v1`, `network_*`, `resource_cascade_rollout_v1`, `service_backlog_rollout_v1`) remain **oracles** unless a charter revision explicitly replaces one.
- **No** cross-`World` coupling inside `step()`; decoupled **composite** JSON remains the audit pattern for multi-kernel stress. Coupled dynamics stay **fork policy**: [`docs/FORK_COUPLING_RESEARCH.md`](docs/FORK_COUPLING_RESEARCH.md).

**Exit criteria (candidate — all unchecked until adoption):**

- [ ] Admission memo (selected candidate, non-goals, replay contract row) checked into `docs/` and linked from `BOUNDARIES.md`.
- [ ] `world/` + `runner` rollout + `rollout_to_replay_dict` compatibility table updated.
- [ ] Determinism + replay contract tests + GA smoke CLI.
- [ ] New **frozen** `*_rollout_v1` bundle id + `GOLDEN_METRICS` row + `tests/test_benchmark_suite.py` coverage.
- [ ] “Why this domain” doc (≤ one page) + counterfactual / ε-sweep / co-evolution **parity** with the pattern used for Phase J / Phase M unless explicitly scoped down with documented reasons.

---

## Cross-cutting themes (post–M)

These span multiple packages; pick **one thin slice** per PR.

- **Observability of reproducibility:** make it trivial to answer “which bundle id, which commit, which Python/numpy” from a single JSON field or manifest subsection (certificate + manifest already move this direction).
- **Contributor guardrails:** expand **CLI smoke** coverage for new scripts before they grow flags; keep `docs/HOW_TO_USE.md` the **single** tutorial index.
- **Research honesty:** when a feature sounds like a “digital twin,” add a **non-goals** bullet beside it or push it to [`docs/RESEARCH_FRONTIERS.md`](docs/RESEARCH_FRONTIERS.md).

---

## Exploration slices (post–Phase L or fork)

Shipped as **thin vertical slices** (schemas + CLIs + tests), not full research programs. CLI flags, examples, and schema names: [`benchmarks/README.md`](benchmarks/README.md). Normative wording: [`BOUNDARIES.md`](BOUNDARIES.md) (Phase H exploration).

| Direction | What shipped | Stretch (not committed) |
|-----------|----------------|-------------------------|
| Robustness | Ensemble / sweeps / GA budgets / neighbor JSON bundles | Larger grids, richer theory, dashboard integration |
| Mechanism design | Preset defenders + inner GA (`fragility-mechanism-design-outer-v1`) | General equilibrium / continuous policy search |
| Institutional composite | Decoupled twin (**v1**) + triple (**v2**) + quad (**v3**), same schedule | Coupled “mega-institution” dynamics (out of charter today) |
| Benchmark hygiene | `run_benchmark_suite.py --validate`, `--manifest-out`, `--bench-search`; scheduled workflow | **`check_manifest_digest.py`** pins `golden_metrics_sha256`; integral bands in manifest |
| Static viewers | Replay / Pareto / attribution UIs over HTTP | Curated **preset JSON** for demos (bundled **service_backlog** replay + Pareto sample); still no server-side simulation |
| Certificates | `fragility-certificate-v1`, flagship demo | Optional **manifest digest** fields linking bundle ids to certificate inputs |
| Third-domain ops | `ServiceBacklogWorld` + `service_backlog_rollout_v1` + cookbooks | Same **narration** coverage as aggregate/network where gaps exist |
| Fork experiments | [`docs/FORK_COUPLING_RESEARCH.md`](docs/FORK_COUPLING_RESEARCH.md) policy | Named sibling packages with **schema-bumped** replay or new top-level artifacts |

---

## Promotion workflow

1. Copy the **Purpose / In scope / Out of scope / Exit criteria** of an adopted phase into `BOUNDARIES.md`.
2. Open a tracking issue per exit criterion with **one acceptance test** named up front.
3. Prefer **small PRs** that close single criteria over mega-diffs.
4. Use **[GitHub issue forms](https://github.com/theorem6/fragility-discovery-engine/issues/new/choose)** (bug report / repro bundle) so repro steps and artifacts are structured.

---

## Relationship to the north star

The one-sentence north star in `BOUNDARIES.md` stays valid. This roadmap adds what comes **after** the stablecoin + topology + economics + explanation + co-evolution spine: **reproducibility others can check**, **clearer cause-and-effect exports**, **extra reference domains**, **honest performance notes**, and **readable outputs**—each gated so claims stay **grounded in tests and JSON**, not presentation alone.

**Post–M emphasis:** the next wins are mostly **tightening**—richer manifests, stricter **artifact discipline**, optional **metric regression** on frozen bundles, and a **disciplined fourth domain** (Phase N) only if the charter opens—**not** a wider physics surface area by default.
