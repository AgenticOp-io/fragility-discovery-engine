# Replay viewer (`index.html`)

This static page expects **rollout replay JSON** produced by `runner.rollout_to_replay_dict` (and the export CLIs that wrap it): top-level `schema_version`, `trajectory`, `events_lane`, `meta`, etc.

**Not loadable here** (different contracts / UIs):

- **Institutional composite** — `fragility-institutional-composite-v1` / **`fragility-institutional-composite-v2`** from `scripts/institutional_composite_demo.py` (`--out`). Side-by-side **scalar summaries** per kernel (aggregate / network / resource cascade), not a per-timestep replay bundle. Inspect in a JSON tool or downstream analytics.
- **`fragility-robustness-*`** payloads from `scripts/fragility_robustness_sweep.py` — ensemble / sweep results.
- **`pareto_front.json`** / **`pareto-front-v1`** — use `artifacts/pareto_viewer/index.html`.

Bundled samples and preset paths are described in the on-page hint inside `index.html` and in the repo root [`README.md`](../../README.md).
