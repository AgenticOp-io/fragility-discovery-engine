# Why liquidity ladder / margin stress?

Phase **N** adds a **fourth** thin reference domain. It is **not** a relabeled peg, backlog, or cascade: the state variables and collapse predicates are about **funding runway** and **margin utilization**, not peg deviation, queue depth, or resource overload alone.

---

## Physics in one paragraph

**Margin utilization** rises when exogenous **reserve_loss** shocks trigger calls; **ladder depth** (funding runway) erodes under **rumor** haircuts. Deleveraging and slow depth recovery compete with redeem pressure from the same thin agent mixture used elsewhere. Collapse is **utilization above a ceiling** or **depth below a floor** — a liability-structure narrative distinct from peg panic, network contagion, resource overload, or ops backlog.

---

## State and interventions (operator view)

| Concept | Role in `LiquidityLadderWorld` |
|---------|--------------------------------|
| `initial_margin` | Reset knob; counterfactual axis `initial_margin_shift` |
| Schedule rows | Same `(horizon, 2)` genome encoding as other domains |
| `reserve_loss` / `rumor` lanes | Exogenous shocks decoded from the schedule |
| Collapse | Utilization ceiling or depth floor breached |

Typical CLI entry points:

```bash
python scripts/run_liquidity_ladder_ga_demo.py --export-replay out.json --initial-margin 0.06
python scripts/export_replay.py --mode liquidity_ladder --initial-margin 0.07 --out replay.json
python scripts/run_benchmark_suite.py --validate   # includes liquidity_ladder_rollout_v1
```

Counterfactual cookbook: [`liquidity_ladder_counterfactual_example.md`](liquidity_ladder_counterfactual_example.md).

---

## What we do not claim

- No calibrated margin tables, Basel compliance, or live-market forecasts.
- No cross-world coupling inside one `step()` — multi-kernel audits stay on decoupled composite JSON (`fragility-institutional-composite-v3` does not yet add liquidity as a fifth kernel; see [`ROADMAP_NEXT.md`](../ROADMAP_NEXT.md)).

---

## Where to look in code

| Piece | Location |
|-------|----------|
| World | `fragility_engine.world.liquidity_ladder.LiquidityLadderWorld` |
| Rollout | `rollout_liquidity_ladder` in `fragility_engine.runner` |
| Frozen bundle | `liquidity_ladder_rollout_v1` in `fragility_engine.benchmarks.suite` |
| GA demo | `scripts/run_liquidity_ladder_ga_demo.py` |
| Mode-aware CLIs | `export_replay.py`, `run_mc_demo.py`, `run_coevolution.py`, `export_pareto_front.py`, … with `--mode liquidity_ladder` |

Gate doc: [`phase_n_liquidity_ladder.md`](phase_n_liquidity_ladder.md). Charter exit criteria: [`BOUNDARIES.md`](../BOUNDARIES.md) (Phase N).
