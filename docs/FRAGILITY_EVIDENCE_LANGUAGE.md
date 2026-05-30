# Fragility Evidence Language (FEL) v0.1

Formal vocabulary for **schedules, rollouts, objectives, interventions, and evidence** in the Fragility Discovery Engine. FEL does not introduce new physics; it axiomatizes what the engine already computes so exports, benchmarks, and explain artifacts share one semantics.

**Implementation:** `src/fragility_engine/fel/`  
**Preprint:** [`preprint/FEL_preprint_v0.1.md`](preprint/FEL_preprint_v0.1.md) · **Publishing guide:** [`preprint/PUBLISHING.md`](preprint/PUBLISHING.md)  
**Related:** [MATH.md](MATH.md) (formulas), [ALGORITHMS.md](ALGORITHMS.md) (procedures)

---

## 0. Design goals

1. **One meaning per operator** — dominance, hypervolume, and attribution deltas are named once.
2. **Two attribution roles** — counterfactual bundles vs path/sweep edges use different delta signs on purpose.
3. **Schema registry** — JSON `schema` fields map to FEL constructors.
4. **Deterministic replay** — same world, schedule, and seed ⇒ same rollout (charter worlds).

Surface syntax (`.fel` files) is optional; v0.1 is the semantic core plus Python helpers.

---

## 1. Core types

| Symbol | Name | Definition |
|--------|------|------------|
| **W** | World | Pinned dynamics template + parameters (network, resource cascade, inventory buffer, …). |
| **G** | Schedule | Matrix in \([0,1]^{H \times 2}\): column 0 = shock intensity, column 1 = timing gate per horizon step. |
| **σ** | Seed | Integer rollout seed (and optional defender genome). |
| **R** | Rollout | Result of `eval(W, G, σ)` — trajectory, collapse flag, costs, integrals. |
| **φ(R)** | Metrics | `{ integral_instability, attack_cost, final_instability, collapsed, collapse_timestep, severity }`. |
| **S(R)** | Severity | Search functional; same as `severity_score(R)` in code. |
| **I** | Intervention | Typed edit to W or rollout initial conditions (remove shock, shift buffer, …). |
| **E** | Evidence | Structured artifact: trace, merge, DAG, certificate, Pareto front, composite. |

**Evaluation:**

\[
R = \mathrm{eval}(W, G, \sigma)
\]

Laws (see §9): determinism on charter worlds; schedule decode is fixed; interventions produce paired rollouts `(R₀, R₁)`.

---

## 2. Objectives and dominance

Attack-layer Pareto uses **maximize severity**, **minimize attack cost**:

\[
A \prec B \iff S(A) \ge S(B) \land c(A) \le c(B) \text{ with strict inequality on at least one axis}
\]

Python: `fel.attack_pareto_dominates`, `adversary.pareto.pareto_indices`.

Non-dominated set = attack Pareto front.

---

## 3. Hypervolume coordinates

Hypervolume is computed in **minimization** 2-D space:

\[
(\tilde{s}, \tilde{c}) = (-S, c)
\]

Reference point must lie **above** all points in both minimized coordinates (worse than the front). See [MATH.md § Hypervolume](MATH.md#hypervolume-on-the-attack-pareto-front).

Python: `fel.to_min_objectives`, `benchmarks.hypervolume.hypervolume_2d_attack_pareto`.

---

## 4. Interventions

An intervention **I** maps a baseline configuration to a variant and runs paired rollouts:

\[
R_0 = \mathrm{eval}(W, G, \sigma), \quad R_1 = \mathrm{eval}(W', G, \sigma) \text{ or } \mathrm{eval}(W, G', \sigma)
\]

Examples (explain layer): remove shock, epsilon sweep on a gate, inventory buffer shift, mutation chain prefix.

Intervention metadata is stored on bundles (`intervention`, pinned parameters).

---

## 5. Attribution operators

FEL defines **two** delta conventions; do not mix them on the same edge kind.

### 5.1 Δ⁻ Counterfactual (bundle attribution)

Used in counterfactual JSON bundles and attribution merges comparing baseline vs variant:

\[
\Delta^{-}(\phi_0, \phi_1) = \phi(R_0) - \phi(R_1)
\]

**Reading:** positive Δ⁻ on `integral_instability` ⇒ variant **reduced** instability vs baseline (variant is better on that metric).

Python: `fel.delta_counterfactual`, fields `delta_integral_instability`, `delta_attack_cost` on counterfactual exports.

### 5.2 Δ⁺ Path forward (sweep / mutation chain)

Used on consecutive nodes along a cumulative path (epsilon sweep, mutation chain):

\[
\Delta^{+}(\phi_i, \phi_{i+1}) = \phi(R_{i+1}) - \phi(R_i)
\]

**Reading:** positive Δ⁺ ⇒ metric **increased** when moving forward along the path (e.g. added mutation increased cost).

Python: `fel.delta_path_forward`, path trace `edges[].delta_*`.

### 5.3 When to use which

| Artifact | Operator | Typical question |
|----------|----------|------------------|
| Counterfactual bundle | Δ⁻ | “What changed if we apply intervention I?” |
| Path trace edge | Δ⁺ | “What did step *i* add along the chain?” |
| Epsilon sweep edge | Δ⁺ | “What changed when ε increased to the next run?” |

---

## 6. Evidence constructors

| Constructor | Schema ID | Role |
|-------------|-----------|------|
| Rollout replay | `schema_version` on replay dict | Canonical serialized **R**. |
| Counterfactual bundle | `counterfactual-bundle-v1` | Baseline vs variant Δ⁻ attribution (all `compare_rollouts` exports) |
| Pareto front | `pareto-front-v1` | Non-dominated **(S, c)** set. |
| Attribution merge | `attribution-merge-v1` | Star merge of Δ⁻ bundles. |
| Explanation DAG | `explanation-dag-v1` | Causal / dependency graph over nodes. |
| Explanation trace | `explanation-trace-v1` | Linear trace with typed edges. |
| Mutation chain path | `explanation-mutation-chain-path-v1` | Prefix rollouts + Δ⁺ edges. |
| Fragility certificate | `fragility-certificate-v1` | Bounded claim + witness schedule. |
| Institutional composite | `fragility-institutional-composite-v4` | Same **G** on multiple **Wᵢ** (not coupled physics). |
| Benchmark manifest | `benchmark-manifest-v2` | Pinned benchmark package metadata. |

Registry in code: `fel.SCHEMA_REGISTRY`.

**Merge (star):** several counterfactual bundles with a shared baseline node; edges carry Δ⁻ from baseline to each variant.

**Certificate:** existential witness `(W, G, σ)` with metrics exceeding thresholds documented in the certificate payload.

---

## 7. Composite evaluation

Institutional composite:

\[
\{ R_i = \mathrm{eval}(W_i, G, \sigma) \}_{i=1}^{k}
\]

Same schedule **G** across worlds; aggregation (e.g. max severity, percentile costs) is documented per manifest. **Not** a single coupled multi-world simulation unless explicitly modeled in one **W**.

---

## 8. Surface syntax (informative)

Optional `.fel` notation for human-authored specs (not required for v0.1 tooling):

```fel
world network_charter_v1
seed 42

schedule G {
  horizon 64
  # shocks decoded from [0,1] columns
}

rollout R0 = eval(W, G, seed)

intervention remove_shock { index 3 }
rollout R1 = eval(W, G', seed)

delta_minus instability = R0.integral_instability - R1.integral_instability
delta_minus cost        = R0.attack_cost - R1.attack_cost

evidence merge {
  baseline R0
  variant  R1
  intervention remove_shock
}
```

Parsers are future work; Python APIs and JSON schemas are normative for v0.1.

---

## 9. Laws (axioms)

1. **Determinism:** On pinned charter worlds, `eval(W, G, σ)` is reproducible.
2. **Schedule domain:** **G** entries ∈ [0,1]; decode to events is fixed by world template.
3. **Attack Pareto order:** §2; hypervolume uses §3 transform.
4. **Δ⁻ on bundles:** §5.1 for counterfactual and merge exports.
5. **Δ⁺ on path edges:** §5.2 for sweeps and mutation chains.
6. **Composite independence:** Multi-world composites are parallel evals, not hidden coupling.
7. **Schema versioning:** New fields bump `schema` IDs; FEL version `fel-v0.1` tags convention docs.

Machine-readable: `fel.fel_laws_summary()`.

---

## 10. Implementation map

| FEL concept | Python location |
|-------------|-----------------|
| eval | `rollout_*` in world modules, `adversary` search |
| φ(R), S(R) | `fel.metrics_from_rollout`, `fel.severity_functional` |
| Dominance / front | `adversary.pareto`, `fel.attack_pareto_dominates` |
| Hypervolume | `benchmarks.hypervolume` |
| Δ⁻ bundles | `explain.counterfactual`, `fel.delta_counterfactual` |
| Δ⁺ paths | `explain.trace`, `fel.delta_path_forward` |
| Merge / DAG | `explain.merge`, `explain.dag` |
| Certificate | `explain.certificate` |
| Composite | `benchmarks.institutional_composite` |

---

## Changelog

- **fel-v0.1** — Initial semantic spec; dual delta operators; schema registry; Python `fragility_engine.fel`.
