# Inventory buffer — counterfactual & mutation-chain cookbook

Sixth reference domain: [`WHY_INVENTORY_BUFFER.md`](WHY_INVENTORY_BUFFER.md). Physics is normalized stock under demand spikes and fulfillment erosion.

## 1. Shock removal (`remove_steps`)

```bash
python scripts/export_inventory_buffer_counterfactual_chain.py \
  --horizon 14 --seed 101 --genome-seed 102 --initial-stock 0.88 \
  --remove-timesteps 0,1,2 --out cf_ib_remove.json
```

## 2. Initial stock shift

```bash
python scripts/export_inventory_buffer_counterfactual_chain.py \
  --initial-stock 0.88 --variant-initial-stock 0.55 \
  --horizon 12 --seed 201 --genome-seed 202 --out cf_ib_stock.json
```

## 3. Demand-spike gain shift

```bash
python scripts/export_inventory_buffer_counterfactual_chain.py \
  --variant-demand-spike-gain 0.95 \
  --horizon 12 --seed 301 --genome-seed 302 --out cf_ib_demand.json
```

## 4. Cumulative mutation chain (path trace)

Fixture: `tests/fixtures/chains/inventory_buffer_demand_fulfillment_chain.json`

```bash
python scripts/export_inventory_buffer_mutation_chain.py \
  --chain-json tests/fixtures/chains/inventory_buffer_demand_fulfillment_chain.json \
  --initial-stock 0.86 --emit-path-trace \
  --horizon 12 --seed 401 --genome-seed 402 --out cf_ib_chain.json
```

Open `cf_ib_chain.json` in `artifacts/attribution_viewer/index.html`. Path trace schema: `explanation-mutation-chain-path-inventory-buffer-v1`.

## 5. Epsilon sweep on initial stock

```bash
python scripts/counterfactual_epsilon_sweep.py --mode inventory_buffer \
  --axis initial_stock --values 0.7,0.8,0.9,0.95 \
  --horizon 12 --rollout-seed 501 --out sweep_ib_stock.json
```

Regenerate bundled viewer sample: `python scripts/regenerate_bundled_viewer_samples.py`.
