# Fragility Discovery Engine — Whitepaper

**Repository:** [github.com/AgenticOp-io/fragility-discovery-engine](https://github.com/AgenticOp-io/fragility-discovery-engine)  
**Version:** 3.1 · **Release:** v0.5.0 · **License:** open-source Python

---

## What is this?

The **Fragility Discovery Engine** is an open-source Python framework for **systematically finding the conditions under which a simulated system breaks** — and then explaining *why* it broke in a form you can archive, reproduce, and compare.

It is built to answer questions like:

- A stablecoin peg holds under normal conditions — at what point does a sequence of redemption shocks trigger a panic and break it?
- A financial network is stable in isolation — which combination of node-level shocks causes contagion to cascade across the graph?
- A service infrastructure runs within capacity — how does an overload in one layer propagate until the whole system fails?
- A funding ladder is adequately margined — what reserve losses and rumor shocks erode the runway fast enough to cause a margin call spiral?
- A supply buffer looks adequate — which demand spikes and fulfillment shocks drive stock to stockout?

In each case the engine searches for the shock sequences that matter, records exactly how the system responded, and produces controlled comparisons that show what would have changed under different conditions.

The engine answers that question with **directed search** (genetic algorithms, Monte Carlo sampling, co-evolution) over discrete-time simulations, then exports structured JSON artifacts at every step so results are **deterministic, verifiable, and citable**.

---

## The core idea: shock schedules and fragility metrics

Any system the engine studies is described as a **simulation world**: a state that resets to known initial conditions, steps forward one timestep at a time, and exposes a small set of scalar metrics. The engine does **not** try to build a single monolithic model of everything — it provides six thin reference worlds that each tell a different physics story.

What all worlds share is the **shock schedule**: an encoded sequence of external pressures applied at each timestep. The engine's adversary layer searches over possible schedules to find which ones are most damaging. This is analogous to fuzz testing for software — but for system-level fragility, with interpretable outputs instead of crash logs.

A run produces:

- **How bad did it get?** — `integral_instability`, `peak_instability`, whether the system `collapsed`.
- **How expensive was the attack?** — `attack_cost` (the resource cost of applying those shocks).
- **When did it collapse?** — `collapse_timestep`, optional recovery metrics.
- **What did the trajectory look like?** — full timestep-by-timestep replay JSON.

The engine records these for every evaluation and exposes them through a consistent JSON schema, so you can compare runs across seeds, modes, and parameter settings.

---

## The five simulation domains

The engine ships five **reference domains** — modular worlds with different physics but the same schedule encoding. You pick whichever fits your research framing:

| Domain | What it models |
|--------|----------------|
| **Aggregate peg** | A scalar stablecoin under redemption pressure and panic dynamics |
| **Network contagion** | Panic spreading across an explicit graph of interconnected nodes |
| **Resource cascade** | Overload propagating through two coupled capacity layers |
| **Service backlog** | An operations queue where processing rate fights rising demand |
| **Liquidity ladder** | Margin utilization vs funding runway under reserve and rumor shocks |

These are **deliberately simplified** reference kernels. They are not calibrated to any real institution or market. Their purpose is to make the engine's search and explanation methods testable across multiple qualitatively different collapse stories. If your domain of interest has similar structure — state that resets, steps forward, and can be driven to a threshold — you can write a new world module using the same interface.

---

## What the engine does that is hard to do by hand

**1. Directed search for fragile conditions**

Running the simulation once with a hand-crafted shock is exploratory. Running Monte Carlo sampling or a genetic algorithm over thousands of possible shock schedules finds *systematically worse* conditions — and records the ones that score highest on instability or lowest cost-to-collapse. Pareto search finds the full tradeoff frontier between severity and attack cost.

**2. Counterfactuals and sensitivity**

After finding a collapsing run, you can ask: what if those shocks had been weaker? What if the initial conditions were different? What if certain shock steps were removed? The engine answers these questions by re-running the simulation under controlled interventions and diffing the outputs — producing **counterfactual JSON pairs** you can compare side by side.

**3. Mutation chains and attribution**

For network and domain-specific worlds, the engine can build **ordered mutation chains**: intermediate rollouts where shocks are applied one by one. Each step in the chain shows how instability accumulates, which lets you trace which shocks contributed most to a collapse.

**4. Reproducible records**

Every output is a JSON file with a versioned schema, the seed used, and the CLI flags that produced it. A **benchmark harness** ships with six frozen reference runs whose golden metrics are checked in CI on every commit. An optional **certificate** script hashes your artifacts and records the Python environment so a paper appendix or audit packet has a stable reference point.

**5. Attacker–defender co-evolution**

The engine includes an alternating search loop where an adversary tries to find collapsing schedules while a defender tries to suppress collapse. The result is a two-objective Pareto frontier trading off attacker severity against defender response cost.

---

## What this is not

- **Not a calibrated model.** The domains are pedagogical. They do not have empirically fitted parameters from any real institution, market, or infrastructure system.
- **Not a forecast or trading system.** The engine produces research artifacts for analysis, not predictions about real-world outcomes.
- **Not a compliance tool.** Outputs are not regulatory-grade stress tests.
- **Not a coupled multi-physics engine.** The six worlds never exchange state inside a timestep. "Institutional composite" outputs apply one schedule to multiple worlds independently and summarize results side by side — there is no cross-world coupling in the physics.
- **Not a platform you deploy.** There is no server, database, or hosted service. It is a Python library and a set of CLI scripts you run locally or in CI.

---

## Who this fits

**Researchers** working on adversarial robustness, counterfactual explanation, fragility and resilience methodology, or simulation-based evaluation will find the engine useful as:
- a controlled environment where ground-truth interventions are mechanical and reproducible
- a benchmark platform with frozen golden runs and versioned JSON schemas
- a codebase demonstrating the separation of search, physics, and explanation layers

**Engineers** building resilience tooling or red-team pipelines will find it useful as:
- a CLI-first framework where every run is reproducible and can be diffed
- a starting point for adding a new physics world to an existing search and explanation stack

**Reviewers and paper authors** will find the artifact chain (replay → Pareto → counterfactuals → certificate) useful as a reproducibility trail for simulation-based results.

This is **not** the right fit if you need real-time simulation, calibrated real-world models, or infrastructure you can deploy to end users.

---

## Quick orientation: what you run

```bash
# Install
pip install -e ".[dev]"

# Run one search (aggregate domain, ~2 min)
python scripts/run_ga_demo.py --export-replay best.json --generations 4 --seed 42

# View result
python scripts/narrate_frozen_json.py best.json
# Open artifacts/replay_viewer/index.html in a browser, load best.json

# Counterfactual: what if those shocks were removed?
python scripts/export_counterfactual.py --mode aggregate --intervention remove_steps \
  --export-replay-dir ./cf_out

# Verify frozen benchmarks match expected metrics
python scripts/run_benchmark_suite.py --validate
```

Full tutorials, domain-specific CLI examples, and viewer guides: [`HOW_TO_USE.md`](HOW_TO_USE.md).  
Complete CLI and schema reference: [`REFERENCE.md`](REFERENCE.md).  
Package layout and data flow: [`ARCHITECTURE.md`](ARCHITECTURE.md).  
Hard limits, wall-clock, non-goals: [`SCALE_AND_LIMITS.md`](SCALE_AND_LIMITS.md) and [`BOUNDARIES.md`](../BOUNDARIES.md).

---

## Document control

| Field | Value |
|--------|--------|
| **Version** | 3.0 |
| **Last updated** | 2026-05 — full conceptual rewrite |
| **Repo state** | Tracks `main`; cite tag `v0.4.0` alongside frozen JSON for reproducibility. |
| **Questions** | [GitHub Issues](https://github.com/AgenticOp-io/fragility-discovery-engine/issues) |
