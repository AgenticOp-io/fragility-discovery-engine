# AI_READ — how to read this repository

**Audience:** coding agents and reviewers. Read this before inventing features, rewriting positioning, or treating the six reference worlds as the product.

**Normative law:** [`BOUNDARIES.md`](BOUNDARIES.md) wins over enthusiasm, README marketing tone, and phase memos. If a change violates world/adversary separation, determinism, or an explicit non-goal, do not ship it.

---

## What this is (one sentence)

A **deterministic stress-search harness**: it searches shock schedules (Monte Carlo / genetic algorithms) against a modular discrete-time simulation, then exports **replay JSON**, **minimized failing schedules**, and **counterfactual re-run** evidence.

It is **not** a calibrated model of any real institution, a digital-twin platform, a compliance engine, or a causal-identification toolkit.

---

## Why it exists

Real systems fail from **ordering and interaction** of stresses (timing × capacity × decay), not only from “everything at once is bad.” The engine exists to:

1. **Search** for high-damage schedules under a fixed budget.
2. **Minimize** those schedules to short, auditable event sequences.
3. **Document** outcomes with frozen, re-runnable artifacts (seeds, configs, hashes, certificates).
4. **Transfer** the same loop to a world *you* write (BYOW), instead of pretending the six toys are your domain.

The six built-in domains exist as **toy regression oracles** for CI and demos. They prove the pattern generalizes. They do **not** claim institutional realism.

**Worth-it bar (BYOW):** the engine earns its keep only when the worst-case shock *ordering* is non-obvious. If search only rediscovers “max everything,” it added nothing. See [`docs/BRING_YOUR_OWN_WORLD.md`](docs/BRING_YOUR_OWN_WORLD.md).

---

## How it works (core loop)

```
genome / schedule  →  decode events  →  world.reset()  →  world.step(events) × T
                              ↓
                     RolloutResult (trajectory, collapsed?, fitness)
                              ↓
              search / minimize / counterfactual / replay JSON / certificate
```

| Piece | Role | Must not |
|-------|------|----------|
| **World** (`reset`, `step`, `state_vector`, `instability_score`, `is_collapsed`) | Physics / state only | Contain attacker logic or hidden RNG |
| **Adversary** (`adversary.search`, encoding) | Propose schedules; score fitness | Know domain physics |
| **Explain** (`explain.*`) | Ablation, minimization, counterfactual re-runs | Change world physics |
| **Runner / replay** | Package trajectories as versioned JSON | Invent causality beyond re-runs |

**Shock encoding:** NumPy array shape `(horizon, 2)` in `[0, 1]`. Kinds are fixed (`reserve_loss`, `rumor`, …); **meaning is world-defined**. Same seed ⇒ same rollout.

**Two harness modes (v0.6.0+):**

| Mode | Package | Damage definition | CLI |
|------|---------|-------------------|-----|
| Dynamics | `fragility_engine.byow` | `is_collapsed()` / instability | `fragility search` / `minimize` |
| Falsification | `fragility_engine.falsify` | `claim_violated()` predicate + optional snapshot reset | `fragility falsify search` |

Falsification finds **presence** of violations, never **absence**. Replay `meta.harness_kind` is `dynamics_v1` or `falsification_v1`.

---

## Product surface vs charter toys

| What | Where | Status |
|------|--------|--------|
| **Product path** | BYOW + `fragility` CLI + falsify | **Shipped** v0.6.0 (Phases Q–S) |
| Tutorial worlds | `capacity-pool`, `token-bucket`, `ranked-store` | Examples, **not** charter domains |
| Six reference worlds | `aggregate`, `network`, `resource_cascade`, `service_backlog`, `liquidity_ladder`, `inventory_buffer` | Frozen **oracles**; charter domains **closed** at six |
| Coupled mega-model | `forks/coupled_institution/` | Fork policy — not default `main` product |

Do **not** open a seventh charter reference domain without a new `BOUNDARIES.md` admission. Prefer BYOW adapters.

---

## Package map (where code lives)

```
src/fragility_engine/
  world/          # six toy physics kernels
  agents/         # thin observe → decide → act archetypes
  adversary/      # encoding, fitness, MC + GA search
  explain/        # minimize, counterfactuals, attribution merge
  network/        # ContagionGraph / topology helpers
  coevolution/    # alternating attacker/defender search
  byow/           # Bring-your-own-world SDK + tutorial examples
  falsify/        # predicate / snapshot falsification harness
  shorthand/      # operator Intelligence Shorthand (IS tiers; no LLM in-sim)
  cli/            # `fragility` console entry (search, minimize, falsify, shorthand, …)
  benchmarks/     # frozen suite + certificate helpers
  fel/            # Fragility Evidence Language conventions
scripts/          # one-task CLIs (demos, exports, GCE, viewers)
forks/coupled_institution/  # mega-institution research fork (not main charter)
examples/         # thin wrappers around byow/falsify tutorials
tests/            # determinism, contracts, CLI smoke
benchmarks/       # golden bundles — `run_benchmark_suite.py --validate`
docs/             # human docs; start at docs/README.md
```

Install: `pip install -e ".[dev]"` then `fragility --help` or `python -m fragility_engine.cli.main --help`.

Operator recipes: `fragility shorthand list` — see [`docs/INTELLIGENCE_SHORTHAND.md`](docs/INTELLIGENCE_SHORTHAND.md).
Coupled fork: [`forks/coupled_institution/CHARTER.md`](forks/coupled_institution/CHARTER.md).
---

## Evidence and claims (do not overclaim)

| Allowed claim | Forbidden claim |
|---------------|-----------------|
| “Under seed S and config C, schedule G collapses / violates predicate P” | “This proves the real institution will fail” |
| “Removing event at t=k and re-running changes outcome (counterfactual)” | “We identified the causal root cause” |
| “Frozen bundle X still matches golden metrics” | “Search exhaustively proved safety” |
| “FEL Δ / certificate hashes match this artifact trail” | “Governance / compliance sign-off” |

Citation / archive: Zenodo DOI `10.5281/zenodo.20455689`, [`CITATION.cff`](CITATION.cff), FEL preprint under `docs/preprint/`. Certificate path: `fragility certify` or `scripts/run_flagship_demo.py`.

---

## Doc triage (what to open for what)

| Need | Open |
|------|------|
| Scope / non-goals / phase gates | [`BOUNDARIES.md`](BOUNDARIES.md) |
| Human install + tutorials | [`docs/HOW_TO_USE.md`](docs/HOW_TO_USE.md) |
| Architecture / data flow | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| CLI flags / schemas | [`docs/REFERENCE.md`](docs/REFERENCE.md) |
| Custom world | [`docs/BRING_YOUR_OWN_WORLD.md`](docs/BRING_YOUR_OWN_WORLD.md) |
| Predicate harness | [`docs/FALSIFICATION_HARNESS.md`](docs/FALSIFICATION_HARNESS.md) |
| Honest limits | [`docs/SCALE_AND_LIMITS.md`](docs/SCALE_AND_LIMITS.md) |
| What shipped / what’s next | [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md), [`ROADMAP_NEXT.md`](ROADMAP_NEXT.md) |
| Version / release | [`RELEASING.md`](RELEASING.md), `pyproject.toml` / `__version__` |

Phase letters (A–S) are **charter section headers**, not required vocabulary for end users. Q–S are **shipped** at v0.6.0; do not re-propose them as open work unless `BOUNDARIES.md` says otherwise.

---

## Common AI failure modes (avoid these)

1. **Treating the six toys as the product** — lead with BYOW / falsify; toys are oracles.
2. **Adding a seventh domain** — charter closed; write an adapter instead.
3. **Putting attack logic inside `World.step`** — shocks enter only via exogenous events.
4. **Claiming “exactly why it broke”** — say counterfactual re-run / attribution, not causal ID.
5. **Breaking determinism** — no wall-clock, no hidden global RNG in rollouts.
6. **Changing frozen golden metrics** without an explicit charter + suite update.
7. **Shipping UI before replay contracts** — evidence JSON + tests first (`BOUNDARIES.md`).
8. **Reading stale roadmap text** — check `BOUNDARIES.md` / phase memo **Status:** lines; Q–R–S are shipped.
9. **Merging coupled-fork physics into `main` worlds** — fork stays under `forks/` unless charter changes.
10. **Skipping `--validate`** after search/explain changes — run `python scripts/run_benchmark_suite.py --validate`.

---

## Minimal verification before claiming “done”

```powershell
pip install -e ".[dev]"
python -m pytest tests/test_byow_cli_falsify.py -q
python scripts/run_benchmark_suite.py --validate
fragility search --example capacity-pool --generations 4 --population-size 12
fragility falsify search --example ranked-store --generations 8 --population-size 20
```

If those pass and the change respects [`BOUNDARIES.md`](BOUNDARIES.md), you are aligned with how this repo actually works.
