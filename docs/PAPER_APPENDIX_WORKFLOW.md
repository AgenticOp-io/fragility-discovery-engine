# Paper-appendix workflow (CLI-oriented, for citations)

This is a **single path** from frozen bundles → search → replay → Pareto → optional counterfactuals → citation JSON. It follows the project rule: **ship versioned JSON and tests before building a product UI** ([`BOUNDARIES.md`](../BOUNDARIES.md); internal shorthand: “evidence before chrome”).

**Broader operator guide** (install, tutorials, artifact map, static viewers): [`HOW_TO_USE.md`](HOW_TO_USE.md).

**Third reference domain (Phase M — shipped):** [`phase_m_third_reference_domain.md`](phase_m_third_reference_domain.md) (`ServiceBacklogWorld`).

## 0. One-command flagship bundle (synthetic aggregate)

Produces `best_replay.json`, `pareto_front.json`, `fragility_certificate.json`, and a short index file:

```powershell
pip install -e ".[dev]"
python scripts/run_flagship_demo.py --out-dir artifacts/flagship/output
```

Use `--skip-validate` only for quick local iteration; for anything you might cite, **drop that flag** so frozen benchmark validation (the Phase H gate in `BOUNDARIES.md`) runs first.

## 1. Phase H regression gate (optional but recommended before claims)

Run the frozen benchmark bundles (same checks as CI) before you treat outputs as cite-ready. New to the word **Phase** in filenames and headings? See [How to read “Phase” labels](../BOUNDARIES.md#how-to-read-phase-labels) in `BOUNDARIES.md`.

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

Network / resource-cascade / service-backlog / inventory-buffer cookbooks: [`network_counterfactual_example.md`](network_counterfactual_example.md), [`resource_cascade_counterfactual_example.md`](resource_cascade_counterfactual_example.md), [`service_backlog_counterfactual_example.md`](service_backlog_counterfactual_example.md), [`inventory_buffer_counterfactual_example.md`](inventory_buffer_counterfactual_example.md).

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

### 5b. Research fork digests (two-scalar + tetra)

When the coupled fork is present, refresh or export with research-fork blocks:

```powershell
python scripts/refresh_flagship_bundled_certificate.py
# or fork-only:
python scripts/export_coupled_fork_certificate.py --out artifacts/coupled_fork_demo/fork_certificate.json
```

Cite these fields alongside the main charter certificate:

- `research_fork_validation.bundle_id` → `coupled_institution_rollout_v1`
- `research_fork_validation.tetra_bundle_id` → `coupled_institution_tetra_rollout_v1`
- `research_fork_artifact_sha256` → includes two-scalar samples **plus** `sample_coupled_tetra_replay.json`, `sample_coupled_pareto_tetra.json`, and `worth_it_bar.json`

Pinned tetra search (GA/MC): `python scripts/check_coupled_fork_tetra_search.py`.

## 6. Narration + LLM prompt packs (Phase L)

```powershell
python scripts/narrate_frozen_json.py artifacts/flagship/output/best_replay.json --cite-digest --json-out narration.json
python scripts/export_llm_narration_prompt.py --prompt-pack paper_appendix_v1 --out prompts.json
```

## 7. Figures (optional `matplotlib`)

`scripts/plot_replay_timeline.py`, `plot_pareto_front.py`, `plot_counterfactual_bars.py` — see [`phase_l_publication.md`](phase_l_publication.md).

---

**What we still do *not* claim:** calibrated forecasts of real institutions, legal/compliance certification, or causal identification beyond the explicit counterfactual vocabulary — see [`BOUNDARIES.md`](../BOUNDARIES.md).
