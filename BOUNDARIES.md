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
- Start with **one** generator family (pick **either** ER **or** small-world — not both at first).
- Panic/rumor as **local neighbor rules** + optional whale-as-hub; keep rules dumb.

**Out of scope for B:**

- Multiple graph ensembles in product UI.
- Rich influencer semantics, belief heterogeneity, weighted cognition.

**Exit criteria:**

- [x] Topology toggled off ⇒ reproduces aggregate baseline within tolerance OR documented why not  
      (**single-node self-loop** equivalence test: `tests/test_network_single_node_matches_aggregate.py`; general graphs differ by design).
- [x] Tests: contagion bounded / deterministic (`tests/test_contagion_bounded.py`, graph factory seeds).

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

### Phase E — Visualization (“Week 5” suggestion)

**Purpose:** cinematic replay, not decoration.

**Status:** static viewer consumes replay JSON including **`events_lane`** (schema **0.4**); **pointer + keyboard timeline scrubber** in `artifacts/replay_viewer/index.html`. Network replays (`simulation_mode: network`) plot **max panic** and **panic dispersion (σ)** from `state_vector[4:6]` on a shared auxiliary scale (Phase B/E bridge).

**In scope:**

- Timeline scrubber consuming **only** replay JSON.
- Contagion-linked traces derived from frozen **`state_vector`** layout for network rollouts (no live graph geometry in v0.4 viewer).

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

**Purpose:** attacker vs defender loops.

**Gate:** only after Phase C + D exist — otherwise co-evolution masks attribution bugs.

**Implementation notes:** `alternating_coevolution` carries `last_rollout` (final probe). `scripts/run_coevolution.py --export-replay` emits replay JSON for the static viewer without changing the core schema.

## Fitness function discipline

Current scalar fitness is **acceptable for Phase A**.

Escalation order:

1. Add **attack cost penalty** (Phase C).
2. Then **Pareto pair** (severity vs cost), not a laundry list.
3. Multi-objective laundry lists (**fast / cheap / stealth / delayed / max contagion / volatility / governance paralysis**) are **NOT** adopted wholesale — pick **two** dimensions per experiment and archive the rest as future ideas.

## Metrics discipline

Measure collapse **and eventually recoverability** — but:

- **Recoverability** enters only when Phase B/C basics exist; define operational metrics (time-to-re-peg, area under instability curve) in code, not prose.

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
