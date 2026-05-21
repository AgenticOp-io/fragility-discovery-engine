# Fragility Discovery Engine — Overview

**Repository:** [github.com/AgenticOp-io/fragility-discovery-engine](https://github.com/AgenticOp-io/fragility-discovery-engine)  
**Release:** v0.5.0 · **License:** open-source Python

---

## What is this?

The **Fragility Discovery Engine** is an open-source Python tool for **finding the conditions that break a simulated system** — and then explaining *why* it broke in a way you can save, reproduce, and share.

It answers questions like:

- A stablecoin peg holds under normal conditions — what sequence of shocks triggers a panic and breaks it?
- A financial network is stable in isolation — which combination of node-level pressures causes failure to spread across the whole graph?
- A service infrastructure runs within capacity — how does overload in one layer cascade until the whole system fails?
- A funding ladder looks adequately margined — what reserve losses and rumor shocks erode it fast enough to cause a forced sell-off spiral?
- A supply buffer looks adequate — which demand surges and fulfillment shocks drive stock to a stockout?

In each case the engine searches for the stress sequences that matter, records exactly how the system responded, and produces controlled comparisons that show what would have changed under different conditions.

The engine uses **automated search** (genetic algorithms, Monte Carlo sampling, attacker/defender co-evolution) over step-by-step simulations, and exports structured JSON files at every step so results are **reproducible and easy to compare**.

---

## The core idea: stress schedules and fragility metrics

Any system the engine studies is described as a **simulation world**: a state that resets to known starting conditions, advances one step at a time, and reports a small set of numbers at each step. The engine does not try to build a single model of everything — it provides six focused reference worlds that each tell a different story about how things fail.

What all worlds share is the **stress schedule**: a sequence of external pressures applied at each step. The engine's search layer tests many possible schedules to find which ones cause the most damage. This is similar to fuzz testing in software — but applied to system-level fragility, with results you can read and explain rather than just crash logs.

A run produces:

- **How bad did it get?** — total accumulated stress, peak stress level, whether the system collapsed.
- **How costly was the attack?** — the total resource cost of applying those pressures.
- **When did it collapse?** — which step the collapse occurred, and optional recovery metrics.
- **What did it look like?** — a full step-by-step replay file you can load in the browser.

The engine saves these for every run through a consistent file format, so you can compare runs across different seeds, domains, and settings.

---

## The six simulation domains

The engine ships six **reference domains** — separate worlds with different mechanics but the same schedule format. You pick whichever fits what you want to study:

| Domain                | What it models                                                           |
| --------------------- | ------------------------------------------------------------------------ |
| **Aggregate peg**     | A stablecoin reserve and panic level under redemption pressure           |
| **Network contagion** | Panic spreading across an explicit graph of interconnected nodes         |
| **Resource cascade**  | Overload propagating through two coupled capacity layers                 |
| **Service backlog**   | A work queue where processing rate fights rising demand                  |
| **Liquidity ladder**  | Financial margin eroding under reserve losses and rumors                 |
| **Inventory buffer**  | Stock level declining under demand surges and fulfillment problems       |

These are **deliberately simple** models. They are not calibrated to any real institution or market. Their purpose is to let the engine's search and explanation methods work across several different failure patterns. If your system follows a similar structure — state that resets, steps forward, and can be driven past a threshold — you can write a new world module using the same interface.

---

## What the engine does that is hard to do by hand

**1. Systematic search for weak points**

Running a simulation once with a hand-crafted scenario is exploratory. Running thousands of possible stress schedules through a genetic algorithm finds *systematically worse* conditions — and records the ones that score highest on damage or lowest cost-to-collapse. Attacker/defender co-evolution finds the full trade-off between how severe an attack is and how much it costs.

**2. Counterfactuals and sensitivity**

After finding a scenario that causes collapse, you can ask: what if those shocks had been weaker? What if the starting conditions were different? What if certain shock steps were removed? The engine answers these questions by re-running the simulation with controlled changes and comparing the outputs — producing **before/after comparison files** you can inspect side by side.

**3. Step-by-step attribution**

The engine can apply discrete changes to the world's parameters one at a time and record how instability accumulates at each step. This lets you trace which shocks or parameter changes contributed most to a collapse.

**4. Reproducible records**

Every output is a JSON file with the version, the random seed used, and the exact settings that produced it. A benchmark harness ships with six frozen reference runs whose expected results are checked automatically on every code change. An optional certificate script creates a single file bundling your results and environment details — useful for paper appendices or audit records.

**5. Attacker–defender co-evolution**

The engine includes an alternating search loop where one side tries to find collapsing scenarios while the other tries to prevent collapse. The result is a curve showing all the non-dominated trade-offs between attack severity and defense cost.

---

## What this is not

- **Not a calibrated model.** The domains are teaching tools. They do not have parameters fitted to any real institution, market, or infrastructure system.
- **Not a forecast or trading system.** The engine produces research artifacts for analysis, not predictions about real-world outcomes.
- **Not a compliance tool.** Outputs are not regulatory-grade stress tests.
- **Not a coupled multi-system engine.** The six worlds never share state within a step. The "composite" output mode runs the same attack through multiple worlds independently and compares the results — the worlds do not interact with each other.
- **Not a calibrated real-world risk tool.** If you need real-time simulation, empirically fitted models, or output that is safe to act on in production, this is not the right fit.

---

## Who this fits

**Researchers** working on adversarial robustness, counterfactual explanation, fragility and resilience, or simulation-based evaluation will find the engine useful as:

- a controlled environment where interventions are mechanical and fully reproducible
- a benchmark platform with frozen reference runs and versioned output formats
- a codebase showing how search, physics, and explanation can be cleanly separated

**Engineers** building resilience tooling or red-team pipelines will find it useful as:

- a command-line tool where every run is reproducible and results can be diffed
- a starting point for adding a new simulation domain to an existing search and explanation stack

**Reviewers and paper authors** will find the artifact chain (replay → trade-off chart → counterfactuals → certificate) useful as a reproducibility trail for simulation-based results.

---

## Quick start

```bash
# Install
pip install -e ".[dev]"

# Run one search (~2 minutes, aggregate domain)
python scripts/run_ga_demo.py --export-replay best.json --generations 4 --seed 42

# Read a summary of the result
python scripts/narrate_frozen_json.py best.json

# Open artifacts/replay_viewer/index.html in a browser and load best.json

# What if those shocks were removed?
python scripts/export_counterfactual.py --mode aggregate --intervention remove_steps \
  --export-replay-dir ./cf_out

# Verify the frozen benchmark results match expectations
python scripts/run_benchmark_suite.py --validate
```

Full tutorials, domain examples, and viewer guides: [How to Use](/docs/how-to-use.html).  
Complete command reference: [Reference](/docs/reference.html).  
Package layout and data flow: [Architecture](/docs/architecture.html).

---

*Last updated: 2026-05 · Release v0.5.0 · [GitHub Issues](https://github.com/AgenticOp-io/fragility-discovery-engine/issues)*
