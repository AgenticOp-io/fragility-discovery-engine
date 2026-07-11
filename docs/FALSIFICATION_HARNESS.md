# Falsification harness (Phase S)

Adversarial search where **damage is an invariant predicate** and **reset** restores a known snapshot. See also the falsification section in [`BRING_YOUR_OWN_WORLD.md`](BRING_YOUR_OWN_WORLD.md).

## Contract

| World member | Falsification role |
|--------------|-------------------|
| `reset()` | Establish baseline corpus / state |
| `save_snapshot()` / `restore_snapshot()` | Optional fast reset between rollouts (`SnapshotMixin`) |
| `step(events, rng)` | One parameterized perturbation tick |
| `claim_violated()` | **Predicate** — `True` when the defended invariant breaks |
| `instability_score()` | Distance-to-violation heuristic (often 0/1) |

Replay JSON includes `meta.harness_kind = falsification_v1`.

## CLI

```powershell
pip install -e ".[dev]"
fragility falsify search --example ranked-store --export-replay artifacts/falsify_replay.json
```

Tutorial script: [`../examples/falsification_ranked_store.py`](../examples/falsification_ranked_store.py).

## Limits

- Search finds **presence** of failures, never **absence**.
- Snapshot restore per rollout can be expensive — budget rollouts accordingly (`docs/SCALE_AND_LIMITS.md`).
- Examples are generic tutorials, not charter reference domains.
