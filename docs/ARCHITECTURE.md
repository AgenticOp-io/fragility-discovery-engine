# Architecture

This document describes how the Fragility Discovery Engine is structured: what runs where, how data flows from a genome to JSON artifacts, and how the reference domains relate. For CLI flags and schema names, see [`REFERENCE.md`](REFERENCE.md). For scope and non-goals, see [`BOUNDARIES.md`](../BOUNDARIES.md).

---

## Design goal

The engine answers one question in a **controlled, repeatable** way:

> Given a fixed world model and a search budget, which **shock schedules** (sequences of exogenous events) drive **high instability** or **collapse**, and what **minimal changes** explain the difference between two runs?

Everything else—Pareto archives, certificates, narration, static HTML viewers—is built on top of that core loop.

---

## Layered layout

```
  scripts/*.py          CLI entry points (subprocess-friendly, pinned seeds)
        │
        ▼
  fragility_engine.adversary     MC / GA search over genomes → schedules
        │
        ▼
  fragility_engine.runner        decode genome, apply events, collect RolloutResult
        │
        ▼
  fragility_engine.world.*       physics only (reset, step, metrics)
        │
        ▼
  fragility_engine.agents        thin observe → decide → act (shared population helpers)
```

**Separation rules** (enforced by convention and review):

| Layer | May contain | Must not contain |
|-------|-------------|------------------|
| `world/` | State, transitions, collapse rules | GA, Pareto, “attacker” concepts |
| `adversary/` | Encoding, fitness, search | Domain-specific peg/backlog physics |
| `explain/` | Counterfactuals, sweeps, narration | Hidden changes to world physics |
| `network/` | Graph topology, contagion step | Search loops |

---

## Rollout pipeline (one evaluation)

1. **Genome** — `numpy` array shape `(horizon, 2)` in `[0, 1]`; each row encodes shock intensity for that timestep (see `adversary.encoding`).
2. **Schedule** — deterministic decode from genome (same genome ⇒ same event list).
3. **World** — `reset(...)` sets initial scalars (panic, overload, backlog, margin, … depending on mode).
4. **Steps** — for each timestep: agents act, world `step`, metrics recorded until `max_steps` or collapse (unless `continue_after_collapse`).
5. **RolloutResult** — aggregates `integral_instability`, `attack_cost`, `collapsed`, trajectory, etc.
6. **Replay JSON** (optional) — `runner.rollout_to_replay_dict` adds `schema_version`, `trajectory`, `events_lane`, `simulation_mode`, `meta`.

Search (MC or GA) calls the same rollout function thousands of times with different genomes and rollout seeds. **Fitness** is derived from `RolloutResult` scalars (instability, cost, collapse).

---

## Simulation modes

All modes share the **same schedule encoding**. Physics differs.

| `simulation_mode` | World class | Primary reset knobs | Typical use |
|-------------------|-------------|---------------------|-------------|
| `aggregate` | `StablecoinPegWorld` | `initial_panic` | Scalar peg / panic toy |
| `network` | `StablecoinNetworkWorld` | `base_panic`, graph topology | Contagion on ER/WS or neighbor JSON |
| `resource_cascade` | `ResourceCascadeWorld` | `initial_overload` | Capacity / overload cascade |
| `service_backlog` | `ServiceBacklogWorld` | `initial_backlog`, `process_rate` | Ops / latency backlog |
| `liquidity_ladder` | `LiquidityLadderWorld` | `initial_margin`, delever/haircut params | Margin utilization vs ladder depth |

Co-evolution and Pareto CLIs take `--mode` and route to the matching rollout + defender decoding.

---

## Search and multi-objective output

| Mechanism | Module | Output |
|-----------|--------|--------|
| Monte Carlo | `adversary.search.monte_carlo_search` | Best sample + optional replay |
| Genetic algorithm | `adversary.search.genetic_search` | Best individual; optional `collect_pareto` archive |
| Co-evolution | `coevolution.alternating_*` | Rounds of attacker/defender GA; optional Pareto per round |

**Pareto** uses two minimized objectives (typically **severity** / instability vs **attack_cost**). Hypervolume helpers live in `benchmarks.hypervolume` for regression checks, not as a third fitness axis in search.

Parallel evaluation (`eval_workers > 1`) clones worlds per task when needed (`coevolution.thread_safe_template`).

---

## Explanation layer

Explanation code **never** feeds back into `World.step`. It compares rollouts under explicit interventions:

| Mechanism | Typical question |
|-----------|------------------|
| `remove_steps` | What if shocks at timesteps *t* were zeroed? |
| Scalar shift | What if reset panic / overload / margin / β changed? |
| Mutation chain | What if physics knobs changed in sequence? |
| ε-sweep | How does one scalar axis move instability? |
| Merge | Star-merge multiple single-branch counterfactuals |

Exports are JSON with stable schema ids (`attribution-merge-v1`, path-trace variants per domain, `explanation-dag-v1`, etc.).

**Institutional composite** runs the **same** schedule on multiple kernels and writes branch metrics JSON (`fragility-institutional-composite-v1` … `v3`). Kernels are **not** coupled inside one `step()`.

---

## Benchmarks and CI

| Piece | Role |
|-------|------|
| `benchmarks.suite` | Six frozen bundles (`*_rollout_v1`), pinned genome + rollout seeds, golden metrics |
| `benchmarks.manifest` | Portable inventory: bundle list, digests, schema index |
| `scripts/run_benchmark_suite.py --validate` | Runs all bundles and checks golden values + integral bands |
| `scripts/check_*` | Pins manifest digest, bundled paths, flagship artifacts |

CI also runs full `pytest`, ruff, viewer preset validation, and optional Numba parity on resource cascade.

---

## Determinism

- **Reference path:** NumPy RNG with explicit seeds on genome construction and rollout.
- **Same inputs** (code version, seeds, CLI flags, world template params) ⇒ **same** metrics and trajectory within documented float tolerances on golden bundles.
- **Parallelism** is safe only with per-task world clones or isolated bundle evaluators; see [`SCALE_AND_LIMITS.md`](SCALE_AND_LIMITS.md).
- **Optional Numba** backend for resource cascade must pass parity tests against NumPy before claims about speedup.

---

## Extension points

| Goal | Approach |
|------|----------|
| New reference domain | New `world/` module + `rollout_*` + replay contract tests + frozen bundle (charter in `BOUNDARIES.md`) |
| Custom co-evolution | `alternating_coevolution_rollout(rollout_fn, ...)` with deterministic `rollout_fn` |
| Custom topology | `ContagionGraph` / `--neighbor-json` list format |
| Faster cascade | `pip install -e ".[accelerate]"`, env `FRAGILITY_RESOURCE_CASCADE_BACKEND` |

Coupled multi-kernel physics inside one world belongs in a **fork** per [`FORK_COUPLING_RESEARCH.md`](FORK_COUPLING_RESEARCH.md), not in this repo’s default charter.
