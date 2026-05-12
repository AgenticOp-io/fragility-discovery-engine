# Paper-appendix workflow (reviewer-grade, mostly CLI)

This is a **single path** from frozen bundles → search → replay → Pareto → optional counterfactuals → citation JSON. It matches the project charter: **audit-ready artifacts before product UI** ([`BOUNDARIES.md`](../BOUNDARIES.md) — “evidence before chrome”).

**Broader operator guide** (install, tutorials, artifact map, static viewers): [`HOW_TO_USE.md`](HOW_TO_USE.md).

**Third reference domain (Phase M — shipped):** [`phase_m_third_reference_domain.md`](phase_m_third_reference_domain.md) (`ServiceBacklogWorld`).

## 0. One-command flagship bundle (synthetic aggregate)

Produces `best_replay.json`, `pareto_front.json`, `fragility_certificate.json`, and a short index file:

```powershell
pip install -e ".[dev]"
python scripts/run_flagship_demo.py --out-dir artifacts/flagship/output
```

Use `--skip-validate` only for quick local iteration; for anything you might cite, **drop that flag** so Phase H golden validation runs first.

## 1. Phase H regression gate (optional but recommended before claims)

```powershell
python scripts/run_benchmark_suite.py --validate
```

JSON inventory (portable manifest):

```powershell
python scripts/run_benchmark_suite.py --manifest-out benchmark_manifest.json
```

## 2. Static viewers (no server)

- **Replay:** open `artifacts/replay_viewer/index.html` → load `artifacts/flagship/output/best_replay.json` (or any `replay.json` from `export_replay.py` / `run_ga_demo.py`).
- **Pareto:** open `artifacts/pareto_viewer/index.html` → load `pareto_front.json` from the flagship folder or `export_pareto_front.py`.

## 3. Greedy minimization (if the best schedule collapses)

```powershell
python scripts/export_minimized_replay.py --out minimized.json
```

(Uses its own defaults; pin seeds/horizon flags as for your study.)

## 4. Counterfactual export (aggregate example)

```powershell
python scripts/export_counterfactual.py --out cf.json --mode aggregate
```

Network / resource-cascade / service-backlog cookbooks: [`network_counterfactual_example.md`](network_counterfactual_example.md), [`resource_cascade_counterfactual_example.md`](resource_cascade_counterfactual_example.md), [`service_backlog_counterfactual_example.md`](service_backlog_counterfactual_example.md).

## 5. Citation bundle (`fragility-certificate-v1`)

After you have JSON artifacts to freeze:

```powershell
python scripts/export_fragility_certificate.py --out cite.json `
  --digest-json artifacts/flagship/output/best_replay.json artifacts/flagship/output/pareto_front.json `
  --validate-bundles
```

Or reuse the certificate embedded in the flagship folder. Fields that matter for prose:

- `git_commit`, `fragility_engine_version`, `python_version`, `numpy_version`
- `artifact_sha256` (per-file digests)
- `certificate_content_sha256` (hash of the JSON body **excluding** that field at generation time — stable for “this blob” citations)
- `benchmark_manifest` (bundle inventory + schema fingerprints)

## 6. Narration + LLM prompt packs (Phase L)

```powershell
python scripts/narrate_frozen_json.py artifacts/flagship/output/best_replay.json --cite-digest --json-out narration.json
python scripts/export_llm_narration_prompt.py --prompt-pack paper_appendix_v1 --out prompts.json
```

## 7. Figures (optional `matplotlib`)

`scripts/plot_replay_timeline.py`, `plot_pareto_front.py`, `plot_counterfactual_bars.py` — see [`phase_l_publication.md`](phase_l_publication.md).

---

**What we still do *not* claim:** calibrated forecasts of real institutions, legal/compliance certification, or causal identification beyond the explicit counterfactual vocabulary — see [`BOUNDARIES.md`](../BOUNDARIES.md).
