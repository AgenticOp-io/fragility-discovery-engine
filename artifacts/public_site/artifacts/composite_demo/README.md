# Institutional composite demo (bundled JSON)

**Not** a replay/Pareto timeline — use **`artifacts/composite_viewer/index.html`** (HTTP presets) or **`scripts/narrate_frozen_json.py`** for human-readable summaries.

Bundled samples: **v2 triple** (`sample_triple_composite.json`) and **v3 quad** (`sample_quad_composite.json`) — same shock schedule on decoupled kernels (no cross-world coupling in `step()`).

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
