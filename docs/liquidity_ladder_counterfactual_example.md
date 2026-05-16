# Liquidity ladder counterfactual example (Phase N)

## Scalar shift

```bash
python scripts/export_counterfactual.py \
  --mode liquidity_ladder \
  --intervention initial_margin_shift \
  --initial-margin 0.06 \
  --variant-initial-margin 0.12 \
  --horizon 14 --seed 424243 --out /tmp/ll_margin.json
```

## ε-sweep

```bash
python scripts/counterfactual_epsilon_sweep.py \
  --mode liquidity_ladder \
  --axis initial_margin \
  --values 0.04,0.06,0.08,0.10 \
  --rollout-seed 42424 --horizon 14 --out /tmp/ll_sweep.json
```

## Mutation chain

Fixture: `tests/fixtures/chains/liquidity_ladder_margin_haircut_chain.json`

```bash
python scripts/export_liquidity_ladder_counterfactual_chain.py \
  --chain-json tests/fixtures/chains/liquidity_ladder_margin_haircut_chain.json \
  --initial-margin 0.065 --emit-path-trace \
  --horizon 10 --seed 66801 --genome-seed 66802 \
  --out artifacts/attribution_viewer/sample_liquidity_ladder_chain_margin_haircut.json
```

Bundled sample regenerates with `python scripts/regenerate_bundled_viewer_samples.py`.
