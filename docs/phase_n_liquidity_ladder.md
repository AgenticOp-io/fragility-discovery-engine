# Phase N — liquidity ladder (fourth reference domain)

**Status:** **Adopted** — see [`BOUNDARIES.md`](../BOUNDARIES.md) (Phase N). Admission memo: [`phase_n_fourth_domain_admission.md`](phase_n_fourth_domain_admission.md).

## Selected candidate

**Liquidity ladder / margin** — scalar-friendly margin utilization + ladder depth; ≤5 archetypes; one frozen bundle `liquidity_ladder_rollout_v1`.

## Replay contract (`simulation_mode`: `liquidity_ladder`)

| Field | Semantics |
|-------|-----------|
| `metrics.price` | Ladder depth headroom (`D`) |
| `metrics.backing_ratio` | Same as price |
| `state_vector` | `[M, D, M/margin_collapse, timestep]` |
| Collapse | `M ≥ margin_collapse` or `D ≤ depth_floor_collapse` |

Schema **0.4.x** unchanged unless a future bump is justified.

## CLI parity (Phase J / M pattern)

| Capability | Entry |
|------------|--------|
| GA smoke | `scripts/run_liquidity_ladder_ga_demo.py` |
| Pareto export | `scripts/export_pareto_front.py --mode liquidity_ladder` |
| MC | `scripts/run_mc_demo.py --mode liquidity_ladder` |
| Co-evolution | `scripts/run_coevolution.py --mode liquidity_ladder` |
| Bench timing | `scripts/benchmark_rollout.py --mode liquidity_ladder` |
| Replay export | `scripts/export_replay.py --mode liquidity_ladder` |
| Counterfactual | `scripts/export_counterfactual.py` (`liquidity_ladder_initial_margin_shift`) |
| ε-sweep | `scripts/counterfactual_epsilon_sweep.py` (`--mode liquidity_ladder`) |
| Mutation chain | `scripts/export_liquidity_ladder_counterfactual_chain.py` (`liquidity-ladder-mutation-chain-spec-v1`) |

Aggregate/network/cascade/backlog chain fixtures stay oracles; liquidity-ladder chain exports now follow the same small-fixture pattern.

## Exit criteria

- [x] World + runner + replay contract tests
- [x] Frozen bundle + `GOLDEN_METRICS` + integral band
- [x] GA smoke + Pareto / MC / co-evolution wiring
- [x] “Why” doc — [`WHY_LIQUIDITY_LADDER.md`](WHY_LIQUIDITY_LADDER.md)
- [x] Mutation-chain spec `liquidity-ladder-mutation-chain-spec-v1` + `export_liquidity_ladder_counterfactual_chain.py` + path trace `explanation-mutation-chain-path-liquidity-ladder-v1`
