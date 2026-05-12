# Phase M — optional GitHub issues (exit criteria ↔ tests)

`BOUNDARIES.md` Phase M asks for **one tracking issue per exit criterion**, each naming a single acceptance test. The criteria are already satisfied on `main`; this file is a **copy-paste** aid if you want labeled issues for audit or onboarding.

**Created on repo (theorem6/fragility-discovery-engine):** [#1](https://github.com/theorem6/fragility-discovery-engine/issues/1) world + rollout + replay · [#2](https://github.com/theorem6/fragility-discovery-engine/issues/2) GA demo · [#3](https://github.com/theorem6/fragility-discovery-engine/issues/3) frozen benchmark / golden row · [#4](https://github.com/theorem6/fragility-discovery-engine/issues/4) counterfactual / Pareto / sweeps.

**Status:** All four were **closed** as retrospective audit issues (criteria were already met on `main` when the issues were filed).

Run from the repo root with [`gh`](https://cli.github.com/) authenticated.

## Issue 1 — World + rollout + replay

```bash
gh issue create --title "Phase M: world + rollout + replay contract" --body "Acceptance: replay export matches documented Phase M table.

Primary tests: \`tests/test_service_backlog_rollout.py\`, \`tests/test_replay_contract_service_backlog.py\`."
```

## Issue 2 — GA smoke entry point

```bash
gh issue create --title "Phase M: GA demo script smoke" --body "Acceptance: documented GA demo exercises search on ServiceBacklogWorld.

Primary script: \`scripts/run_service_backlog_ga_demo.py\` (see \`docs/phase_m_third_reference_domain.md\`)."
```

## Issue 3 — Frozen benchmark bundle + golden metrics

```bash
gh issue create --title "Phase M: frozen benchmark bundle + GOLDEN_METRICS" --body "Acceptance: frozen bundle \`service_backlog_rollout_v1\` + CI golden row.

Primary tests: \`tests/test_benchmark_suite.py\`."
```

## Issue 4 — Counterfactual / co-evolution / Pareto / sweeps parity

```bash
gh issue create --title "Phase M: counterfactual + Pareto + sweep parity" --body "Acceptance: counterfactuals, co-evolution hooks, Pareto/MC exports, ε-sweeps documented in Phase M doc §4.

Cookbook: \`docs/service_backlog_counterfactual_example.md\`. Representative tests: \`tests/test_counterfactual_chain_service_backlog.py\`, sweep/counterfactual tests under \`tests/\` for \`service_backlog\` mode."
```
