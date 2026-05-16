# Aggregate counterfactual examples (Phase I)

All commands assume repo root and `pip install -e ".[dev]"`.

## 1. Scalar ε-sweep on **initial panic** at reset

```powershell
python scripts/counterfactual_epsilon_sweep.py `
  --mode aggregate --horizon 12 `
  --axis initial_panic --values "0.02,0.05,0.10,0.18" `
  --seed 6101 --genome-seed 33 `
  --out artifacts/tmp_agg_panic_sweep.json `
  --emit-trace
```

## 2. Cumulative multi-knob mutation chain

Chain spec (`aggregate-mutation-chain-spec-v1`): steps apply in order on a template clone; the counterfactual rollout compares the **final** clone vs the **original** template (same genome + rollout seed).

```powershell
Set-Content -Path artifacts/tmp_agg_chain.json -Value @'
{
  "schema": "aggregate-mutation-chain-spec-v1",
  "steps": [
    {"kind": "depeg_threshold", "value": 0.88},
    {"kind": "panic_decay", "value": 0.92},
    {"kind": "rumor_panic_gain", "value": 1.15}
  ]
}
'@

python scripts/export_aggregate_counterfactual_chain.py `
  --chain-json artifacts/tmp_agg_chain.json `
  --horizon 12 --seed 6102 --genome-seed 33 `
  --initial-panic 0.05 `
  --out artifacts/tmp_agg_chain_cf.json `
  --path-trace-out artifacts/tmp_agg_chain_path.json
```

Open `artifacts/tmp_agg_chain_path.json` in `artifacts/attribution_viewer/index.html` (mutation-chain path trace).

## 3. Path trace only (from an existing chain export)

Re-use `export_aggregate_counterfactual_chain.py --path-trace-out` as above, or build traces mechanically via `fragility_engine.explain.trace.mutation_chain_path_to_trace_aggregate`.

## See also

- Network counterpart: [`network_counterfactual_example.md`](network_counterfactual_example.md)
- Resource cascade: [`resource_cascade_counterfactual_example.md`](resource_cascade_counterfactual_example.md)
- Phase I normative gates: [`BOUNDARIES.md`](../BOUNDARIES.md)
