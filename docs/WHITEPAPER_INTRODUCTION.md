# Fragility Discovery Engine — Overview

**What it is:** An open-source Python **stress-search harness** — wire a resettable discrete-time model, search shock schedules for worst-case failure, export reproducible replay JSON and counterfactual attribution bundles.

**Not:** a calibrated institution model, a causal inference tool, or a drop-in production risk product.

**Live demo:** http://34.61.255.147/ · **Source:** https://github.com/AgenticOp-io/fragility-discovery-engine · **Release:** v0.6.0

---

## The core idea

You describe a system as a simulation world — something that **resets** to known starting conditions and **advances one step at a time**. The engine searches across possible stress sequences to find ones that maximize damage under your metric, then saves a step-by-step record of the run.

That record is JSON you can replay in the browser, compare with counterfactual re-runs, and reproduce with the same seed.

**Attribution** means counterfactual and path deltas on re-rollouts (FEL Δ⁻ / Δ⁺ conventions) — not Pearl-grade causal identification.

---

## Bring your own world (primary path)

Real value is a **~100-line adapter** you write (`reset`, `step`, `state_vector`, `instability_score`, `is_collapsed`). Tutorial: [`BRING_YOUR_OWN_WORLD.md`](BRING_YOUR_OWN_WORLD.md).

```powershell
pip install -e ".[dev]"
fragility search --example capacity-pool
fragility check-world --example capacity-pool
```

---

## Six reference domains (toy regression oracles)

The in-tree worlds are **deliberately simplified** — structural analogies for frozen CI, not models of real institutions:

| Domain | Structural analogy |
|--------|-------------------|
| Aggregate peg | Reserve + panic under pressure |
| Network contagion | Panic on a graph |
| Resource cascade | Coupled capacity layers |
| Service backlog | Queue vs processing rate |
| Liquidity ladder | Margin erosion |
| Inventory buffer | Stock under demand |

Use them to validate the harness; use **BYOW** for your own physics.

---

## What a run produces

1. **Replay file** — timestep trajectory, collapse bit, shock lane.
2. **Pareto archive** (optional) — severity vs attack-cost trade-offs.
3. **Attribution bundles** — counterfactual re-runs and mutation chains.
4. **Certificate / manifest** — reproducibility metadata for papers.

All outputs are schema-versioned JSON with deterministic seeds.

---

## What it is not

- Not a live trading system or market data feed
- Not regulatory compliance or calibrated institutional risk
- Not proof that your production system is safe

---

## Quick start

```bash
git clone https://github.com/AgenticOp-io/fragility-discovery-engine
cd fragility-discovery-engine
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

fragility search --example capacity-pool --export-replay out.json
fragility falsify search --example ranked-store   # invariant predicate demo
python scripts/run_ga_demo.py --mode aggregate --generations 4 --export-replay toy.json
```

Full guide: [How to Use](/docs/how-to-use.html) · **Cite:** Zenodo [10.5281/zenodo.20455689](https://doi.org/10.5281/zenodo.20455689)
