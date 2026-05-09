# Fragility Discovery Engine

[![CI](https://github.com/theorem6/fragility-discovery-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/theorem6/fragility-discovery-engine/actions/workflows/ci.yml)

Autonomous **coverage-guided-style** search over a modular simulation: mutate shock schedules, maximize instability metrics, then extract **minimal collapse sequences** and causal replay artifacts.

## Layout (four engines)

| Layer | Role |
|--------|------|
| `fragility_engine.world` | Domain physics only — no attacker concepts. |
| `fragility_engine.agents` | Behavior archetypes — `observe → decide → act`. |
| `fragility_engine.adversary` | Deterministic search (Monte Carlo + GA) over shock schedules. |
| `fragility_engine.explain` | Ablation / minimization / **counterfactual** bundles. |
| `fragility_engine.network` | ``ContagionGraph`` + topology + contagion diffusion (Phase B). |
| `fragility_engine.coevolution` | Alternating attacker/defender search scaffold. |

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

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/week1_smoke.py` | Deterministic rollout smoke test |
| `scripts/run_ga_demo.py` | GA + greedy minimization + replay stats |
| `scripts/run_network_demo.py` | GA on **graph contagion** world |
| `scripts/export_replay.py` | Write versioned `replay.json` (`--mode aggregate` or `--mode network`) |
| `scripts/fragility_surface.py` | CSV grid scan (parameter fragility map, shocks off) |
| `scripts/run_coevolution.py` | Alternating attacker/defender GA |
| `scripts/export_pareto_front.py` | Dump `pareto_front.json` (2-objective archive) |
| `scripts/find_cheap_collapse.py` | GA with attack-cost penalty (Phase C demo) |
| `scripts/export_counterfactual.py` | Write counterfactual attribution JSON |

Static replay UI (drag-and-drop JSON): `artifacts/replay_viewer/index.html` — hover / drag timeline scrub, keyboard arrows.

## Week roadmap (suggested)

1. CLI smoke + collapse metric — `scripts/week1_smoke.py`
2. Evolutionary adversary — `scripts/run_ga_demo.py`
3. Network contagion — `fragility_engine.network` + `StablecoinNetworkWorld`
4. Replay JSON — `runner.rollout_to_replay_dict` (`schema_version` **0.4.0**, includes `events_lane`)
5. Web UI — later; consume replay artifact only after engine stabilizes.
