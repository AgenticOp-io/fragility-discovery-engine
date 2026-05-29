# Public demo guide

This page describes the **browser workbench** on the **GCE demo server** (primary). A static mirror may exist on GitHub Pages; use GCE for runs and live validation. Everything you open in the viewers is **JSON already on the server** — you do not upload files in the demo.

## How the demo is organized

| Area | URL | What it does |
|------|-----|----------------|
| **Workbench** | `/` | Index of server-hosted samples and links into viewers |
| **Run a scenario** | `/run.html` | Starts a capped GA or co-evolution job; results land under `/runs/<id>/` |
| **Past runs** | `/runs.html` | Lists completed server runs |
| **Guided tour** | `/?tour=1` or `/tour.html` | Walkthrough across replay, attribution, fork, and Pareto |
| **Documentation** | `/docs/` | Install, tutorials, architecture, reference |
| **This host** | `/host.html` | Validation snapshot (`/status.json`) and engine health |

## Viewers (server data only)

Each viewer loads artifacts with **Presets** (dropdown) or a **hash link** from the workbench, for example:

`/artifacts/replay_viewer/index.html#src=sample_replay.json`

| Viewer | Typical JSON | Use when you want to… |
|--------|----------------|------------------------|
| [Replay](/artifacts/replay_viewer/index.html) | `best_replay.json`, `sample_*_replay.json` | Scrub a step-by-step collapse timeline |
| [Pareto](/artifacts/pareto_viewer/index.html) | `pareto_front.json`, `sample_pareto_*.json` | See cost vs severity trade-offs |
| [Attribution](/artifacts/attribution_viewer/index.html) | counterfactual / merge / chain JSON | Compare baseline vs intervention paths |
| [Composite](/artifacts/composite_viewer/index.html) | `sample_*_composite.json` | Same attack genome across multiple domains |
| [Coupling sweep](/artifacts/coupling_sweep_viewer/index.html) | `coupling_strength_sweep.json` | Research fork: coupling vs instability |
| [Coupling compare](/artifacts/coupling_comparison_viewer/index.html) | `sample_coupling_comparison.json` | Research fork: two coupling levels, same schedule |

On the **public demo**, local file pickers and drag-and-drop are **disabled**. Use presets or workbench links. For local file workflows, clone the repo and open the same viewer HTML from `artifacts/` on your machine.

## Running a new scenario on the server

1. Open [Run a scenario](/run.html).
2. Pick **domain and search type** (single-domain replay search vs attacker/defender co-evolution).
3. Set seed, horizon (if shown), generations, and population within server caps.
4. Submit — when finished, links open the replay or Pareto viewer against `/runs/<id>/…`.

Outputs are written only on the server (`/var/www/fragility/public/runs/` on GCE). Nothing is read from your computer.

## Six charter domains vs research fork

**Charter domains** (aggregate peg, network, resource cascade, service backlog, liquidity ladder, inventory buffer) are the reference workbench. Samples live under `/artifacts/pareto_viewer/`, `/artifacts/replay_viewer/`, etc.

**Coupled institution** is a **research fork** (`forks/coupled_institution/`): peg panic and overload exchange signals inside one simulation step. Fork samples are tagged on the workbench and documented in [Coupled fork (research)](/docs/fork-coupling.html).

## Suggested first visit

1. Workbench → **Flagship benchmark replay** (collapse timeline).
2. **Run a scenario** → aggregate peg, default caps → open your run in the replay viewer.
3. **Guided tour** from the workbench hero (voice optional).
4. **Attribution** sample “What caused the collapse?” for counterfactual chains.
5. Optional: coupled fork replay + Pareto from the **Research fork** section on the workbench.

## Operators

- Validation: `/status.json` and `/host.html`
- Republish GCE: `powershell -File scripts/gce_deploy_public_site.ps1`
- Optional static mirror: `powershell -File scripts/deploy_github_pages.ps1` (not used for testing)
