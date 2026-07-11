# Coupled “mega-institution” dynamics — fork policy

This repository ships **decoupled** reference kernels (aggregate peg, network contagion, resource cascade, service backlog) and **audit composites** that evaluate the **same shock schedule** on multiple kernels **without** shared mutable state across `World.step()`.

## Active flight

**v0.4** lives in [`forks/coupled_institution/`](../forks/coupled_institution/) with charter [`forks/coupled_institution/CHARTER.md`](../forks/coupled_institution/CHARTER.md):

- Explicit `CouplingContract` + opt-in **liquidity** triad and **backlog** tetra
- Per-step `coupling_contrib_to_*` metrics (panic, overload, liquidity, backlog)
- Replay schema `coupled-fork-0.4.0`
- Worth-it bar (two-scalar + triad + tetra): `python scripts/run_coupled_worth_it_bar.py`
- Tetra under search (GA/MC + pins): `python scripts/check_coupled_fork_tetra_search.py`
- Operator capsules: `fragility shorthand resolve coupled-worth-it` / `coupled-tetra-search`

Default contract keeps liquidity/backlog channels off so the v0.1 golden bundle (`coupled_institution_rollout_v1`) stays green.

## Why not on main charter

A **single coupled state graph** is a **different research product**: new physics contracts, replay schema decisions, benchmark oracles, and attribution semantics. Shipping it inside `fragility_engine.world` would blur [`BOUNDARIES.md`](../BOUNDARIES.md).

## If you extend it

1. Keep work under `forks/coupled_institution/` (or a sibling package).
2. **Schema bump** for replay JSON with migration notes.
3. New **golden** metrics when physics change; do **not** overload `fragility-institutional-composite-v*`.
4. Pass the **worth-it bar** before promoting complexity (third scalar, etc.).
5. Reuse main-engine schedule encoding / search / counterfactual patterns where honest.

## Related shipped tooling

Use **institutional composite v1–v5** only for **side-by-side** metrics under identical schedules (`scripts/institutional_composite_demo.py`).

Operator Intelligence Shorthand (Chrysalis-inspired, post-hoc only): [`docs/INTELLIGENCE_SHORTHAND.md`](INTELLIGENCE_SHORTHAND.md).

## Public demo

| Demo | URL |
|------|-----|
| Coupled replay | `/artifacts/replay_viewer/index.html#src=sample_coupled_institution_replay.json` |
| Coupling mutation chain | `/artifacts/attribution_viewer/index.html#src=sample_coupled_mutation_chain.json` |
| Coupling strength sweep chart | `/artifacts/coupling_sweep_viewer/index.html` |
| Coupling baseline vs variant | `/artifacts/coupling_comparison_viewer/index.html` |
| Fork JSON bundle (download) | `/artifacts/coupled_fork_demo/` |
| Policy (this page) | `/docs/fork-coupling.html` |

```bash
python scripts/regenerate_coupled_fork_artifacts.py
python scripts/run_coupled_worth_it_bar.py
python scripts/check_coupled_fork_tetra_search.py
python scripts/narrate_coupled_fork_bundle.py --cite-digest
fragility shorthand resolve coupled-tetra-search
```
