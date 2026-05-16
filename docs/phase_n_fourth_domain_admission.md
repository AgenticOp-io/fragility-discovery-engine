# Phase N — fourth reference domain (admission memo, draft)

**Status:** **Not adopted.** There is no Phase N section in [`BOUNDARIES.md`](../BOUNDARIES.md). Do not add a fourth `world/` physics line until this memo is promoted and exit criteria are checked in the charter.

## Purpose

Reserve a named slot for a **fourth** thin `World` on the same shock-schedule encoding, with a new physics story and a new frozen `*_rollout_v1` bundle—without silently expanding Phase M or coupling kernels in one `step()`.

## Candidate directions (pick one if Phase N opens)

| Candidate | Rationale | Risk |
|-----------|-----------|------|
| **Liquidity ladder / margin** | Different liability story than peg or backlog; still scalar-friendly | Scope creep into “banking realism” |
| **Supply-chain choke** | Discrete delays + inventory (J/M-like) | Harder to keep ≤5 archetypes |
| **Regulatory halt / circuit breaker** | Event-driven freezes on schedules | Easy to overfit narrative |

**Recommendation:** choose the candidate that adds the **smallest** new state vector while still failing the “this is just aggregate with renamed labels” test.

**Draft preference (not adopted):** **Liquidity ladder / margin** — scalar-friendly, distinct from peg/backlog/cascade narratives; keep scope to ≤5 archetypes and one frozen bundle if Phase N opens.

## Non-goals (unchanged charter)

- No cross-`World` coupling inside `step()`.
- No LLM agents inside physics.
- No claims of regulatory compliance or calibrated forecasts.
- Coupled “mega-institution” dynamics remain fork policy: [`FORK_COUPLING_RESEARCH.md`](FORK_COUPLING_RESEARCH.md).

## Exit criteria (must copy into `BOUNDARIES.md` before coding)

- [ ] This admission memo linked from `BOUNDARIES.md` with selected candidate.
- [ ] `world/` + `runner` + `rollout_to_replay_dict` compatibility row.
- [ ] Determinism + replay contract tests + GA smoke CLI.
- [ ] New frozen bundle id + `GOLDEN_METRICS` + `tests/test_benchmark_suite.py`.
- [ ] “Why this domain” doc (≤ one page) + counterfactual / ε-sweep / co-evolution parity **or** documented scope-down.

## Relationship to shipped domains

Existing oracles stay frozen unless a charter revision explicitly replaces one:

- `aggregate_rollout_v1`
- `network_er_rollout_v1`, `network_neighbor_list_rollout_v1`
- `resource_cascade_rollout_v1` (Phase J)
- `service_backlog_rollout_v1` (Phase M)
