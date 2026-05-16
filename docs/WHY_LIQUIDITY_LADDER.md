# Why liquidity ladder / margin stress?

Phase **N** adds a **fourth** thin reference domain that is **not** a relabeled peg, backlog, or cascade story.

## Physics in one paragraph

**Margin utilization** rises when exogenous **reserve_loss** shocks trigger calls; **ladder depth** (funding runway) erodes under **rumor** haircuts. Deleveraging and slow depth recovery compete with redeem pressure from the same thin agent mixture used elsewhere. Collapse is **utilization above a ceiling** or **depth below a floor** — a liability-structure narrative distinct from peg panic, network contagion, resource overload, or ops backlog.

## What we do not claim

- No calibrated margin tables, Basel compliance, or live-market forecasts.
- No cross-world coupling inside one `step()` — multi-kernel audits stay on decoupled composite JSON (`fragility-institutional-composite-v3`).

## Where to look in code

| Piece | Location |
|-------|----------|
| World | `fragility_engine.world.liquidity_ladder.LiquidityLadderWorld` |
| Rollout | `rollout_liquidity_ladder` in `fragility_engine.runner` |
| Frozen bundle | `liquidity_ladder_rollout_v1` in `benchmarks/suite.py` |
| GA smoke | `scripts/run_liquidity_ladder_ga_demo.py` |

Gate doc: [`phase_n_liquidity_ladder.md`](phase_n_liquidity_ladder.md). Charter: [`BOUNDARIES.md`](../BOUNDARIES.md) (Phase N).
