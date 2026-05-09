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

### Phase H — Fragility certificates & benchmark harness

**Purpose:** Turn ad hoc scripts into a **portable, auditable benchmark layer**: comparable runs across machines and time.

**In scope:**

- **Benchmark bundles**: versioned directories or single manifest JSON listing topology source, neighbor JSON hashes, GA budgets, seeds, CLI invocation fingerprints.
- **Regression targets**: metric ceilings/floors on **integral instability**, collapse rate under fixed budgets, Pareto hypervolume proxies (simple, documented)—not only wall-clock (`FRAGILITY_PERF_GATE` stays auxiliary).
- **`pytest` + subprocess** coverage for “golden” bundles (small graphs, short horizons) checked into `artifacts/benchmarks/` or `tests/fixtures/benchmarks/` (small files only).

**Out of scope:**

- Claiming industry certification or regulatory compliance.

**Exit criteria (candidate):**

- [ ] At least **three** frozen benchmark bundles runnable via one documented command (Make/ps1/target).
- [ ] CI job (or scheduled workflow) runs bundles with **tight numeric tolerances** on summary stats.
- [ ] README section: “How to cite / reproduce run XYZ.”

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

- [ ] `explain/` APIs + tests cover **≥2** network-only intervention families beyond timestep deletion.
- [ ] CLI (`export_counterfactual` or successor) documents semantics in `--help` and in `BOUNDARIES.md`.
- [ ] One **worked example** in docs with paired replay files.

---

### Phase J — Second reference domain (single flight)

**Purpose:** Demonstrate that the **architecture** is the product—not only the stablecoin toy.

**Candidates (pick one when gate opens):**

- Contagion + resource allocation on a **different** liability structure (not crypto-themed).
- Infrastructure-style **cascade** with overload + recovery (still discrete-time, still thin agents).

**Hard rules:**

- Exactly **one** new domain in flight; **max 3–5** archetypes (`BOUNDARIES.md`).
- Stablecoin kernel remains **CI oracle**: no release regresses aggregate/network parity tests already shipped.

**Exit criteria (candidate):**

- [ ] New `world/` module + replay schema compatibility table (what transfers unchanged).
- [ ] GA + (optional) co-evolution smoke + **determinism tests**.
- [ ] README “Why this domain” ≤ 1 page; link to limits / non-goals.

---

### Phase K — Honest performance & optional accelerated backends

**Purpose:** Grow **n** and budgets without lying about complexity.

**In scope:**

- **World protocol / ABC** (if not already explicit): swap NumPy stepper for **optional** accelerated backend **without** changing search semantics (golden tests against NumPy).
- **Batch evaluation**: independent seeds rolled out in parallel **only** where bitwise reproducibility is preserved per seed (document ordering discipline).

**Out of scope:**

- “Real-time market simulation” or implicit coupling to external feeds (`BOUNDARIES.md`).

**Exit criteria (candidate):**

- [ ] Documented speedups on **named** benchmark bundles (Phase H).
- [ ] Fallback path always available (acceleration optional dependency).

---

### Phase L — Narration & publication layer (wrapper only)

**Purpose:** Make artifacts **legible to humans and reviewers** without letting narration drive physics.

**In scope:**

- **LLM optional summarizer** over **frozen** JSON (replay + counterfactual diff + Pareto)—prompt templates versioned; output never fed back into simulation.
- **Figure hooks**: scriptable plots from CSV/JSON (e.g. fragility surfaces, Pareto fronts, collapse timelines) suitable for papers.

**Out of scope:**

- LLM as agent policy inside worlds (see `BOUNDARIES.md`).

**Exit criteria (candidate):**

- [ ] Summaries carry **citations** to artifact paths / hashes.
- [ ] Visual outputs reproducible from CLI with pinned style configs.

---

## Moonshots (explicitly post–Phase L or fork)

These are **not** commitments—ideas worth protecting from premature implementation:

- **Fragility robustness**: distributions over topologies; report **quantiles** of collapse metrics under fixed search budgets (careful with stochasticity vs ensemble-of-deterministic-seeds).
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
