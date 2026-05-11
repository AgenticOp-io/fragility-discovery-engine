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

1. [x] **§Selected candidate** below is filled in (one narrative + public API names planned).
2. [x] **No other** open domain flight (no parallel second “Phase J–style” rewrite; no duplicate Phase M candidates in flight).
3. [x] **Issues filed** — one tracker issue per exit criterion in `BOUNDARIES.md` Phase M, each naming **one** acceptance test. Copy-paste bodies: [`PHASE_M_TRACKING_ISSUES.md`](PHASE_M_TRACKING_ISSUES.md).
4. [x] **Replay table drafted** — §5 below completed for the candidate (even if implementation lags by one PR).

**Historical:** this checklist gated the **first** Phase M merge. With all items checked, further work follows normal `BOUNDARIES.md` simulation rules (not “design-only only”).

---

## 4. Selected candidate — `ServiceBacklogWorld` *(shipped)*

**World module:** `fragility_engine.world.service_backlog.ServiceBacklogWorld`

**`simulation_mode` string:** `service_backlog`

**One-sentence physics story:** discrete-time **work backlog** `B` and **service slack** `S` (capacity headroom in `[0,1]`); `reserve_loss` shocks add load, `rumor` shocks erode slack; the same archetyped redeemers modulate drain rate before slack recovers.

**Why not cascade / peg / network:** third scalar **operations / latency** narrative without peg mechanics or graph contagion — still schedule-driven shocks and replay-shaped metrics for apples-to-oranges comparison in tooling.

**Shipped in v1:** `rollout_service_backlog`, `rollout_to_replay_dict`, defender decoding (`build_defended_service_backlog_world`), co-evolution (`alternating_coevolution_service_backlog`), Pareto + MC + export CLIs, counterfactuals (`remove_steps`, `initial_backlog_shift`, `process_rate_shift`), ε-sweeps (`initial_backlog`, `process_rate`), Phase **H** bundle `service_backlog_rollout_v1`, GA demo `scripts/run_service_backlog_ga_demo.py`.

**Also shipped (J-style parity):** cumulative mutation chains (`service-backlog-mutation-chain-spec-v1`, `scripts/export_service_backlog_counterfactual_chain.py`), path trace `explanation-mutation-chain-path-service-backlog-v1`, joint star-merge (`scripts/export_service_backlog_joint_attribution.py`), and cookbook [`service_backlog_counterfactual_example.md`](service_backlog_counterfactual_example.md).

---

## 5. Replay JSON contract (template — copy and fill)

Assume `schema_version` **0.4.x** unless you justify a bump in `BOUNDARIES.md`.

| Topic | Aggregate / network / cascade (reference) | Phase M (`service_backlog`) |
|--------|---------------------------------------------|------------------------|
| `simulation_mode` | `aggregate` \| `network` \| `resource_cascade` | **`service_backlog`** |
| `state_vector` length + semantics | see Phase J table | **4 floats:** `B`, `S`, `B / backlog_collapse` clipped to `[0,1]`, timestep index |
| `metrics.price` semantics | peg / headroom / … | **Slack headroom** `S` (same field name for viewer compatibility) |
| `metrics.instability` | domain formulas | `0.55 * norm(B) + 0.45 * (1 - S)` with bounded backlog norm |
| `events_lane` | shocks | Same `reserve_loss` / `rumor` encoding as other domains |
| Viewer | `artifacts/replay_viewer/index.html` behavior | Treat **`price` as slack** (healthy when high); collapse when `B >= backlog_collapse` or `S <= slack_floor_collapse` |

---

## 6. Exit criteria (mirror `BOUNDARIES.md` Phase M)

Track these in issues; checkboxes flip only when merged to `main`:

- [x] World + rollout + replay path + determinism tests.
- [x] Replay contract tests (new or extended).
- [x] GA (or equivalent) smoke entry point documented.
- [x] Phase **H** bundle + `GOLDEN_METRICS` + CI tolerance row.
- [x] Co-evolution / counterfactual / Pareto / MC / ε-sweeps — shipped as listed in §4.

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

- [x] **`BOUNDARIES.md`** Phase M **Status** set to *shipped* (module + bundle id + script pointers).
- [x] **`docs/WHY_SERVICE_BACKLOG.md`** — scope disclaimer for newcomers.
- Optionally extend **institutional composite** tooling later (decoupled audit only) — not required for Phase M closure.
