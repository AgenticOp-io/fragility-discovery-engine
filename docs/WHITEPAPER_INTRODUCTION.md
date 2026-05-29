# Fragility Discovery Engine — Overview

**What it is:** An open-source Python tool for finding the conditions that break a simulated system, then explaining exactly why it broke.

**Live demo:** http://34.61.255.147/ · **Source:** https://github.com/AgenticOp-io/fragility-discovery-engine · **Release:** v0.5.0

---

## The core idea

You describe a system as a simulation world — something that resets to known starting conditions and advances one step at a time. The engine searches across thousands of possible stress sequences to find the ones that cause the most damage, then saves a step-by-step record of how the system failed.

That record is a JSON file you can replay in the browser, compare against counterfactuals, and reproduce exactly by re-running with the same seed.

---

## Six simulation domains

The engine ships six ready-to-use worlds. Pick the one that matches what you want to study:

| Domain | What it models |
|--------|----------------|
| **Aggregate peg** | A stablecoin reserve and panic level under redemption pressure |
| **Network contagion** | Panic spreading across a graph of interconnected nodes |
| **Resource cascade** | Overload propagating through two coupled capacity layers |
| **Service backlog** | A work queue where processing rate fights rising demand |
| **Liquidity ladder** | Financial margin eroding toward a forced sell-off |
| **Inventory buffer** | Stock level declining under demand surges |

These are deliberately simple models — not calibrated to any real institution. Their purpose is to let the search and explanation methods work across several different failure patterns.

---

## What a run produces

1. **Replay file** — every timestep recorded: what happened, how bad it got, when it collapsed. Load in the browser to scrub the timeline.
2. **Trade-off chart** (attacker vs defender runs) — the full range between cheap-but-mild and expensive-but-devastating attacks.
3. **Attribution trace** — counterfactual comparisons showing which specific shocks caused the collapse.
4. **Composite audit** — same attack genome evaluated across multiple domains side by side.

All outputs are plain JSON with stable schemas. Every result is reproducible from the seed.

---

## What it is not

- Not a live trading system or market data feed
- Not a regulatory compliance tool
- Not a calibrated model of any specific institution

---

## Quick start

```bash
# Install
git clone https://github.com/AgenticOp-io/fragility-discovery-engine
cd fragility-discovery-engine
python3 -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
pip install -e ".[dev]"

# Run a search
python scripts/run_ga_demo.py --mode aggregate --generations 4 --export-replay out.json

# Open the replay in your browser
open artifacts/replay_viewer/index.html  # then load out.json
```

Full install and usage: [How to Use](/docs/how-to-use.html)
