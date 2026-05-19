# Project status (charter scope)

**Last updated:** 2026-05-19 (branch `cursor/stable-manifest-summary-digest`)

## Charter complete

Phases **H–N** and **L** publication tooling described in [`BOUNDARIES.md`](../BOUNDARIES.md) are **shipped** for this repository:

| Area | Status |
|------|--------|
| **Frozen benchmark harness** (6 bundles, golden metrics, manifest v2, validate CLI) | Shipped |
| **Metric regression floors** (integral, attack_cost, collapsed expect) | Shipped |
| **Five reference domains** (aggregate, network, resource_cascade, service_backlog, liquidity_ladder) | Shipped |
| **Explanation grammar** (counterfactuals, ε-sweeps, merges, chains, path traces) | Shipped per domain |
| **Search parity** (MC, GA, Pareto, co-evolution, bench-search, eval_workers / eval_pool on bundles) | Shipped |
| **Institutional composite** (twin → penta, schema **v4**) | Shipped |
| **Narration + LLM prompt packs + plot CLIs** | Shipped (deterministic narration; LLM export only) |
| **Bundled viewer samples + preset validation** | Shipped |
| **Local / scheduled CI parity** | Shipped (`ci_local.*`, `.github/workflows/schedule.yml`) |
| **CLI subprocess smokes** | 110+ slices; full suite **471** tests (3 skipped) |

**Verification command** (venv activated):

```bash
bash scripts/ci_local.sh          # Linux / macOS / WSL
# or
powershell -NoProfile -File scripts/ci_local.ps1   # Windows
```

Optional wheel smoke: `FRAGILITY_CI_LOCAL_BUILD=1` before `ci_local`.

## Explicitly out of scope (by design)

- **Coupled multi-kernel physics** in one `World.step()` — see [`FORK_COUPLING_RESEARCH.md`](FORK_COUPLING_RESEARCH.md).
- **Fifth reference domain** — charter closed; see [`BOUNDARIES.md`](../BOUNDARIES.md) “Future charter slots”.
- **Production dashboards, live market feeds, regulatory certification claims**.
- **LLM-driven simulation policy** inside rollouts.

## Stretch / fork work (optional, not blocking “done”)

Tracked aspirationally in [`ROADMAP_NEXT.md`](../ROADMAP_NEXT.md): larger robustness grids, mechanism-design theory, coupled-institution forks, richer dashboards. None of these are required for the current charter exit.

## Merge checklist

1. Open PR: `cursor/stable-manifest-summary-digest` → `main`.
2. Confirm CI green on Ubuntu + Windows matrix.
3. Tag release per [`RELEASING.md`](../RELEASING.md) if publishing **0.4.0** artifacts.
