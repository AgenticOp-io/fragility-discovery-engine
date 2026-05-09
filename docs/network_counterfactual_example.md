# Network counterfactual examples (Phase I)

All commands assume repo root and `pip install -e ".[dev]"`.

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

Schema: `counterfactual-epsilon-sweep-v1` (`fragility_engine.explain.sweep`).
