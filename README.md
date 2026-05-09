# Fragility Discovery Engine

Autonomous **coverage-guided-style** search over a modular simulation: mutate shock schedules, maximize instability metrics, then extract **minimal collapse sequences** and causal replay artifacts.

## Layout (four engines)

| Layer | Role |
|--------|------|
| `fragility_engine.world` | Domain physics only — no attacker concepts. |
| `fragility_engine.agents` | Behavior archetypes — `observe → decide → act`. |
| `fragility_engine.adversary` | Deterministic search (Monte Carlo + GA) over shock schedules. |
| `fragility_engine.explain` | Ablation / minimization / attribution helpers. |

Phase 1 is **deterministic** (fixed NumPy RNG seeds). LLM policies stay out until the core loop is proven.

**Scope creep guardrail:** read [`BOUNDARIES.md`](BOUNDARIES.md) before adding agents, graph models, multi-objective fitness, UI, or defender loops.

## Quick start

```powershell
cd C:\Users\david\projects\fragility-discovery-engine
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -q
python scripts/week1_smoke.py
python scripts/run_ga_demo.py
```

## Week roadmap (suggested)

1. CLI smoke + collapse metric — `scripts/week1_smoke.py`
2. Evolutionary adversary — `scripts/run_ga_demo.py`
3. Replay JSON + timeline scaffold — `fragility_engine.runner`
4. Web UI — later; consume replay artifact only after engine stabilizes.
