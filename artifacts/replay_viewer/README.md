# Replay viewer (`index.html`)

**Loads:** rollout JSON from `runner.rollout_to_replay_dict` (and CLIs that wrap it): `schema_version`, `trajectory`, `events_lane`, `meta`, …

**Use a different surface** (this page will not chart them correctly):

| Kind | Example schema / artifact | Where |
|------|---------------------------|--------|
| Institutional composite | `fragility-institutional-composite-v1`, `v2` | `institutional_composite_demo.py --out` |
| Robustness / GA sweeps | `fragility-robustness-*` | `fragility_robustness_sweep.py --json` |
| Pareto | `pareto_front.json`, `pareto-front-v1` | `artifacts/pareto_viewer/index.html` |

Samples and preset workflow: hint block in `index.html`; pointers in repo [`README.md`](../../README.md).
