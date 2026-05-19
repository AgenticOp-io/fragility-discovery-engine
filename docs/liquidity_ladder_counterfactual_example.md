# Liquidity ladder — counterfactual & sweep cookbook

Phase N domain: [`phase_n_liquidity_ladder.md`](phase_n_liquidity_ladder.md), motivation [`WHY_LIQUIDITY_LADDER.md`](WHY_LIQUIDITY_LADDER.md). Same attacker genome encoding as other reference worlds; physics is margin utilization vs ladder depth.

## 1. Shock removal (`remove_steps`)

Zero selected schedule rows; initial margin at reset is pinned by `--initial-margin`.

```bash
python scripts/export_counterfactual.py --mode liquidity_ladder --out cf_ll_remove.json \
  --horizon 14 --remove "0,1" --seed 101 --genome-seed 102 --initial-margin 0.07 \
  --export-replay-dir ./tmp_ll_pair
```

## 2. Initial margin shift

Same genome + rollout seed; only reset margin changes.

```bash
python scripts/export_counterfactual.py --mode liquidity_ladder \
  --intervention initial_margin_shift \
  --initial-margin 0.06 --variant-initial-margin 0.12 \
  --horizon 12 --seed 201 --genome-seed 202 --out cf_ll_margin.json
```

## 3. ε-sweep on initial margin

```bash
python scripts/counterfactual_epsilon_sweep.py \
  --mode liquidity_ladder \
  --axis initial_margin \
  --values 0.04,0.06,0.08,0.10 \
  --rollout-seed 42424 --horizon 14 --out cf_ll_sweep.json
```

Optional: `--emit-path-trace` when the sweep supports traces for your axis (see `--help`).

## 4. Mutation chain (ordered interventions)

Fixture: `tests/fixtures/chains/liquidity_ladder_margin_haircut_chain.json`

```bash
python scripts/export_liquidity_ladder_counterfactual_chain.py \
  --chain-json tests/fixtures/chains/liquidity_ladder_margin_haircut_chain.json \
  --initial-margin 0.065 --emit-path-trace \
  --horizon 10 --seed 66801 --genome-seed 66802 \
  --out artifacts/attribution_viewer/sample_liquidity_ladder_chain_margin_haircut.json
```

Open `artifacts/attribution_viewer/index.html` (serve repo root over HTTP) and load the bundled preset or your output file.

## 5. Single replay export (baseline trace)

```bash
python scripts/export_replay.py --mode liquidity_ladder \
  --initial-margin 0.07 --horizon 14 --seed 9001 --out ll_replay.json
```

## 6. Regenerate bundled viewer samples

```bash
python scripts/regenerate_bundled_viewer_samples.py
```

See [`BUNDLED_ARTIFACTS.md`](BUNDLED_ARTIFACTS.md) for the full checked-in file list.
