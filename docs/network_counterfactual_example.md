# Network counterfactual examples (Phase I)

All commands assume repo root and `pip install -e ".[dev]"`.

Multi-edge weights (one JSON patch file listing several directed out-edges):

```powershell
Set-Content -Path artifacts/tmp_patch.json -Value '[{"from":0,"to":1,"weight":3},{"from":1,"to":0,"weight":2}]'
python scripts/export_counterfactual.py `
  --mode network --neighbor-json artifacts/tmp_nl.json --horizon 10 `
  --intervention edge_weights_shift --edges-patch-json artifacts/tmp_patch.json `
  --seed 7203 --genome-seed 54 --out artifacts/tmp_cf_multi_edge.json
```

Chain specs may include `"kind": "edge_weights_patch", "edges": [ ... ]` alongside `contagion_beta` steps.

## 1. Baseline vs higher uniform **base panic** (same genome + rollout seed)

```powershell
python scripts/export_counterfactual.py `
  --mode network --nodes 14 --horizon 12 `
  --intervention base_panic_shift `
  --base-panic 0.05 --variant-base-panic 0.18 `
  --seed 5001 --genome-seed 19 `
  --out artifacts/tmp_cf_panic.json `
  --export-replay-dir artifacts/tmp_cf_panic_replays
```

Compare `artifacts/tmp_cf_panic_replays/baseline.json` vs `counterfactual.json` in the replay viewer (`artifacts/replay_viewer/index.html`).

## 2. Baseline vs lower **contagion β** (topology-preserving clone)

```powershell
python scripts/export_counterfactual.py `
  --mode network --nodes 14 --horizon 12 `
  --intervention contagion_beta_shift `
  --beta 0.42 --variant-beta 0.12 --base-panic 0.06 `
  --seed 5002 --genome-seed 19 `
  --out artifacts/tmp_cf_beta.json `
  --export-replay-dir artifacts/tmp_cf_beta_replays
```

## 3. Timestep removal (existing behavior)

```powershell
python scripts/export_counterfactual.py `
  --mode network --nodes 14 --horizon 12 `
  --intervention remove_steps --remove "0,2" `
  --seed 5003 --genome-seed 19 `
  --out artifacts/tmp_cf_steps.json
```

`artifacts/tmp_*.json` paths are suggestions; create folders as needed or omit `--export-replay-dir`.

## 4. ε-sweep (many panic or β values, one genome + seed)

```powershell
python scripts/counterfactual_epsilon_sweep.py `
  --axis base_panic `
  --values "0.05,0.1,0.15,0.2" `
  --nodes 14 --horizon 12 `
  --rollout-seed 6001 --genome-seed 77 `
  --out artifacts/tmp_sweep_panic.json
```

Contagion β sweep (fixed reset panic):

```powershell
python scripts/counterfactual_epsilon_sweep.py `
  --axis contagion_beta `
  --values "0.08,0.22,0.4" `
  --base-panic 0.06 `
  --nodes 14 --horizon 12 `
  --out artifacts/tmp_sweep_beta.json
```

Schema: `counterfactual-epsilon-sweep-v1` (`fragility_engine.explain.sweep`). Plot axis vs integral instability: `python scripts/plot_epsilon_sweep.py <sweep.json> --out sweep.png`.

## 5. Aggregate **initial_panic** sweep + linear trace

```powershell
python scripts/counterfactual_epsilon_sweep.py `
  --mode aggregate --axis initial_panic `
  --values "0.04,0.07,0.11" `
  --horizon 14 --rollout-seed 6100 --genome-seed 88 `
  --emit-trace `
  --out artifacts/tmp_sweep_agg.json
```

`--emit-trace` adds **`explanation-trace-v1`**: a path graph linking consecutive runs with `delta_integral_instability` / `delta_attack_cost` (mechanical, not causal identification).

## 6. Neighbor-list **edge weight** counterfactual + merged attribution

Directed edge **0 → 1** on list topology `[[1],[0]]` — bump only that out-edge weight on the counterfactual clone (baseline keeps implicit uniform weights when weights JSON is omitted):

```powershell
python scripts/export_counterfactual.py `
  --mode network --neighbor-json artifacts/tmp_nl.json --horizon 10 `
  --intervention edge_weight_shift `
  --edge-from 0 --edge-to 1 --variant-edge-weight 4.0 `
  --base-panic 0.06 --seed 7201 --genome-seed 40 `
  --out artifacts/tmp_cf_edgew.json
```

ε-sweep several weights on the same edge (still fixed genome + rollout seed):

```powershell
python scripts/counterfactual_epsilon_sweep.py `
  --axis edge_weight --values "0.3,1.0,5.0" `
  --neighbor-json artifacts/tmp_nl.json --edge-from 0 --edge-to 1 `
  --horizon 10 --rollout-seed 7301 --genome-seed 41 `
  --out artifacts/tmp_sweep_edgew.json
```

Merge two or more **`export_counterfactual`** JSON files into one star-shaped **`attribution-merge-v1`** (baseline snapshots must agree unless `--no-strict-baseline`):

```powershell
python scripts/merge_counterfactual_attribution.py `
  --inputs artifacts/tmp_cf_panic.json artifacts/tmp_cf_edgew.json `
  --out artifacts/tmp_merge_attr.json
```

## 7. **Ordered mutation chain** (cumulative physics on one clone)

Chain spec JSON (`network-mutation-chain-spec-v1`): steps run in order on a template clone; the counterfactual rollout uses the **final** clone vs the **original** template (same genome + rollout seed). Include **`edge_weight`** steps only with **`--neighbor-json`**.

Example spec file `artifacts/tmp_chain.json`:

```json
{
  "schema": "network-mutation-chain-spec-v1",
  "steps": [
    {"kind": "contagion_beta", "value": 0.18},
    {"kind": "edge_weight", "from": 0, "to": 1, "weight": 4.5}
  ]
}
```

```powershell
python scripts/export_counterfactual_chain.py `
  --chain-json artifacts/tmp_chain.json `
  --neighbor-json artifacts/tmp_nl.json `
  --horizon 10 --base-panic 0.06 --seed 7401 --genome-seed 52 `
  --out artifacts/tmp_cf_chain.json
```

Optional **`--variant-base-panic`** sets reset panic for the **final** rollout when the chain has **no** `base_panic` steps.

**Multi-knob reset panic:** add a chain step `{"kind": "base_panic", "value": 0.14}` (topology unchanged). Steps apply in order; the final rollout uses the **last** `base_panic` step value. Example: [`tests/fixtures/chains/network_contagion_base_panic_chain.json`](../tests/fixtures/chains/network_contagion_base_panic_chain.json).

**Path trace** (one rollout per cumulative prefix; schema **`explanation-mutation-chain-path-v1`**):

```powershell
python scripts/export_counterfactual_chain.py `
  --chain-json artifacts/tmp_chain.json `
  --neighbor-json artifacts/tmp_nl.json `
  --horizon 10 --seed 7402 --genome-seed 53 `
  --emit-path-trace `
  --out artifacts/tmp_cf_chain_trace.json
```

Intermediate nodes use baseline panic unless a prior `base_panic` step updated it; the final node uses the last `base_panic` step or **`--variant-base-panic`** when no `base_panic` steps exist (edges record `reset_panic_from` / `reset_panic_to`).
