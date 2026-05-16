# Flagship demo (bundled, checked in)

Small GA run for static viewers and narration smoke tests. Regenerate:

```bash
python scripts/regenerate_bundled_viewer_samples.py
```

Or only flagship (faster):

```bash
python scripts/run_flagship_demo.py --out-dir artifacts/flagship/bundled --skip-validate --generations 2 --population-size 8 --horizon 10
```

Open **`artifacts/replay_viewer/index.html`** or **`artifacts/pareto_viewer/index.html`** over HTTP and pick the **Flagship bundled** preset.
