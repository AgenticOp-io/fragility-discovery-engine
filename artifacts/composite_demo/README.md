# Institutional composite demo (bundled JSON)

**Not** a replay/Pareto viewer artifact — use **`scripts/narrate_frozen_json.py`** for human-readable summaries.

Bundled quad composite (`fragility-institutional-composite-v3`): same shock schedule on four decoupled kernels (aggregate peg, network, resource cascade, service backlog).

Regenerate:

```bash
python scripts/regenerate_bundled_viewer_samples.py
```

Or only the composite file:

```bash
python scripts/institutional_composite_demo.py --quad --horizon 10 --out artifacts/composite_demo/sample_quad_composite.json
```

```bash
python scripts/narrate_frozen_json.py artifacts/composite_demo/sample_quad_composite.json
```
