# Coupled mega-institution fork — charter (v0.4)

**Status:** active research flight under [`docs/FORK_COUPLING_RESEARCH.md`](../../docs/FORK_COUPLING_RESEARCH.md).  
**Package:** `coupled-institution` 0.4.x · **not** a main-charter reference domain.

## Purpose

Demonstrate **in-step state exchange** among peg-panic, cascade-overload, **liquidity**, and **service backlog** so search can find **ordering / interaction** effects that a decoupled institutional composite cannot.

## Scalars

| Symbol | Meaning | Default channels |
|--------|---------|------------------|
| `P` | Peg panic | Always on (via `coupling_strength`) |
| `O` | Cascade overload | Always on |
| `L` | Liquidity buffer | Opt-in (`triad_contract`) |
| `B` | Service backlog | Opt-in (`tetra_contract`) |

## Worth-it bar

```bash
python scripts/run_coupled_worth_it_bar.py
```

Requires **all three**: two-scalar, liquidity triad, backlog tetra — each must shift integral vs the previous layer and stay order-sensitive.

## Non-goals

- Calibrated finance / regulatory claims
- LLM as policy inside `step()`
- Overloading institutional composite JSON as coupled physics
- Merging into `fragility_engine.world` without a new `BOUNDARIES.md` phase
- A fifth scalar without a fresh worth-it justification

## Exit criteria

- [x] CouplingContract + channel metrics
- [x] Liquidity triad (v0.3) + backlog tetra (v0.4)
- [x] Schema `coupled-fork-0.4.0`
- [x] Worth-it bar v3 (two-scalar + triad + tetra)
- [x] Golden `coupled_institution_rollout_v1` green (extra channels default off)
- [x] Tetra under search: GA/MC demos + pinned golden `coupled_institution_tetra_rollout_v1` + search pins
- [ ] Stop here unless a new research question needs another scalar or topology

## Tetra search

```bash
python scripts/run_coupled_fork_demo.py --contract tetra --method ga --generations 2 --population-size 8
python scripts/run_coupled_fork_demo.py --contract tetra --method mc --samples 24
python scripts/check_coupled_fork_tetra_search.py
python scripts/validate_coupled_fork_bundle.py
```

## Operator shorthand

`fragility shorthand resolve coupled-worth-it` — see [`docs/INTELLIGENCE_SHORTHAND.md`](../../docs/INTELLIGENCE_SHORTHAND.md).
