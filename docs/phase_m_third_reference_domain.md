# Phase M — Third reference domain (admission gate + contract)

**Normative summary:** [`BOUNDARIES.md`](../BOUNDARIES.md) (Phase M). **Aspirational roadmap:** [`ROADMAP_NEXT.md`](../ROADMAP_NEXT.md). **Coupling / fork policy:** [`RESEARCH_FRONTIERS.md`](RESEARCH_FRONTIERS.md).

Phase **J** shipped the **second** reference domain (`ResourceCascadeWorld`). Phase **M** is the **chartered slot** for a **third** reference domain: one new `World` class, same adversary schedule encoding, new physics — **not** a coupled mega-model.

---

## 1. Purpose

- Prove the **engine** (encoding → rollout → replay → benchmarks) supports **another** thin physics story.
- Keep **aggregate**, **network**, and **cascade** bundles as **numeric regression anchors** unless the project explicitly changes that policy.
- Ship only what can be **frozen**: determinism, schema docs, golden bundle, tests.

---

## 2. Hard rules (non-negotiable)

| Rule | Detail |
|------|--------|
| **One flight** | At most **one** Phase M world under active development at a time. |
| **Archetypes** | **Max 3–5** behavioral archetypes in the new world unless a benchmark issue proves otherwise (`BOUNDARIES.md`). |
| **Encoding** | Reuse **`decode_schedule` / `schedule_attack_cost`**; no forked genome shape for Phase M unless paired with a versioned encoding bump + migration plan. |
| **Coupling** | No cross-`World` liquidity or shared mutable graph inside a single `step()` (see **Out of scope**). |
| **Replay** | Must export through **`rollout_to_replay_dict`** (or a documented schema bump with migration notes and viewer guidance). |

---

## 3. Admission checklist (before the first Phase M implementation PR)

All must be true:

1. [ ] **§Selected candidate** below is filled in (one narrative + public API names planned).
2. [ ] **No other** open domain flight (no parallel second “Phase J–style” rewrite; no duplicate Phase M candidates in flight).
3. [ ] **Issues filed** — one tracker issue per exit criterion in `BOUNDARIES.md` Phase M, each naming **one** acceptance test.
4. [ ] **Replay table drafted** — §5 below completed for the candidate (even if implementation lags by one PR).

Until admission is satisfied, Phase M work stays **design-only** (docs, spikes on branches) or lives in a **fork**.

---

## 4. Selected candidate *(fill when opening the flight)*

**World module (planned):** `fragility_engine.world.________________`

**`simulation_mode` string (planned):** `________________`

**One-sentence physics story:**


**Why not cascade / peg / network:**


**Deferred to later issues (optional):** co-evolution mode, Pareto, counterfactuals, mutation chains — list explicitly if not in v1 flight.

---

## 5. Replay JSON contract (template — copy and fill)

Assume `schema_version` **0.4.x** unless you justify a bump in `BOUNDARIES.md`.

| Topic | Aggregate / network / cascade (reference) | Phase M world (fill) |
|--------|---------------------------------------------|------------------------|
| `simulation_mode` | `aggregate` \| `network` \| `resource_cascade` | |
| `state_vector` length + semantics | see Phase J table | |
| `metrics.price` semantics | peg / headroom / … | |
| `metrics.instability` | | |
| `events_lane` | shocks | |
| Viewer | `artifacts/replay_viewer/index.html` behavior | |

---

## 6. Exit criteria (mirror `BOUNDARIES.md` Phase M)

Track these in issues; checkboxes flip only when merged to `main`:

- [ ] World + rollout + replay path + determinism tests.
- [ ] Replay contract tests (new or extended).
- [ ] GA (or equivalent) smoke entry point documented.
- [ ] Phase **H** bundle + `GOLDEN_METRICS` + CI tolerance row.
- [ ] Optional co-evolution / counterfactual / Pareto — only if listed in §4 **Deferred** as in-scope for this flight.

---

## 7. Out of scope (Phase M charter)

- **Coupled institutional dynamics** (single `World` merging peg + graph + cascade state) — fork material (`RESEARCH_FRONTIERS.md`).
- Regulatory / market calibration claims.
- LLM agents inside `world/` rollouts.

---

## 8. Candidate ideas (not commitments)

Pick **one** when opening §4; the others remain backlog references:

- Non–crypto-themed **liability / inventory** dynamics with explicit shocks into a balance-sheet-like state.
- **Operations** queueing + failure propagation (discrete-time, thin agents) — still deterministic, still schedule-driven.
- **Liquidity latency** toy (order-book–free): shocks to settlement delay or pipe capacity — only if the replay contract stays interpretable.

---

## 9. After shipping

- Update **`BOUNDARIES.md`** Phase M **Status** from *proposed* to *shipped* (short pointer to module + bundle id).
- Add **`docs/WHY_<DOMAIN>.md`** (or expand this doc) so newcomers know what the world does **not** claim.
- Optionally extend **institutional composite** tooling later (decoupled audit only) — not required for Phase M closure.
