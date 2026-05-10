# Flagship demo output (local)

Generated files live under **`output/`** (gitignored). Regenerate:

```powershell
python scripts/run_flagship_demo.py --out-dir artifacts/flagship/output
```

For a fast smoke without Phase H validation first:

```powershell
python scripts/run_flagship_demo.py --out-dir artifacts/flagship/output --skip-validate
```

Then open `artifacts/replay_viewer/index.html` and load `best_replay.json`, and `artifacts/pareto_viewer/index.html` for `pareto_front.json`. Citation fields are in `fragility_certificate.json` (`fragility-certificate-v1`).

Full reviewer path: [`docs/PAPER_APPENDIX_WORKFLOW.md`](../docs/PAPER_APPENDIX_WORKFLOW.md).
