# Institutional composite viewer

Static HTML UI for **`fragility-institutional-composite-v1` / v2 / v3** JSON (decoupled branch metrics — not replay timelines).

## Use

From repo root:

```bash
python -m http.server 8765
```

Open `http://localhost:8765/artifacts/composite_viewer/index.html` and pick a preset or load JSON.

Bundled quad sample: `artifacts/composite_demo/sample_quad_composite.json` (regenerate via `scripts/regenerate_bundled_viewer_samples.py`).

## Related

- Narration: `scripts/narrate_frozen_json.py`
- Bar chart: `scripts/plot_institutional_composite_bars.py`
- Generator: `scripts/institutional_composite_demo.py`
