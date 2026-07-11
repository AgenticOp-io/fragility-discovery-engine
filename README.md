# Fragility Discovery Engine

**Agents / automated reviewers:** read [`AI_READ.md`](AI_READ.md) first (what this is, why it exists, how the loop works, common misreads).

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20455688.svg)](https://doi.org/10.5281/zenodo.20455688)

**Releases / git tags:** [`RELEASING.md`](RELEASING.md) · **Latest:** [v0.6.5](https://github.com/AgenticOp-io/fragility-discovery-engine/releases/tag/v0.6.5) (tetra certificate digests + workbench callouts; wheel on GitHub Releases) · **FEL / Zenodo:** [fel-v0.1.1](https://github.com/AgenticOp-io/fragility-discovery-engine/releases/tag/fel-v0.1.1) · **Citation:** [`CITATION.cff`](CITATION.cff) · **Coupled multi-kernel work (fork policy):** [`docs/FORK_COUPLING_RESEARCH.md`](docs/FORK_COUPLING_RESEARCH.md) · **New minimal GCE VM:** [`docs/GCE_BOOTSTRAP.md`](docs/GCE_BOOTSTRAP.md)

**Directed search** (Monte Carlo and **genetic algorithms**) over modular discrete-time simulations — or **your own world** via [`docs/BRING_YOUR_OWN_WORLD.md`](docs/BRING_YOUR_OWN_WORLD.md). Export replay JSON, minimized failing schedules, and counterfactual attribution bundles.

**Install + BYOW CLI (v0.6.5):**

```powershell
pip install fragility-engine
# or: pip install -e ".[dev]"
fragility search --example capacity-pool
fragility minimize --example capacity-pool
fragility falsify search --example ranked-store
fragility shorthand list
fragility certify
```

**Public demo** (browse-first; live runs are API-key gated): https://fragility.agenticop.io/ (IP fallback: http://34.61.255.147/) · Chrysalis hub: https://hub.agenticop.io/ · [vhost plan](docs/HOSTNAME_MAP.md) · [guardrails](docs/GCE_HTTPS_AND_AUTH.md)

**Documentation hub:** [`docs/README.md`](docs/README.md) — index by role (user, contributor, reviewer). **Hands-on guide:** [`docs/HOW_TO_USE.md`](docs/HOW_TO_USE.md) · **Architecture / reference:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/REFERENCE.md`](docs/REFERENCE.md) · **After clone:** [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md) · **Install / Git:** [`docs/INSTALLATION.md`](docs/INSTALLATION.md) · **Whitepaper:** [`docs/WHITEPAPER.md`](docs/WHITEPAPER.md)

## Supported platforms

**Validation:** run tests on **Windows** (`powershell -File scripts/ci_local.ps1`) or **GCE** (`bash scripts/gce_pull_and_test.sh` on the VM). GitHub Actions CI runs on **push/PR to `main`** and via `workflow_dispatch`.

## Cite

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20455688.svg)](https://doi.org/10.5281/zenodo.20455688)

- **Concept DOI (latest):** [10.5281/zenodo.20455688](https://doi.org/10.5281/zenodo.20455688)
- **v0.6.5 version:** [10.5281/zenodo.21313024](https://doi.org/10.5281/zenodo.21313024)
- **v0.6.4 version:** [10.5281/zenodo.21312735](https://doi.org/10.5281/zenodo.21312735)
- **v0.6.3 version:** [10.5281/zenodo.21312495](https://doi.org/10.5281/zenodo.21312495)
- **v0.6.2 version:** [10.5281/zenodo.21304265](https://doi.org/10.5281/zenodo.21304265)
- **v0.6.1 version:** [10.5281/zenodo.21304131](https://doi.org/10.5281/zenodo.21304131)
- **v0.6.0 version:** [10.5281/zenodo.21303841](https://doi.org/10.5281/zenodo.21303841)
- **FEL snapshot:** [10.5281/zenodo.20455689](https://doi.org/10.5281/zenodo.20455689) (`fel-v0.1.1`)
- **Machine-readable:** [`CITATION.cff`](CITATION.cff)
- **Preprint:** [`docs/preprint/FEL_preprint_v0.1.md`](docs/preprint/FEL_preprint_v0.1.md)
- **Repro bundle:** `fragility certify` or `python scripts/run_flagship_demo.py`
- **Install:** `pip install fragility-engine` · [PyPI](https://pypi.org/project/fragility-engine/) · [GitHub Release](https://github.com/AgenticOp-io/fragility-discovery-engine/releases/tag/v0.6.5)

```bibtex
@software{peterson2026fde,
  author = {David Peterson},
  title  = {Fragility Discovery Engine},
  year   = {2026},
  doi    = {10.5281/zenodo.20455688},
  url    = {https://doi.org/10.5281/zenodo.20455688}
}
```

## What this is / is not

| Is | Is not |
|----|--------|
| Deterministic stress-search **harness** + JSON evidence contracts | Calibrated model of any real institution |
| BYOW adapter for your steppable simulation | Drop-in prod risk engine |
| Counterfactual **re-run** attribution (FEL Δ conventions) | Causal identification / compliance sign-off |
| Six **toy oracles** for frozen regression CI | Seventh charter domain (closed) |

See [`BOUNDARIES.md`](BOUNDARIES.md) non-goals.

Build **sdist + wheel** locally with `python -m build` (or set `FRAGILITY_CI_LOCAL_BUILD=1` in `ci_local`). Core package code is pure Python; dependencies resolve via PyPI wheels (`numpy`, `networkx`, optional `numba`). Requires **CPython ≥ 3.11** ([`pyproject.toml`](pyproject.toml)).

## Layout (core Python packages)

| Layer | Role |
|--------|------|
| `fragility_engine.world` | Domain physics only — no attacker concepts. |
| `fragility_engine.agents` | Behavior archetypes — `observe → decide → act`. |
| `fragility_engine.adversary` | Deterministic search (Monte Carlo + GA) over shock schedules. |
| `fragility_engine.explain` | Ablation, schedule minimization, **counterfactual** bundles, mutation chains, sweeps. |
| `fragility_engine.network` | ``ContagionGraph`` + topology; contagion uses **neighbor lists** (**O(edges)** per step, dense adjacency storage unchanged). |
| `fragility_engine.coevolution` | Alternating attacker/defender search; aggregate + network + `alternating_coevolution_rollout` hook for custom worlds. |

The **numerical core** is **deterministic** (fixed NumPy RNG seeds). LLM policies stay out until the core loop is proven.

**Scope creep guardrail:** read [`BOUNDARIES.md`](BOUNDARIES.md) before adding agents, graph models, multi-objective fitness, UI, or defender loops.

**Where we go next (aspirational):** [`ROADMAP_NEXT.md`](ROADMAP_NEXT.md). Phases **Q → R → S** shipped at **v0.6.0**. **Normative gates:** [`BOUNDARIES.md`](BOUNDARIES.md). **Operator checklist:** [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md). **Agents:** [`AI_READ.md`](AI_READ.md).

**Phase J (second domain narrative):** [`docs/WHY_RESOURCE_CASCADE.md`](docs/WHY_RESOURCE_CASCADE.md) — why `ResourceCascadeWorld` exists and what we do *not* claim. Worked counterfactual commands: [`docs/resource_cascade_counterfactual_example.md`](docs/resource_cascade_counterfactual_example.md).

**Phase M (third domain narrative):** [`docs/WHY_SERVICE_BACKLOG.md`](docs/WHY_SERVICE_BACKLOG.md) — `ServiceBacklogWorld` + `simulation_mode` **`service_backlog`**; gate + replay table: [`docs/phase_m_third_reference_domain.md`](docs/phase_m_third_reference_domain.md). Counterfactual cookbook: [`docs/service_backlog_counterfactual_example.md`](docs/service_backlog_counterfactual_example.md).

**Phase N (fourth domain narrative):** [`docs/WHY_LIQUIDITY_LADDER.md`](docs/WHY_LIQUIDITY_LADDER.md) — `LiquidityLadderWorld` + `simulation_mode` **`liquidity_ladder`**; gate: [`docs/phase_n_liquidity_ladder.md`](docs/phase_n_liquidity_ladder.md). Counterfactual cookbook: [`docs/liquidity_ladder_counterfactual_example.md`](docs/liquidity_ladder_counterfactual_example.md).

**Phase O (sixth domain narrative):** [`docs/WHY_INVENTORY_BUFFER.md`](docs/WHY_INVENTORY_BUFFER.md) — `InventoryBufferWorld` + `simulation_mode` **`inventory_buffer`**; gate: [`docs/phase_o_stretch.md`](docs/phase_o_stretch.md). Counterfactual cookbook: [`docs/inventory_buffer_counterfactual_example.md`](docs/inventory_buffer_counterfactual_example.md).

**Toy-model scope:** all six reference worlds are deliberately simplified stress kernels — not calibrated to any real institution. See [`BOUNDARIES.md`](BOUNDARIES.md) non-goals and [`docs/AUDIT_RESOLUTION.md`](docs/AUDIT_RESOLUTION.md).

**Your system, not our toys:** the engine's value on a real problem comes from a world *you* write — a ~100-line adapter (`reset` / `step` / `state_vector` / `instability_score` / `is_collapsed`), after which search, minimization, attribution, and replay work unchanged. Tutorial + runnable example: [`docs/BRING_YOUR_OWN_WORLD.md`](docs/BRING_YOUR_OWN_WORLD.md), [`examples/bring_your_own_world.py`](examples/bring_your_own_world.py). Honest bar before you invest: the engine earns its keep only when the worst-case shock *ordering* is non-obvious — if the search merely rediscovers "everything at once is bad," it added nothing. The doc includes a one-day falsification test for exactly that.

**Reproducible benchmarks:** [`benchmarks/README.md`](benchmarks/README.md) — `python scripts/run_benchmark_suite.py --validate`. **Validation (Windows or GCE):** [`docs/INSTALLATION.md`](docs/INSTALLATION.md) — `pwsh -File scripts/ci_local.ps1` or `bash scripts/gce_pull_and_test.sh` on the VM.

**Paper-style walkthrough (one path):** [`docs/PAPER_APPENDIX_WORKFLOW.md`](docs/PAPER_APPENDIX_WORKFLOW.md) · **Scale / limits (honest):** [`docs/SCALE_AND_LIMITS.md`](docs/SCALE_AND_LIMITS.md) · **Citation JSON:** `fragility-certificate-v1` via `scripts/export_fragility_certificate.py` / `scripts/run_flagship_demo.py` · **Research frontiers (third domain, coupling):** [`docs/RESEARCH_FRONTIERS.md`](docs/RESEARCH_FRONTIERS.md).

## Quick start

Follow **[`docs/HOW_TO_USE.md`](docs/HOW_TO_USE.md)** for a full tutorial layout; the steps below match the Windows fast path.

**Windows — install CPython with winget** (avoids the Microsoft Store `python.exe` stubs). Requires **Python ≥ 3.11** ([`pyproject.toml`](pyproject.toml)):

```powershell
winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
```

Open a **new** terminal, then create a venv and install dev deps (use **`py -3.12`** if the launcher is on your `PATH`, or run **`python.exe`** from `%LocalAppData%\Programs\Python\` — e.g. `Python312-x64` on amd64):

```powershell
cd C:\Users\david\projects\fragility-discovery-engine
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
# Optional Numba (`pip install -e ".[accelerate]"`): on Windows on ARM, prefer **x64** CPython under emulation (`Python312-x64`) so wheels match; see `.\scripts\install_accelerate_windows.ps1` and docs/phase_k_acceleration.md.
# Tests: use ``python -m pytest`` (Linux/macOS/GCE/CI). Only Windows venvs expose ``pytest.exe``; that shim does not exist on Unix.
python -m pytest -q
python scripts/week1_smoke.py
python scripts/run_ga_demo.py
```

### Google Compute Engine (Linux VM)

Use a small **Debian/Ubuntu** instance when you want Linux CI parity or heavier `pytest` runs. **Prefer git clone/pull on the VM** instead of uploading tarballs from your laptop.

**One-shot deploy** (public `main`; installs Python 3.11+ via `apt` if needed, shallow clone, venv, editable install):

```bash
sudo apt-get update && sudo apt-get install -y git curl python3.11 python3.11-venv
curl -fsSL https://raw.githubusercontent.com/AgenticOp-io/fragility-discovery-engine/main/scripts/gce_git_deploy.sh | bash
```

**Private repo:** `raw.githubusercontent.com` will **404** — copy both scripts from your laptop, then SSH (see [`docs/GCE_DEPLOY_KEY.md`](docs/GCE_DEPLOY_KEY.md)):

```bash
gcloud compute scp scripts/gce_git_deploy.sh scripts/gce_remote_git_deploy.sh acs-hss-server:/tmp/ --zone=us-central1-a
gcloud compute ssh acs-hss-server --zone=us-central1-a --command='bash /tmp/gce_remote_git_deploy.sh'
```

Run tests after install:

```bash
curl -fsSL https://raw.githubusercontent.com/AgenticOp-io/fragility-discovery-engine/main/scripts/gce_git_deploy.sh | FRAGILITY_RUN_TESTS=1 bash
```

Or after the first clone: `FRAGILITY_RUN_TESTS=1 bash ~/fragility-discovery-engine/scripts/gce_git_deploy.sh`

**Updates:** rerun the script from anywhere — it **`git pull`s** when `~/fragility-discovery-engine` already exists.

**Private repo:** use a **deploy key** (recommended): [`docs/GCE_DEPLOY_KEY.md`](docs/GCE_DEPLOY_KEY.md) — generate with [`scripts/generate_gce_deploy_key.ps1`](scripts/generate_gce_deploy_key.ps1), add `.pub` on GitHub, copy private key to the VM, then set `FRAGILITY_REPO_URL` + `GIT_SSH_COMMAND` as documented.

Alternatives: SSH agent forwarding, or HTTPS + token (avoid logging tokens; prefer deploy keys).

Optional env: `FRAGILITY_DEPLOY_DIR`, `FRAGILITY_BRANCH`, `FRAGILITY_PYTHON`, `FRAGILITY_SHALLOW=0` for full history — see header in [`scripts/gce_git_deploy.sh`](scripts/gce_git_deploy.sh).

To have **Cursor** run **on the VM**, use **Remote - SSH** and open the deploy directory as the workspace.

**winget** is Windows-only; on the VM use **`apt`** as above.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/week1_smoke.py` | Deterministic rollout smoke (`--export-replay`, `--initial-panic`, `--continue-after-collapse`) |
| `scripts/run_mc_demo.py` | Monte Carlo random schedules (`--export-replay`, `--continue-after-collapse`) |
| `scripts/export_minimized_replay.py` | Random collapsing schedule → greedy minimization → replay JSON; optional **`--minimization-report-out`** (JSON for `export_explanation_dag.py`) |
| `scripts/export_explanation_dag.py` | **`explanation-dag-v1`** from **`--from-counterfactual`** or **`--from-minimization-report`** |
| `scripts/run_ga_demo.py` | GA + greedy minimization (`--export-replay`, `--export-minimized-replay`, `--generations`, `--population-size`, `--seed`) |
| `scripts/run_resource_cascade_ga_demo.py` | Phase **J** scaffold: GA + minimization on **`ResourceCascadeWorld`** (`--initial-overload`, same export flags); see [`docs/phase_j_resource_cascade.md`](docs/phase_j_resource_cascade.md) |
| `scripts/run_service_backlog_ga_demo.py` | Phase **M** third domain: GA + minimization on **`ServiceBacklogWorld`** (`--initial-backlog`, same export flags); see [`docs/phase_m_third_reference_domain.md`](docs/phase_m_third_reference_domain.md), [`docs/WHY_SERVICE_BACKLOG.md`](docs/WHY_SERVICE_BACKLOG.md) |
| `scripts/run_liquidity_ladder_ga_demo.py` | Phase **N** fourth domain: GA + minimization on **`LiquidityLadderWorld`** (`--initial-margin`, same export flags); see [`docs/phase_n_liquidity_ladder.md`](docs/phase_n_liquidity_ladder.md), [`docs/WHY_LIQUIDITY_LADDER.md`](docs/WHY_LIQUIDITY_LADDER.md) |
| `scripts/run_network_demo.py` | GA on **graph contagion** (`--graph-kind`, `--neighbor-json` / `--neighbor-weights-json`, `--export-replay`, sizing flags) |
| `scripts/export_replay.py` | `replay.json`: **`--mode aggregate|network|resource_cascade|service_backlog|liquidity_ladder|inventory_buffer`** (domain-specific reset flags — see `--help`) |
| `scripts/fragility_surface.py` | CSV fragility grid; `--panic-*`, `--depeg-*`, `integral_instability` column |
| `scripts/run_coevolution.py` | Alternating attacker/defender GA: `--mode aggregate|network|resource_cascade|service_backlog|liquidity_ladder`, **`--initial-overload`** (cascade) / **`--initial-backlog`** (backlog) / **`--initial-margin`** (liquidity), `--continue-after-collapse`, topology flags or `--neighbor-json`, `--collect-attacker-pareto`, **`--export-pareto-json`** (viewer-ready `pareto-front-v1`), `--json-summary`, `--export-replay` |
| `scripts/export_coevolution_pareto.py` | Convert `--json-summary` output → `pareto_front.json` (`--from-summary`, `--out`) |
| `scripts/export_pareto_front.py` | `pareto_front.json`; **`--mode aggregate|network|resource_cascade|service_backlog|liquidity_ladder`** (**`--initial-overload`** / **`--initial-backlog`** / **`--initial-margin`**); topology / `--neighbor-json` for network; GA sizing `--horizon`, `--generations`, `--population-size`; `--export-replay` (+ `--replay-pareto-index`) |
| `scripts/find_cheap_collapse.py` | Cost-penalized GA (`--export-replay`) |
| `scripts/export_counterfactual.py` | Attribution JSON; **`--mode aggregate|network|resource_cascade|service_backlog|liquidity_ladder`**; cascade: `remove_steps`, **`initial_overload_shift`**, **`cascade_coupling_shift`**; backlog: `remove_steps`, **`initial_backlog_shift`**, **`process_rate_shift`**; liquidity: `remove_steps`, **`initial_margin_shift`**, **`delever_rate_shift`**; network shifts (`base_panic_shift`, …); cookbooks in `docs/*_counterfactual_example.md` |
| `scripts/export_counterfactual_chain.py` | Ordered mutation chain counterfactual + optional **`--emit-path-trace`** (`explanation-mutation-chain-path-v1`) |
| `scripts/export_resource_cascade_counterfactual_chain.py` | Phase **J**: **`ResourceCascadeWorld`** cumulative physics chain (`resource-cascade-mutation-chain-spec-v1`) + optional **`--emit-path-trace`** (`explanation-mutation-chain-path-resource-cascade-v1`) |
| `scripts/export_liquidity_ladder_counterfactual_chain.py` | Phase **N**: **`LiquidityLadderWorld`** cumulative physics chain (`liquidity-ladder-mutation-chain-spec-v1`) + optional **`--emit-path-trace`** (`explanation-mutation-chain-path-liquidity-ladder-v1`) |
| `scripts/export_resource_cascade_joint_attribution.py` | **`attribution-merge-v1`**: shared-baseline **remove_steps** + **`--second-branch`** **initial_overload_shift** or **cascade_coupling_shift** |
| `scripts/narrate_frozen_json.py` | Phase **L**: replay / Pareto / merge / epsilon-sweep JSON; **`--cite-digest`**; **`--json-out`** → **`narration-summary-v1`** (core narration lives in **`fragility_engine.explain.narration`**) |
| `scripts/export_llm_narration_prompt.py` | Phase **L**: **`llm-prompt-bundle-v1`**; **`--prompt-pack`** `narration_v1` \| `reviewer_memo_v1` \| `paper_appendix_v1`; optional **`--invoke-openai`** **`--max-tokens`** |
| `scripts/plot_replay_timeline.py` | Replay: **`metrics.price`** / **`metrics.instability`** vs timestep; **`fragility-plot-style-v1`** |
| `scripts/plot_epsilon_sweep.py` | **`counterfactual-epsilon-sweep-v1`** curve + collapse markers; **`fragility-plot-epsilon-sweep-style-v1`** |
| `scripts/plot_pareto_front.py` | **`pareto-front-v1`**: severity vs attack_cost; **`fragility-plot-pareto-style-v1`** |
| `scripts/plot_fragility_surface_csv.py` | **`fragility_surface.py`** CSV heatmap (**panic0** × **depeg_threshold**); **`fragility-plot-surface-style-v1`** |
| `scripts/plot_counterfactual_bars.py` | **`export_counterfactual`** JSON: grouped bars (**integral_instability**, **attack_cost**) baseline vs counterfactual; **`fragility-plot-counterfactual-style-v1`** |
| `scripts/merge_counterfactual_attribution.py` | Star-merge exports → **`attribution-merge-v1`** |
| `scripts/summarize_attribution_merge.py` | **`attribution-interaction-summary-v1`** (sum of branch deltas + disclaimer) |
| `scripts/frozen_json_digest.py` | SHA-256 fingerprints for frozen JSON (`--json-out`) |
| `scripts/compare_replays.py` | Print JSON diff of top-level replay metrics + **`metric_notes`** (price/headroom semantics); optional `--out` |
| `scripts/gce_git_deploy.sh` | **Linux VM / GCE:** `git clone` or `git pull`, venv, `pip install -e ".[dev]"` — curl (public) or `scp` + [`gce_remote_git_deploy.sh`](scripts/gce_remote_git_deploy.sh) (private) |
| `scripts/gce_clone_pull_and_test.sh` | **On VM:** clone (HTTPS or SSH if **`~/.ssh/gce_github_ed25519`** exists) + **`~/.ssh/config`** helper when bundled + pull + **`ruff`** + **`pytest`** (CI perf gate) |
| `scripts/gce_create_minimal.ps1` / `scripts/gce_create_minimal.sh` | **Bootstrap:** enable Compute API + **e2-micro** Ubuntu **24.04** VM; default **startup** installs **git**, **Python 3.12**, shallow **clone** + **`pip install -e ".[dev]"`** ([`docs/GCE_BOOTSTRAP.md`](docs/GCE_BOOTSTRAP.md)) |
| `scripts/gce_remote_git_deploy.sh` | VM-side wrapper: SSH env + apt + runs **`/tmp/gce_git_deploy.sh`** (upload both scripts for private GitHub) |
| `scripts/gce_pull_pytest.sh` | **On VM:** pull **`main`**, `pip install -e ".[dev]"`, **`python -m pytest -q`** only (deploy key env same as `gce_git_deploy.sh`) |
| `scripts/gce_bootstrap_pull_latest_pytest.sh` | **Bootstrap:** `scp` to VM **`/tmp/`**, then **`bash /tmp/gce_bootstrap_pull_latest_pytest.sh`** — pulls commit that adds `gce_pull_pytest.sh`, then runs it |
| `scripts/gce_pull_and_test.sh` | **On VM:** pull **`main`**, **`pip install -e ".[dev]"`**, **`ruff`**, **`pytest`** with CI perf gate (`FRAGILITY_PERF_GATE`) — see [`docs/GCE_DEPLOY_KEY.md`](docs/GCE_DEPLOY_KEY.md) |
| `scripts/gce_configure_git_ssh.sh` | **On VM:** idempotent **`~/.ssh/config`** for **`github.com`** + deploy key (`~/.ssh/gce_github_ed25519`); avoids **`GIT_SSH_COMMAND`** on every pull — see [`docs/GCE_DEPLOY_KEY.md`](docs/GCE_DEPLOY_KEY.md) |
| `scripts/gce_sync_vm.ps1` | **From Windows:** `scp` (LF-normalized) **`gce_configure_git_ssh.sh`** + **`gce_pull_and_test.sh`**, then **`gcloud compute ssh`** to run both. Args **`-Instance`** / **`-Zone`** or env **`FRAGILITY_GCE_*`** (see [`GCE_DEPLOY_KEY.md`](docs/GCE_DEPLOY_KEY.md) — single VM) |
| `scripts/generate_gce_deploy_key.ps1` | Create `.deploy/gce_github_ed25519` (+ `.pub`) for GitHub **Deploy keys** — see [`docs/GCE_DEPLOY_KEY.md`](docs/GCE_DEPLOY_KEY.md) |
| `scripts/install_accelerate_windows.ps1` | Windows **amd64** CPython: `pip install -e ".[dev,accelerate]"` (finds x64 Python / `py -3.12-64`; WoA uses built-in x64 emulation — same wheels as x64 PCs) |
| `scripts/regenerate_test_exports.ps1` / `scripts/regenerate_test_exports.sh` | Fill `artifacts/test_exports/` for browser QA (gitignored) |
| `scripts/regenerate_bundled_viewer_samples.py` | Regenerate checked-in `artifacts/replay_viewer/sample_*`, attribution merge, quad composite, flagship bundled JSON |
| `scripts/check_manifest_digest.py` | CI guard: `golden_metrics_sha256` must match `tests/fixtures/benchmarks/golden_metrics_sha256.txt` |
| `scripts/export_aggregate_counterfactual_chain.py` | Aggregate peg cumulative mutation chain + optional path trace |
| `scripts/plot_institutional_composite_bars.py` | Bar chart of per-branch `integral_instability` from institutional composite JSON |
| `scripts/benchmark_rollout.py` | Wall-clock: **`--bundle <bundle_id>`** (frozen suite IDs in [`benchmarks/README.md`](benchmarks/README.md)), **`--bundle-all`** (full suite JSON), or **ad-hoc** `--mode aggregate|network|resource_cascade|service_backlog|liquidity_ladder|inventory_buffer` (`--json`, **`workflow`** field) |
| `scripts/run_benchmark_suite.py` | Frozen benchmark suite (`--validate`, `--json`, **`--manifest-out`**, **`--bench-search`**) — see [`benchmarks/README.md`](benchmarks/README.md), charter Phase H in [`BOUNDARIES.md`](BOUNDARIES.md) |
| `scripts/ci_local.sh` | **Linux / macOS / WSL:** same checks as Windows `ci_local.ps1` (canonical validation path — not GitHub Actions on push) |
| `scripts/ci_local.ps1` | **Windows PowerShell:** canonical validation (ruff, pytest, manifest pins) |
| `scripts/run_flagship_demo.py` | **Flagship bundle:** short GA + `pareto_front.json` + **`fragility-certificate-v1`** under `artifacts/flagship/output` (see [`docs/PAPER_APPENDIX_WORKFLOW.md`](docs/PAPER_APPENDIX_WORKFLOW.md)) |
| `scripts/export_fragility_certificate.py` | Emit **`fragility-certificate-v1`** for digested JSON + env fingerprints (`--digest-json`, optional `--validate-bundles`) |
| `scripts/fragility_robustness_sweep.py` | Ensemble over **`graph_seed`** or **`--neighbor-json-list`**; physics **`--sweep-*`**; GA **`--ga-budget-sweep`**, **`--ga-population-sweep`** + **`--ga-fixed-generations`**, **`--ga-budget-2d`** — see [`benchmarks/README.md`](benchmarks/README.md) |
| `scripts/mechanism_design_policy_sweep.py` | Defender presets + inner GA; **`--eval-workers`**; **`fragility-mechanism-design-outer-v1`** |
| `scripts/institutional_composite_demo.py` | Decoupled multi-kernel composite: twin (**v1**), **`--triple`** (**v2**), **`--quad`** (**v3**), **`--penta`** (**v4**, + liquidity ladder); **`--out`** — see [`benchmarks/README.md`](benchmarks/README.md) |
| `scripts/export_liquidity_ladder_joint_attribution.py` | **`attribution-merge-v1`**: remove_steps + margin or delever branch — [`docs/liquidity_ladder_counterfactual_example.md`](docs/liquidity_ladder_counterfactual_example.md) |
| `scripts/counterfactual_epsilon_sweep.py` | **`--mode aggregate|network|resource_cascade|service_backlog|liquidity_ladder`**; axes **`initial_panic`** / **`initial_overload`** / **`initial_backlog`** / **`process_rate`** / **`initial_margin`** / **`delever_rate`** / network scalars; **`--emit-trace`** → `explanation-trace-v1`; [`docs/network_counterfactual_example.md`](docs/network_counterfactual_example.md), cascade cookbook [`docs/resource_cascade_counterfactual_example.md`](docs/resource_cascade_counterfactual_example.md), liquidity cookbook [`docs/liquidity_ladder_counterfactual_example.md`](docs/liquidity_ladder_counterfactual_example.md) |

**Plot scripts** (`plot_*.py`) require **`matplotlib`** (`pip install -e ".[dev]"` or **`.[viz]`**).

Static **replay** UI: `artifacts/replay_viewer/index.html` — timeline scrub, optional compare replay, hash routing (HTTP). **JSON contracts:** which files this page loads vs not — [`artifacts/replay_viewer/README.md`](artifacts/replay_viewer/README.md).

Local **bulk exports** for trying many scenarios in the browser: run `pwsh -File scripts/regenerate_test_exports.ps1` → writes under `artifacts/test_exports/` (gitignored). See `artifacts/README_test_exports.txt`.

Static **Pareto** UI: `artifacts/pareto_viewer/index.html` — load `pareto_front.json` (from `scripts/export_pareto_front.py`); bundled aggregate, network, resource cascade, service backlog, and liquidity ladder samples; HTTP **Presets** via `local_presets.json`; hover / click / arrows; optional hash `#src=…&archive=N`. Archive JSON includes `integral_instability` per point.

Static **attribution** UI: `artifacts/attribution_viewer/index.html` — `attribution-merge-v1` and mutation-chain path traces.

Static **composite** UI: `artifacts/composite_viewer/index.html` — institutional composite v1–v3 branch metrics (HTTP presets). Bundled demo map: [`docs/BUNDLED_ARTIFACTS.md`](docs/BUNDLED_ARTIFACTS.md).

## Extending

- **Custom co-evolution:** implement a deterministic ``rollout_fn(schedule, seed, defender)`` and pass it to ``fragility_engine.coevolution.alternating_coevolution_rollout`` (see [`BOUNDARIES.md`](BOUNDARIES.md) Phase G).
- **Custom topology:** ``ContagionGraph.from_neighbor_lists([[...], ...])`` builds from adjacency lists (symmetrized by default). For **directed out-neighbor lists** without a dense matrix, pass JSON via ``--neighbor-json`` (optional ``--neighbor-weights-json``); replay metadata uses ``neighbor_lists_topology_meta`` (`storage: neighbor_lists`). Synthetic graphs still attach ``undirected_edges`` + ``storage: dense_adjacency``.
- **Perf gate:** set ``FRAGILITY_PERF_GATE=1`` and ``FRAGILITY_PERF_GATE_MS`` (240s default) when running ``python -m pytest`` locally or on GCE. Without those vars, ``tests/test_benchmark_perf_gate.py`` is skipped.
- **Numba parity:** CI runs a separate Ubuntu job that installs ``.[accelerate]`` and executes ``tests/test_resource_cascade_numba_parity.py`` (matrix jobs stay NumPy-only for speed and portability).

## Week roadmap (suggested)

1. CLI smoke + collapse metric — `scripts/week1_smoke.py`
2. Evolutionary adversary — `scripts/run_ga_demo.py`
3. Network contagion — `fragility_engine.network` + `StablecoinNetworkWorld`
4. Replay JSON — `runner.rollout_to_replay_dict` (`schema_version` **0.4.0**, includes `events_lane`)
5. Static replay / Pareto viewers (`artifacts/*/viewer`) consume frozen JSON; richer web UI remains optional.
