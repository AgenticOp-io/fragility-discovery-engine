# Resource cascade — counterfactual & sweep cookbook

Phase J domain: [`phase_j_resource_cascade.md`](phase_j_resource_cascade.md). Same attacker genome encoding as aggregate/network; physics differs (capacity + overload).

## 1. Shock removal (`remove_steps`)

Same pattern as aggregate: zero selected schedule rows; overload at reset is pinned by `--initial-overload`.

```bash
python scripts/export_counterfactual.py --mode resource_cascade --out cf_rc_remove.json \
  --horizon 14 --remove "0,1" --seed 101 --genome-seed 102 --initial-overload 0.07 \
  --export-replay-dir ./tmp_rc_pair
```

## 2. Initial overload shift

Same genome + rollout seed; only reset overload changes.

```bash
python scripts/export_counterfactual.py --mode resource_cascade \
  --intervention initial_overload_shift \
  --initial-overload 0.06 --variant-initial-overload 0.14 \
  --horizon 12 --seed 201 --genome-seed 202 --out cf_rc_io.json
```

## 3. Cascade coupling shift (physics clone)

Baseline uses the default template coupling; counterfactual uses `clone_resource_cascade` with `--variant-cascade-coupling`.

```bash
python scripts/export_counterfactual.py --mode resource_cascade \
  --intervention cascade_coupling_shift \
  --variant-cascade-coupling 0.42 \
  --initial-overload 0.065 --horizon 12 --seed 301 --genome-seed 302 --out cf_rc_cc.json
```

## 4. Joint star-merge (two branches, one baseline)

Combines **remove_steps** + a second branch into `attribution-merge-v1` (open in `artifacts/attribution_viewer/index.html`). Default second branch is **initial_overload_shift**; use **`--second-branch cascade_coupling_shift`** for a physics clone branch.

```bash
python scripts/export_resource_cascade_joint_attribution.py --out merge_rc.json \
  --horizon 11 --seed 401 --genome-seed 402 --initial-overload 0.07 \
  --variant-initial-overload 0.12 --remove "0"

python scripts/export_resource_cascade_joint_attribution.py --out merge_rc_cc.json \
  --second-branch cascade_coupling_shift --variant-cascade-coupling 0.42 \
  --horizon 11 --seed 403 --genome-seed 404 --initial-overload 0.07 --remove "0"
```

## 5. ε-sweep on `initial_overload`

```bash
python scripts/counterfactual_epsilon_sweep.py --mode resource_cascade --axis initial_overload \
  --values "0.05,0.09,0.13" --horizon 11 --rollout-seed 501 --genome-seed 502 \
  --out sweep_rc.json --emit-trace
```

## 6. Narration + citation digest (Phase L hook)

Deterministic summary; `--cite-digest` adds SHA-256 of the **raw JSON bytes** and the resolved path.

```bash
python scripts/narrate_frozen_json.py artifacts/replay_viewer/sample_resource_cascade_replay.json --cite-digest
python scripts/narrate_frozen_json.py merge_rc.json --json-out narration.json --cite-digest
```

## 7. Compare two replays

`compare_replays.py` adds `metric_notes` reminding that `metrics.price` is **headroom** for `resource_cascade`, peg ratio for aggregate.

```bash
python scripts/compare_replays.py tmp_rc_pair/baseline.json tmp_rc_pair/counterfactual.json
```
