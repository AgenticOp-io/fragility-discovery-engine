# Service backlog — counterfactual & sweep cookbook

Phase M domain: [`phase_m_third_reference_domain.md`](phase_m_third_reference_domain.md), motivation [`WHY_SERVICE_BACKLOG.md`](WHY_SERVICE_BACKLOG.md). Same attacker genome encoding as other reference worlds; physics is backlog + slack.

## 1. Shock removal (`remove_steps`)

Zero selected schedule rows; initial backlog at reset is pinned by `--initial-backlog`.

```bash
python scripts/export_counterfactual.py --mode service_backlog --out cf_sb_remove.json \
  --horizon 14 --remove "0,1" --seed 101 --genome-seed 102 --initial-backlog 0.07 \
  --export-replay-dir ./tmp_sb_pair
```

## 2. Initial backlog shift

Same genome + rollout seed; only reset backlog changes.

```bash
python scripts/export_counterfactual.py --mode service_backlog \
  --intervention initial_backlog_shift \
  --initial-backlog 0.06 --variant-initial-backlog 0.14 \
  --horizon 12 --seed 201 --genome-seed 202 --out cf_sb_ib.json
```

## 3. Process rate shift (physics clone)

Baseline uses the template `process_rate`; counterfactual uses a cloned world with `--variant-process-rate`.

```bash
python scripts/export_counterfactual.py --mode service_backlog \
  --intervention process_rate_shift \
  --variant-process-rate 0.48 \
  --initial-backlog 0.065 --horizon 12 --seed 301 --genome-seed 302 --out cf_sb_pr.json
```

## 4. Joint star-merge (two branches, one baseline)

Combines **remove_steps** + a second branch into `attribution-merge-v1` (open in `artifacts/attribution_viewer/index.html`). Default second branch is **initial_backlog_shift**; use **`--second-branch process_rate_shift`** with **`--variant-process-rate`** for a physics clone branch.

```bash
python scripts/export_service_backlog_joint_attribution.py --out merge_sb.json \
  --horizon 11 --seed 401 --genome-seed 402 --initial-backlog 0.07 \
  --variant-initial-backlog 0.02 --remove "0"

python scripts/export_service_backlog_joint_attribution.py --out merge_sb_pr.json \
  --second-branch process_rate_shift --variant-process-rate 0.50 \
  --horizon 11 --seed 403 --genome-seed 404 --initial-backlog 0.07 --remove "0"
```

## 5. Cumulative mutation chain (`service-backlog-mutation-chain-spec-v1`)

Ordered physics knobs applied on a template clone; baseline vs final cumulative variant uses the same genome and rollout seed. Optional **`--emit-path-trace`** emits **`explanation-mutation-chain-path-service-backlog-v1`**.

Save a small chain spec as `chain_sb.json`:

```json
{
  "schema": "service-backlog-mutation-chain-spec-v1",
  "steps": [
    {"kind": "process_rate", "value": 0.42},
    {"kind": "ingest_gain", "value": 0.27}
  ]
}
```

```bash
python scripts/export_service_backlog_counterfactual_chain.py \
  --chain-json chain_sb.json --horizon 12 --seed 601 --genome-seed 602 \
  --initial-backlog 0.065 --variant-initial-backlog 0.10 \
  --emit-path-trace --out cf_sb_chain.json
```

## 6. ε-sweeps (`initial_backlog`, `process_rate`)

```bash
python scripts/counterfactual_epsilon_sweep.py --mode service_backlog --axis initial_backlog \
  --values "0.05,0.09,0.13" --horizon 11 --rollout-seed 501 --genome-seed 502 \
  --out sweep_sb.json --emit-trace

python scripts/plot_epsilon_sweep.py sweep_sb.json --out sweep_sb.png
```

## 7. Narration + citation digest (Phase L)

See [`docs/phase_l_publication.md`](phase_l_publication.md) for the full Phase L CLI index.

```bash
python scripts/narrate_frozen_json.py merge_sb.json --json-out narration.json --cite-digest
```

## Related

Resource cascade cookbook (parallel patterns): [`resource_cascade_counterfactual_example.md`](resource_cascade_counterfactual_example.md).
