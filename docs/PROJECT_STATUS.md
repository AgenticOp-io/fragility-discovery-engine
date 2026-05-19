# Project status (charter scope)

**Last updated:** 2026-05-19 · **`main`** · release **[v0.4.0](https://github.com/AgenticOp-io/fragility-discovery-engine/releases/tag/v0.4.0)**

## Charter complete

Phases **H–N** and **L** publication tooling described in [`BOUNDARIES.md`](../BOUNDARIES.md) are **shipped** on `main`:

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
| **Release artifacts** | GitHub Release **v0.4.0** wheel + sdist; [`scripts/install_release.sh`](../scripts/install_release.sh) / [`.ps1`](../scripts/install_release.ps1) |

**Verification** (venv activated):

```bash
bash scripts/ci_local.sh          # Linux / macOS / WSL
# or
powershell -NoProfile -File scripts/ci_local.ps1   # Windows
```

Optional wheel smoke: `FRAGILITY_CI_LOCAL_BUILD=1` before `ci_local`.

**Install a tagged release** (no PyPI): see [`RELEASING.md`](../RELEASING.md) or `bash scripts/install_release.sh v0.4.0`.

## Explicitly out of scope (by design)

- **Coupled multi-kernel physics** in one `World.step()` — [`FORK_COUPLING_RESEARCH.md`](FORK_COUPLING_RESEARCH.md).
- **Fifth reference domain** — charter closed; [`BOUNDARIES.md`](../BOUNDARIES.md) “Future charter slots”.
- **Production dashboards, live market feeds, regulatory certification claims**.
- **LLM-driven simulation policy** inside rollouts.

## Optional follow-on (not charter blockers)

Aspirational items live in [`ROADMAP_NEXT.md`](../ROADMAP_NEXT.md) (larger grids, coupled forks, dashboards). Open a **new phase** in `BOUNDARIES.md` before expanding physics or bundle count.
