# Research extensions — QD · differential · evidence · plausibility · STL

Charter-compatible additions from the 2024–26 scenario-discovery / provenance / CPS
falsification literature. Does **not** merge mega-institution onto `main` or add
LLM-in-the-loop physics.

## Flight 1

### 1. Quality-diversity illumination → `scenario-archive-v1`

MAP-Elites–style niches over `(collapse_bin, severity_bin, cost_bin)`. Complements Pareto (severity vs cost) with **coverage of failure kinds**.

```powershell
fragility illuminate --example capacity-pool --generations 6 --population-size 16 `
  --export-archive artifacts/scenario_archive/sample.json
fragility shorthand resolve illuminate-archive
```

Module: `fragility_engine.adversary.scenario_archive`.

### 2. Differential stress → `differential-stress-v1`

Same schedule on two BYOW worlds; prefer **A collapses ∧ B survives** (regression / adapter comparison).

```powershell
fragility differential --example-a capacity-pool --example-b token-bucket `
  --generations 8 --export-json artifacts/differential/sample.json
```

Not FEL Δ⁻ (that is same-world counterfactual). Module: `fragility_engine.adversary.differential`.

### 3. PROV-lite evidence pack → `evidence-pack-v1`

Wraps digests + `fragility-certificate-v1` with PROV-style entities/activities.

```powershell
fragility evidence-pack --out artifacts/evidence_packs/sample.json `
  --artifact artifacts/flagship/bundled/best_replay.json `
  --artifact artifacts/flagship/bundled/pareto_front.json
```

Module: `fragility_engine.benchmarks.evidence_pack`.

## Flight 2

### 4. Plausibility / insanity budget → `plausibility-search-v1`

Quiet independent-row prior on genomes (Gremlin / AST-inspired). Fitness =
`severity − weight × insanity_budget` so search prefers severe *and* less insane schedules.

```powershell
fragility plausible-search --example capacity-pool --plausibility-weight 0.35 `
  --generations 8 --export-json artifacts/plausibility/sample.json
fragility shorthand resolve plausible-search
```

Module: `fragility_engine.adversary.plausibility`. Not a calibrated likelihood.

### 5. Discrete-time STL subset → `stl-robustness-v1`

Predicates `x[i] >/</>=/<= c` plus `G[a,b]`, `F[a,b]`, `U[a,b]` on trajectory
`state_vector`. Search minimizes robustness (negative ⇒ formula falsified).

```powershell
fragility falsify stl --formula "G[0,5] x[0] > 0" --byow-example capacity-pool `
  --generations 8 --export-json artifacts/stl_robustness/sample.json
# or falsification harness:
fragility falsify stl --formula "F[0,8] x[0] < 0.5" --example ranked-store
fragility shorthand resolve falsify-stl
```

Module: `fragility_engine.falsify.stl`.

## Deferred

- Hypergraph cascade fork (needs domain owner)
