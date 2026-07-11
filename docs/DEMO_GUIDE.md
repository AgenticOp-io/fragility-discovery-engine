# Public demo guide

The demo is at **http://34.61.255.147/** (Fragility workbench on the same VM as https://hub.agenticop.io/). Everything is server-hosted — you open samples in the browser; nothing is uploaded from your computer.

**Guardrails:** the public site is **browse-first**. Bundled samples and viewers are open. Live **Run a scenario** requires an operator API key (or install locally: `pip install fragility-engine`). See [Demo guardrails](/docs/gce-https-and-auth.html).

---

## Pages at a glance

| Page | URL | What to do here |
|------|-----|-----------------|
| **Workbench** | `/` | Browse server-hosted samples and open them in viewers |
| **Run a scenario** | `/run.html` | Operator-gated live search (API key) — or use local CLI |
| **Past runs** | `/runs.html` | See completed server runs and open their results |
| **Guided tour** | `/?tour=1` | Step-by-step walkthrough with written explanations |
| **Documentation** | `/docs/` | Full manual |
| **This host** | `/host.html` | Validation snapshot and engine health |

---

## Viewers

Click any sample row on the workbench to open the right viewer. You can also use the **Presets** dropdown inside each viewer.

| Viewer | Opens | What you see |
|--------|-------|--------------|
| [Replay](/artifacts/replay_viewer/index.html) | Replay JSON | Step-by-step collapse timeline |
| [Pareto](/artifacts/pareto_viewer/index.html) | Pareto JSON | Cost vs severity trade-off chart |
| [Attribution](/artifacts/attribution_viewer/index.html) | Counterfactual / chain JSON | Which steps caused the outcome |
| [Composite](/artifacts/composite_viewer/index.html) | Composite JSON | Same attack across multiple domains |
| [Coupling sweep](/artifacts/coupling_sweep_viewer/index.html) | Sweep JSON | Research fork: coupling strength vs instability |
| [Coupling compare](/artifacts/coupling_comparison_viewer/index.html) | Comparison JSON | Research fork: two coupling levels compared |

Local file pickers and drag-and-drop are **disabled on this demo**. Use the Presets menu or the workbench links. To load your own files, clone the repo and open the viewers from `artifacts/` on a local server.

---

## Running a new scenario

Live runs on the **public** demo need an operator **run API key**. Without it, use bundled samples or install locally:

```powershell
pip install fragility-engine
fragility search --example capacity-pool
```

If you have a key:

1. Go to [Run a scenario](/run.html) (or `?run_key=…` once).
2. Choose a **domain and search type** from the dropdown.
3. Set the seed, horizon, generations, and population (within server limits).
4. Click **Run scenario**. When the job finishes, links appear to the replay or Pareto viewer.

Results are saved on the server under `/runs/<id>/`. Nothing on your computer is read or modified.

**Server limits:** max 150s · 1 concurrent run · 3 runs/hour/IP · anonymous runs off by default.

---

## Six charter domains vs the research fork

**Charter domains** (aggregate peg, network contagion, resource cascade, service backlog, liquidity ladder, inventory buffer) are the stable reference workbench.

**Coupled institution** is a research fork: peg panic and overload exchange signals inside one simulation step. It has its own sample section on the workbench and is documented in [Coupled fork (research)](/docs/fork-coupling.html).

---

## Suggested first visit

1. Workbench → click **Flagship benchmark** replay to see a collapse timeline.
2. Open any **Attribution** sample to see a counterfactual chain (no live run needed).
3. Optional: work through the [Guided tour](/?tour=1) — read each step, then press Next.
4. For a fresh search: install locally or ask an operator for a run key.

---

## For operators

- Check validation: `/status.json` and `/host.html`
- Deploy updated site from local machine: `powershell -File scripts/gce_deploy_public_site.ps1`
- Optional static mirror: `powershell -File scripts/deploy_github_pages.ps1`
