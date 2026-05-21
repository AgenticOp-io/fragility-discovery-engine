# Architecture

This document describes how the Fragility Discovery Engine is structured: what runs where, how data flows from a stress schedule to output files, and how the simulation domains relate. For CLI flags and output file formats, see [Reference](/docs/reference.html). For scope and non-goals, see [BOUNDARIES.md](../BOUNDARIES.md).

---

## Design goal

The engine answers one question in a **controlled, repeatable** way:

> Given a fixed simulation world and a search budget, which **stress schedules** (sequences of external events) drive **high instability** or **collapse**, and what **minimal changes** explain the difference between two runs?

Everything else — trade-off charts, certificates, narration, static HTML viewers — is built on top of that core loop.

---

## Code layers

```
  scripts/*.py             Command-line entry points (one script per task, pinned seeds)
        │
        ▼
  fragility_engine.adversary     Monte Carlo / genetic search over stress schedules
        │
        ▼
  fragility_engine.runner        Decode a schedule, apply events, collect the result
        │
        ▼
  fragility_engine.world.*       Physics: reset, step forward, report metrics
        │
        ▼
  fragility_engine.agents        Shared agent population helpers (observe, decide, act)
```

Each layer has a strict boundary:

| Layer | Contains | Does not contain |
|-------|----------|-----------------|
| `world/` | State, transitions, collapse rules | Search algorithms, attacker logic |
| `adversary/` | Schedule encoding, fitness, search | Domain-specific physics |
| `explain/` | Counterfactuals, sweeps, narration | Changes to world physics |
| `network/` | Graph topology, contagion update | Search loops |

---

## How a single run works

1. **Schedule encoding** — a NumPy array of shape `(horizon, 2)`, values in `[0, 1]`. Each row encodes the type and intensity of the stress event for that timestep.
2. **Decode** — the schedule is decoded deterministically: the same input always produces the same event sequence.
3. **World reset** — the simulation starts from a fixed initial state (panic level, overload, backlog, margin, stock level, etc. depending on the domain).
4. **Steps** — at each timestep: agents act, the world advances one step, metrics are recorded. Continues until the step limit or collapse.
5. **Result** — collects total accumulated stress, peak stress, whether the system collapsed, and the full step-by-step trajectory.
6. **Replay file** (optional) — packages the result as a JSON file you can load in the browser viewer.

Search (Monte Carlo or genetic algorithm) calls this same run function thousands of times with different schedules and random seeds. The best-scoring results are saved.

---

## Simulation modes

All modes share the **same stress encoding**. The physics of each world is different.

| `--mode` | World class | Key starting parameters | What it models |
|----------|-------------|------------------------|----------------|
| `aggregate` | `StablecoinPegWorld` | `initial_panic` | Stablecoin reserve under redemption pressure and panic |
| `network` | `StablecoinNetworkWorld` | `base_panic`, graph topology | Panic spreading across a graph of connected nodes |
| `resource_cascade` | `ResourceCascadeWorld` | `initial_overload` | Overload cascading through two coupled capacity layers |
| `service_backlog` | `ServiceBacklogWorld` | `initial_backlog`, `process_rate` | Operations queue where demand fights processing rate |
| `liquidity_ladder` | `LiquidityLadderWorld` | `initial_margin`, delever/haircut params | Financial margin eroding toward a forced sell-off |
| `inventory_buffer` | `InventoryBufferWorld` | `initial_stock` | Stock level under demand spikes and fulfillment problems |

All co-evolution and search scripts accept `--mode` and route to the appropriate simulation and defender logic.

---

## Search and the trade-off chart

| Method | Module | Output |
|--------|--------|--------|
| Monte Carlo | `adversary.search.monte_carlo_search` | Best sample, optional replay |
| Genetic algorithm | `adversary.search.genetic_search` | Best schedule; optional Pareto archive |
| Attacker/defender co-evolution | `coevolution.alternating_*` | Rounds of alternating GA; optional Pareto per round |

The trade-off chart (Pareto front) shows two objectives: **severity** (instability) vs **attack cost**. These are projected from the search history after the run — the search itself optimizes for a single fitness score.

Parallel evaluation clones the simulation world per worker thread so each evaluation is independent.

---

## Explanation layer

Explanation code **never** modifies how the simulation steps. It re-runs the simulation with controlled changes and compares the results:

| Technique | Question it answers |
|-----------|---------------------|
| Remove steps | What if certain stress events had not happened? |
| Scalar shift | What if the starting conditions had been different? |
| Mutation chain | What if the world's physical parameters changed one at a time? |
| Parameter sweep | How does instability change as one parameter moves across a range? |
| Attribution merge | Which of several interventions made the most difference? |

Outputs are JSON files with stable format identifiers (`attribution-merge-v1`, `explanation-dag-v1`, etc.) so they can be versioned and cited.

**Multi-domain comparison** runs the same stress schedule through several simulation worlds independently and produces a side-by-side summary. The worlds never share state — it is a comparison, not a coupled simulation.

---

## Automated tests and frozen benchmarks

| Component | What it does |
|-----------|--------------|
| `benchmarks.suite` | Six reference runs with pinned seeds and known-good metrics. Every CI run checks these. |
| `benchmarks.manifest` | A portable inventory of all bundles and their checksums. |
| `run_benchmark_suite.py --validate` | Runs all reference bundles and confirms the results match expectations. |
| `scripts/check_*` | Additional checks for manifest digest, bundled file paths, and the flagship demo bundle. |

The full test suite also runs the linter, all unit tests, viewer preset validation, and optional Numba backend parity on the resource cascade domain.

---

## Reproducibility

- Every run uses NumPy's random number generator with an explicit seed you supply on the command line.
- The same code version, seeds, and flags always produce the same metrics and trajectory (within the float tolerances documented in the frozen benchmark bundles).
- Parallel evaluation is safe only when each worker gets its own copy of the simulation world — the engine handles this automatically via world cloning.
- The optional Numba-accelerated backend for the resource cascade domain is tested for numeric parity against the default NumPy path before any performance claims are made.

---

## Adding new capabilities

| What you want to add | How to do it |
|----------------------|--------------|
| A new simulation domain | Add a `world/` module with reset, step, and metrics; add a rollout function; write replay contract tests; add a frozen reference bundle. |
| A custom attacker/defender loop | Pass your own deterministic rollout function to `alternating_coevolution_rollout`. |
| A real-world network topology | Use the `--neighbor-json` flag with a JSON file of directed out-neighbor lists. |
| Faster resource cascade runs | `pip install -e ".[accelerate]"` enables the optional Numba-accelerated backend. |

Adding physics where multiple worlds share state within a single timestep is out of scope for this repository and belongs in a separate research fork.
