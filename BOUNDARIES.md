# Project boundaries (anti-weeds charter)

This document is **normative**: if an idea is not justified against these gates, default answer is **no** or **later**.

## North star (what we are building)

One sentence: **a deterministic engine that searches for shock schedules that maximize measurable fragility in a modular simulation, then explains collapse with replay + minimization + (later) counterfactuals.**

We are **not** building: a generic “digital twin platform,” a blockchain product, an LLM roleplay sandbox, or a pretty dashboard without a frozen replay artifact contract.

## Immutable principles (do not violate)

1. **Deterministic core first** — same seed ⇒ same rollout; search is reproducible.
2. **World/adversary separation** — worlds interpret physics only; “attacks” enter as explicit exogenous schedules or budgets, never as hidden hooks inside `World.step`.
3. **Evidence before chrome** — no web UI until replay JSON schema + tests are stable.
4. **Few agent knobs** — archetypes stay thin (response functions + thresholds). No personalities, memory, language, or beliefs until topology + metrics are done.
5. **One primary domain in flight** — stablecoin peg toy stays the reference until Phase B explicitly replaces it.

## Explicit non-goals (reject without guilt)

- LLM-driven agents or “GPT personas” as policy (until Phase E and only as an optional wrapper).
- Blockchain / mainnet coupling, real-time market feeds, production custody models.
- Multiplayer / MMO-style simulation, arbitrary plugin marketplaces, NL world builders.
- “Governance-grade” legal/compliance claims or calibrated forecasts of real institutions.
- Sprawling agent taxonomies (many archetypes) — **max 3–5** archetypes per domain unless a written benchmark proves need.

## Phased roadmap — hard gates

Work **does not start** on a phase until **all exit criteria** for the prior phase are true.

### Phase A — Aggregate kernel (current baseline)

**Purpose:** prove search + collapse + explain minimization on a fast toy.

**In scope:** aggregate redemption pressure, simple shocks, GA/MC, greedy minimal schedule, tests, replay dict export.

**Exit criteria:**

- [x] Replay artifact schema documented in code (`runner.rollout_to_replay_dict`) + version field.
- [x] CI-green tests on determinism + search smoke (GitHub Actions: `.github/workflows/ci.yml`).
- [x] One documented fitness scalar (even if naive) with explicit formula in docstring (`adversary.fitness.severity_score` / ``fitness_phase_a``).

**Do not start Phase B until:** exit criteria above are checked.

### Phase B — Topology contagion (“Week 2.5” suggestion)

**Status:** `fragility_engine.network` + `StablecoinNetworkWorld` + **`ContagionGraph`** façade (`contagion_graph.py`).

**Purpose:** replace “statistics-only” collapse with **propagation structure** when justified.

**In scope:**

- New package: `fragility_engine/network/` with a thin `ContagionGraph` façade (adjacency helpers exist; named façade optional).
- Start with **one** generator family per experiment (ER **or** Watts–Strogatz — CLI exposes both; default ER).
- Panic/rumor as **local neighbor rules** + optional whale-as-hub; keep rules dumb.

**Out of scope for B:**

- Multiple graph ensembles in product UI.
- Rich influencer semantics, belief heterogeneity, weighted cognition.

**Exit criteria:**

- [x] Topology toggled off ⇒ reproduces aggregate baseline within tolerance OR documented why not  
      (**single-node self-loop** equivalence test: `tests/test_network_single_node_matches_aggregate.py`; general graphs differ by design).
- [x] Tests: contagion bounded / deterministic (`tests/test_contagion_bounded.py`, graph factory seeds).
- [x] Network diffusion uses **precomputed neighbor lists** (`contagion_step_lists`) so each timestep is **O(edges)** mixing vs dense **adj @ panic** (dense adjacency storage unchanged).

**Gate:** ship Phase B only if Phase A replay/tests are frozen — otherwise topology becomes undebuggable.

### Phase C — Attack economics + richer objectives

**Purpose:** stop “maximize violence” trivial optima.

**In scope:**

- **Attack budget / cost** subtracted from fitness (document units: abstract cost, not USD claims).
- **Two-objective** frontier at most: e.g. `(collapse severity, −attack_cost)` with Pareto archive — not a seven-axis monster.

**Out of scope for C:**

- Full multi-objective UX polish.
- Calibrated dollar carbon accounting.

**Exit criteria:**

- [x] Cost model maps 1:1 to genome / schedule (auditable — see `encoding.schedule_attack_cost` + genome decode).
- [x] Demonstrate **one** “cheap stealthy collapse” schedule found by search — `scripts/find_cheap_collapse.py` (cost-penalized GA).

### Phase D — Counterfactual explainability

**Purpose:** “WITHOUT whale at t=7 ⇒ survives” class insights.

**In scope:**

- Structured counterfactual trials on **pinned seeds**: remove event, remove agent class, snap threshold ±ε.
- Output as machine-readable diff attached to replay (`explain/`).

**Out of scope for D:**

- General causal identification theory; claims of Pearl-grade ID without assumptions stated.

**Exit criteria:**

- [x] Minimum viable counterfactual API + tests on synthetic schedules (`explain/counterfactual.py`, `tests/test_counterfactual_*.py`, `scripts/export_counterfactual.py`).
- [x] Same remove-timestep counterfactual on **network** rollouts (`tests/test_counterfactual_network.py`, `export_counterfactual.py --mode network`).

### Phase E — Visualization (“Week 5” suggestion)

**Purpose:** cinematic replay, not decoration.

**Status:** static viewer consumes replay JSON including **`events_lane`** (schema **0.4**); **pointer + keyboard timeline scrubber** in `artifacts/replay_viewer/index.html`. Network replays (`simulation_mode: network`) plot **max panic** and **panic dispersion (σ)** from `state_vector[4:6]` on a shared auxiliary scale (Phase B/E bridge). Optional **A/B**: second replay file for per-step **price / instability deltas** in the meta panel (same scrub index). **Pareto:** `artifacts/pareto_viewer/index.html` plots **`pareto_front.json`** (`severity` vs `attack_cost`), including **`export_pareto_front.py`** (aggregate or **network** / list-only JSON), **`run_coevolution --export-pareto-json`**, and **`export_coevolution_pareto.py`** (merged `pareto-front-v1`).

**In scope:**

- Timeline scrubber consuming **only** replay JSON.
- Contagion-linked traces derived from frozen **`state_vector`** layout for network rollouts (no live graph geometry in v0.4 viewer).

**Exit criteria:**

- [x] Timeline + shock lane + collapse marker + scrub playhead on **`events_lane`** / trajectory contract.
- [x] **`artifact_meta`** surfaced when `meta` is present; bundled aggregate + network samples in repo.
- [x] Network mode auxiliary panic traces when `state_vector` layout matches Phase B.
- [x] Optional second-file comparison (meta-only deltas) for counterfactual / minimized pairs.

**Out of scope for E:**

- Real-time GPU graphs, D3 art projects without replay contract.

### Phase F — Fragility surfaces & phase transitions (research flavor)

**Purpose:** 2D parameter maps (e.g. reserve ratio × panic sensitivity) showing metastability.

**Gate:** run only **after** Phase C (otherwise maps optimize nonsense).

**Cap:** ≤2 parameter dimensions per figure unless publishing a methods note.

**Implementation:** `scripts/fragility_surface.py` scans `(panic0, depeg_threshold)` under **zero adversary shocks** (`numpy` helpers in `run_fragility_surface_grid`).

**Exit criteria:**

- [x] CSV artifact with axis columns **`panic0`**, **`depeg_threshold`**, outcome **`collapsed`**, **`collapse_t`**, **`peak_instability`**, **`integral_instability`** (Phase C metric alignment).
- [x] CLI axes configurable (`--panic-min/max`, `--panic-points`, `--depeg-min/max`, `--depeg-points`) with **`points ≥ 2`** validation.
- [x] Determinism tests (`tests/test_fragility_surface.py`) + subprocess smoke (`tests/test_scripts_cli_smoke.py`).

### Phase G — Defender co-evolution

**Purpose:** attacker vs defender loops on shared deterministic rollouts.

**Gate:** only after Phase C + D exist — otherwise co-evolution masks attribution bugs.

**Implementation:**

- **Aggregate:** `alternating_coevolution` → `rollout_stablecoin(..., defender_genome=…)`.
- **Network:** `alternating_coevolution_network` → `rollout_stablecoin_network(..., defender_genome=…)` using the **same** four defender knobs (`coevolution.defender.decode_defender_genome_params`).
- **Custom / heavy worlds:** `alternating_coevolution_rollout(rollout_fn)` with `rollout_fn(schedule_genome, seed, defender_genome) -> RolloutResult` — attach alternate physics or compiled steppers without forking the alternating loop.
- **CLI:** `scripts/run_coevolution.py --mode aggregate|network` (topology flags mirror `run_network_demo.py`), optional **`--neighbor-json`** / **`--neighbor-weights-json`** for list-only directed graphs, **`--collect-attacker-pareto`** / **`--export-pareto-json`** (merged `pareto-front-v1` for the static viewer), `--json-summary`, `--export-replay`; replay `meta` includes `coevolution_mode` and optional `topology`.

**Exit criteria:**

- [x] Alternating search reproducible on aggregate (`tests/test_coevolution_smoke.py`).
- [x] Network rollouts honor defender genome and diverge from undefended baseline (`tests/test_runner_network_defender.py`).
- [x] Network co-evolution smoke + extensibility hook (`tests/test_coevolution_network.py`).
- [x] CLI exports network replay + topology meta (`tests/test_scripts_cli_smoke.py`).
- [x] List-only topology JSON + optional attacker Pareto surfacing (`tests/test_neighbor_list_topology.py`, `tests/test_scripts_cli_smoke.py`, `tests/test_coevolution_network.py`).

**Scale / complexity (large systems):**

- Cost per **round** scales roughly as **O(G_att·P_att·H·step + G_def·P_def·H·step)** where **step** is one simulated timestep and **H** is attacker schedule horizon.
- **Network:** dense **`int8` adjacency** remains the default synthetic-graph path (**Θ(n²)** RAM). **List-only** **`neighbor_lists`** (+ optional positive **row weights** aligned with out-edges) avoids storing a dense matrix; diffusion stays **O(out-edges)** per step via `contagion_step_lists`. CI enables **`FRAGILITY_PERF_GATE=1`** (`.github/workflows/ci.yml`; ceiling **`FRAGILITY_PERF_GATE_MS`**, default **240000** ms). Locally, omit the env var to skip `tests/test_benchmark_perf_gate.py`.
- Reduce **`max_steps`**, GA generations/population, or **horizon** before adding defender parameters; new knobs belong in `coevolution/defender.py` with explicit tests.
- Optional **threaded batch** helper for isolated rollouts: `fragility_engine.parallel_rollouts.thread_pool_map_ordered` — ordering matches inputs; do not share mutable worlds across threads without cloning (see [`docs/phase_k_acceleration.md`](docs/phase_k_acceleration.md)).
- For institution-scale models, supply **`alternating_coevolution_rollout`** with your own deterministic `rollout_fn`; keep **seed discipline** documented at the call site.

### Phase H — Fragility certificates & benchmark harness

**Status:** `fragility_engine.benchmarks` + `scripts/run_benchmark_suite.py` + `benchmarks/README.md`; **`scripts/benchmark_rollout.py`** **`--bundle <id>`** or **`--bundle-all`** times the same frozen workloads as the suite ([`docs/phase_k_acceleration.md`](docs/phase_k_acceleration.md)).

**Purpose:** portable, regression-tested **golden bundles** so fragility claims stay reproducible across time and machines.

**In scope:**

- Deterministic bundle runners (aggregate + network dense + network neighbor-list) with pinned genome/rollout seeds.
- Golden scalar checks (`GOLDEN_METRICS`) with relaxed tolerances in CI.
- Optional CLI validation (`run_benchmark_suite.py --validate`).

**Moonshot (ensemble dispersion):** `fragility_engine.benchmarks.ensemble` + `scripts/fragility_robustness_sweep.py` — same genome and rollout seed; sweep **`graph_seed`**; emit quantiles (**not** within-rollout stochasticity).

**Exit criteria:**

- [x] Three frozen bundles + golden expectations (`fragility_engine/benchmarks/suite.py`, `tests/test_benchmark_suite.py`).
- [x] CLI + subprocess smoke (`scripts/run_benchmark_suite.py`, `tests/test_scripts_cli_smoke.py`).
- [x] README-style reproduction / citation notes (`benchmarks/README.md`).
- [x] Ensemble robustness sweep + tests (`fragility_engine/benchmarks/ensemble.py`, `tests/test_fragility_robustness_ensemble.py`, `scripts/fragility_robustness_sweep.py`).

### Phase I — Network-native explanation grammar

**Status:** `explain/counterfactual.py`, `scripts/export_counterfactual.py`, `docs/network_counterfactual_example.md`.

**Purpose:** structured network counterfactuals beyond **shock timestep removal** — same pinned genome + rollout seed, varying **reset physics** interpretable in replay meta.

**In scope (shipped slice):**

- **`network_base_panic_shift`** — baseline vs variant uniform `base_panic` at `StablecoinNetworkWorld.reset`.
- **`network_contagion_beta_shift`** — topology-preserving clones with different `contagion_beta` (`clone_stablecoin_network`).
- CLI: `--intervention remove_steps|base_panic_shift|contagion_beta_shift|edge_weight_shift` (network-only for the physics shifts; **edge_weight_shift** requires **`--neighbor-json`**).

**Shipped backlog slices (Phase I extension):**

- **Neighbor edge-weight counterfactual** — single directed out-edge weight on list topology (`counterfactual_network_edge_weight_with_rollouts`, `clone_stablecoin_network(..., neighbor_weights=…)`).
- **Merged attribution graph** — `merge_heterogeneous_counterfactuals` + schema **`attribution-merge-v1`**; CLI `scripts/merge_counterfactual_attribution.py`.
- **ε-sweep** axis **`edge_weight`** (`sweep_network_edge_weight`, `counterfactual_epsilon_sweep.py`) when **`--neighbor-json`** + **`--edge-from` / `--edge-to`** are set.

**Ordered chains (shipped):** cumulative mutations on a template clone — `counterfactual_network_mutation_chain_with_rollouts`, chain spec **`network-mutation-chain-spec-v1`**, CLI **`scripts/export_counterfactual_chain.py`** (`contagion_beta` and `edge_weight` steps).

**Path trace (shipped):** `--emit-path-trace` on `export_counterfactual_chain.py` emits **`explanation-mutation-chain-path-v1`** (`mutation_chain_path_rollouts`, `mutation_chain_path_to_trace`).

**Multi-edge weights (shipped):** `counterfactual_network_neighbor_edges_weight_patch_with_rollouts`, `--intervention edge_weights_shift` + **`--edges-patch-json`**; chain step **`edge_weights_patch`**.

**Additive interaction summary (shipped):** `summarize_attribution_merge` → **`attribution-interaction-summary-v1`** (`explain/interaction_summary.py`, `scripts/summarize_attribution_merge.py`) — sum of branch deltas with explicit non-identification disclaimer.

**Static viewer (shipped):** `artifacts/attribution_viewer/index.html` for **`attribution-merge-v1`** and mutation-chain path traces.

**Backlog (not gates yet):** formal Shapley-style decompositions; richer **aggregate/network** multi-step knob bundles beyond the shipped scalar shifts / merges (Phase J **resource-cascade** cumulative chains are shipped: `resource-cascade-mutation-chain-spec-v1`, `export_resource_cascade_counterfactual_chain.py`, path trace schema `explanation-mutation-chain-path-resource-cascade-v1`).

**Earlier shipped backlog slices:**

- ε-sweeps — `explain/sweep.py`, `counterfactual_epsilon_sweep.py` (**network** `base_panic` / `contagion_beta`, **aggregate** `initial_panic`, **resource_cascade** `initial_overload`).
- Linear trace — `explain/trace.py` (`explanation-trace-v1`, `--emit-trace` on epsilon sweep CLI).

**Exit criteria:**

- [x] ≥2 network-only intervention families beyond timestep deletion (`counterfactual_network_*_with_rollouts`, `tests/test_counterfactual_network_interventions.py`).
- [x] CLI semantics documented in `--help` and this section; subprocess smoke (`tests/test_scripts_cli_smoke.py`).
- [x] Worked example with commands (`docs/network_counterfactual_example.md`).
- [x] Deterministic ε-sweeps (**network** `base_panic` / `contagion_beta`, **aggregate** `initial_panic`, **resource_cascade** `initial_overload`) + optional linear trace (`explain/trace.py`, `tests/test_explain_trace.py`, `tests/test_scripts_cli_smoke.py`).

### Phase J — Second reference domain (scaffold shipped)

**Status:** `world/resource_cascade.py` — **`ResourceCascadeWorld`** + **`runner.rollout_resource_cascade`** (schedule encoding matches aggregate/network; physics is capacity + overload cascade, not a peg). GA smoke CLI: **`scripts/run_resource_cascade_ga_demo.py`**. Co-evolution + Pareto: **`alternating_coevolution_resource_cascade`**, **`scripts/run_coevolution.py --mode resource_cascade`**, **`scripts/export_pareto_front.py --mode resource_cascade`** (defender genome uses the same four-knob decoding as aggregate/network; **`reserve_boost`** damps effective initial overload at reset). Counterfactuals: **`export_counterfactual.py --mode resource_cascade`** (`remove_steps`, **`initial_overload_shift`**, **`cascade_coupling_shift`**); joint star-merge **`scripts/export_resource_cascade_joint_attribution.py`** (`--second-branch` overload vs coupling); cumulative mutation chains **`scripts/export_resource_cascade_counterfactual_chain.py`** + `explain/counterfactual_chain_resource_cascade.py`; optional Numba rollout behind **`FRAGILITY_RESOURCE_CASCADE_BACKEND`** (`numpy` \| `numba` \| `auto`), optional extra **`[accelerate]`** — see [`docs/phase_k_acceleration.md`](docs/phase_k_acceleration.md). Cookbook [`docs/resource_cascade_counterfactual_example.md`](docs/resource_cascade_counterfactual_example.md).

**Purpose:** architecture transfer demo without relaxing stablecoin CI oracles.

**Normative exit criteria** remain in [`ROADMAP_NEXT.md`](ROADMAP_NEXT.md). Replay compatibility: [`docs/phase_j_resource_cascade.md`](docs/phase_j_resource_cascade.md). Motivation ≤ 1 page: [`docs/WHY_RESOURCE_CASCADE.md`](docs/WHY_RESOURCE_CASCADE.md). Phase **H** bundle: **`resource_cascade_rollout_v1`** (`benchmarks/suite.py`).

### Phase L — Narration & publication (wrapper)

**Status:** adopted — [`docs/phase_l_publication.md`](docs/phase_l_publication.md).

**Purpose:** Make frozen JSON **legible** (deterministic summaries, citations, publication figures) without letting narration or LLM prose **drive** physics or search.

**In scope:**

- Deterministic narration library + CLI (`fragility_engine.explain.narration`, `scripts/narrate_frozen_json.py`, `--cite-digest` / `narration-summary-v1`).
- Versioned **LLM prompt packs** (`artifacts/llm_prompts/narration_v1`, **`reviewer_memo_v1`**, **`paper_appendix_v1`**; `scripts/export_llm_narration_prompt.py --prompt-pack …`, schema **`llm-prompt-bundle-v1`**); optional OpenAI invoke is **stdout-only documentation**, never fed back into worlds.
- Matplotlib figure hooks: replay timelines, ε-sweeps, Pareto archives, fragility-surface CSV heatmaps, **counterfactual baseline/variant bars** (`scripts/plot_*.py`, pinned styles under `artifacts/plot_styles/`).

**Out of scope:**

- LLM (or any external model) as **agent policy** inside `world/` rollouts.

**Exit criteria:**

- [x] Citations / hashes on summaries (`--cite-digest`, `frozen_json_digest.py`).
- [x] Reproducible CLI figures from frozen JSON/CSV with pinned style configs.
- [x] Optional LLM path restricted to prompt export + explicit disclaimer; templates versioned on disk.

## Fitness function discipline

Current scalar fitness is **acceptable for Phase A**.

Escalation order:

1. Add **attack cost penalty** (Phase C).
2. Then **Pareto pair** (severity vs cost), not a laundry list.
3. Multi-objective laundry lists (**fast / cheap / stealth / delayed / max contagion / volatility / governance paralysis**) are **NOT** adopted wholesale — pick **two** dimensions per experiment and archive the rest as future ideas.

## Metrics discipline

Measure collapse **and eventually recoverability** — but:

- **Recoverability** enters only when Phase B/C basics exist; define operational metrics in code, not prose.
- **Shipped (replay JSON):** `integral_instability` (sum), `mean_instability` (per-step average), `recovery_timestep` / `recovery_latency_steps` when ``continue_after_collapse=True`` yields re-peg (see `runner._replay_recoverability_fields`).

## How we use external advice (including other AIs)

Allowed pattern:

1. File issue under “idea backlog” with **phase tag**.
2. Require **one acceptance test** idea before coding.
3. If it skips phases, **reject**.

Forbidden pattern:

- “Quickly add NetworkX + six graph models + new fitness axes + UI” in one sprint.

## Definition of done for any PR touching simulation

- Updates tests or adds a **conscious** `pytest.skip` with reason (temporary only).
- Documents any new genome dimension or fitness term in `BOUNDARIES.md` **or** module docstring linked from README.
- Keeps **determinism** unless explicitly labeled stochastic experiment behind a flag.

## Project motto

**Engine first, topology second, economics third, cinema last, co-evolution last-er.**
