# Fragility Evidence Language (FEL): A Semantic Contract for Reproducible Stress-Search and Attribution in Discrete-Time Simulations

**David Peterson**  
Founder, Agentic Ops · [https://agenticop.io](https://agenticop.io)  
Preprint fel-v0.1 — May 2026  
Software: [https://github.com/AgenticOp-io/fragility-discovery-engine](https://github.com/AgenticOp-io/fragility-discovery-engine)  
Spec: `docs/FRAGILITY_EVIDENCE_LANGUAGE.md` · Reference module: `src/fragility_engine/fel/`

---

## Abstract

Simulation-based stress testing and adversarial search produce heterogeneous JSON artifacts—rollout replays, Pareto archives, counterfactual bundles, path traces, and audit certificates—whose metric deltas are easy to misread when sign conventions differ across export paths. We introduce the **Fragility Evidence Language (FEL)**, a lightweight semantic contract that axiomatizes the types, evaluation laws, objective transforms, and attribution operators already implemented in the open-source Fragility Discovery Engine. FEL contributes three ideas: (1) a typed core **eval(W, G, σ) → R** separating worlds, exogenous shock schedules, and deterministic seeds; (2) **dual attribution operators**—Δ⁻ for counterfactual bundles (baseline minus variant) and Δ⁺ for forward path edges (successor minus predecessor)—with explicit roles so reviewers cannot conflate “intervention effect” with “cumulative step increment”; and (3) a **versioned evidence constructor registry** mapping schema IDs to merge graphs, explanation DAGs, fragility certificates, and institutional composites. FEL v0.1 is normative at the semantics layer; it does not define new physics or claim calibrated institutional risk. We describe the formal core, relate it to causal counterfactual framing and simulation reproducibility practice, walk through a flagship evidence chain, and state limitations honestly. A reference Python module encodes the operators for tests and tooling. FEL is intended as an interchange layer for discrete-time fragility experiments, not a replacement for domain-specific modeling languages.

**Keywords:** simulation evidence, reproducibility, counterfactual attribution, Pareto search, stress testing, semantic contract, JSON schema

---

## 1. Introduction

Engineers and researchers increasingly run **directed search** over stress scenarios in discrete-time simulators: genetic algorithms and Monte Carlo samplers propose shock schedules, simulators return trajectories and collapse metrics, and explainability layers emit counterfactual diffs and minimization traces. The Fragility Discovery Engine (FDE) follows this pattern across six reference “worlds” (aggregate peg, network contagion, resource cascade, service backlog, liquidity ladder, inventory buffer), exporting plain JSON with stable schema names for replay viewers and frozen benchmark CI [1].

A recurring failure mode is not incorrect physics but **ambiguous evidence**: the same numeric field `delta_integral_instability` may mean “variant improved on baseline” in one export and “the next mutation step added instability” in another, because counterfactual bundles and mutation-chain path traces use opposite subtraction orders by design. Without a named contract, reviewers, tooling authors, and future contributors miscompare artifacts—a problem familiar from reproducibility crises in computational science [2] and from the gap between causal *intent* and operational *metrics* in explainable simulation [3].

**Fragility Evidence Language (FEL)** addresses this by formalizing what the engine already computes:

- **Types** for worlds **W**, schedules **G**, seeds **σ**, rollouts **R**, interventions **I**, and evidence **E**.
- **Laws** for determinism, schedule domain, attack Pareto order, and composite independence.
- **Operators** Δ⁻ and Δ⁺ with non-overlapping artifact roles.
- **Constructors** with schema IDs (`pareto-front-v1`, `attribution-merge-v1`, `fragility-certificate-v1`, …).

FEL is deliberately **not** a domain-specific modeling language (cf. Modelica) nor a proof system; it is an evidence semantics layer comparable in spirit to provenance models [4] or experiment description vocabularies, but specialized for adversarial schedule search and fragility metrics.

**Contributions.**

1. The FEL core calculus: evaluation, metrics φ(R), severity functional S(R), attack Pareto dominance, and hypervolume coordinate transform.
2. Dual attribution operators with explicit epistemic readings (§5).
3. A schema registry linking evidence constructors to JSON artifacts in a production open-source pipeline (§6).
4. Reference implementation `fragility_engine.fel` with unit tests anchoring conventions (§8).

**Non-claims.** FEL does not establish causal identifiability, regulatory capital adequacy, or calibrated forecasts for real institutions. Toy worlds remain intentional [1].

---

## 2. Background and related work

### 2.1 Counterfactuals and interventions

Pearl’s structural causal framework defines counterfactual comparison under interventions do(X=x) [3]. FDE’s schedule-mask counterfactuals mechanically zero selected shock timesteps and re-run the simulator, then diff rollouts—a operational pipeline inspired by do-calculus but **not** equivalent to identifying causal effects in an observed system. FEL names this Δ⁻ convention so the engineering artifact aligns with the statistical reading “baseline minus variant.”

### 2.2 Minimal failing configurations

Greedy shock-set minimization and delta debugging [5] both shrink configurations while preserving a failure predicate. FDE’s greedy minimal collapse operates on attack schedules with pinned seeds; FEL treats the resulting explanation DAG as constructor `explanation-dag-v1`.

### 2.3 Multi-objective search quality

Attack search maximizes severity while minimizing attack cost. Pareto dominance and hypervolume indicators are standard in evolutionary multi-objective optimization [6]. FEL documents the engine’s transform to minimization coordinates **(-S, c)** before hypervolume, correcting a class of sign errors when mixing “maximize severity” fronts with “minimize both axes” volume code.

### 2.4 Reproducible computational experiments

Peng [2] argues for data and code availability as first-class scholarly objects. FDE’s frozen benchmark harness pins `(genome_seed, rollout_seed)` and asserts golden metrics in CI—**evidence before chrome** in project charter terms [1]. FEL extends this by standardizing *meaning* of exported deltas, not only *values*.

### 2.5 Positioning


| Approach                    | FEL relationship                                                                        |
| --------------------------- | --------------------------------------------------------------------------------------- |
| PROV-DM [4]                 | General provenance; FEL is domain-specific evidence semantics                           |
| SBOL / BioPAX               | Exchange formats for models; FEL exchanges *experiment outcomes*                        |
| SHAP / integrated gradients | Path attributions in ML; FEL’s Δ⁺ is defined on discrete simulator paths, not gradients |
| Regulatory stress scenarios | Real institutions and calibration; explicitly out of scope                              |


---

## 3. Problem statement

Consider a typical FDE workflow:

1. Search finds schedule **G** under world **W** with seed **σ**.
2. Export replay **R** and Pareto front **F**.
3. Explain layer emits counterfactual **B** (remove shock *k*) and mutation-chain path **P** (apply mutations sequentially).

Artifacts **B** and **P** both expose fields named `delta_integral_instability`. In **B**, positive values mean the variant **lowered** instability relative to baseline. In **P**, positive values mean the **next** prefix **increased** instability relative to the previous prefix. Confusing the two leads to incorrect scientific conclusions even when every simulation is deterministic and correct.

**Requirements** for a semantic contract:


| ID  | Requirement                                                                             |
| --- | --------------------------------------------------------------------------------------- |
| R1  | Named evaluation entry point eval(W, G, σ)                                              |
| R2  | Single definition of attack Pareto dominance and hypervolume transform                  |
| R3  | Distinct operators for counterfactual vs path attribution                               |
| R4  | Versioned mapping from JSON `schema` fields to constructors                             |
| R5  | Explicit non-goals (no hidden coupling in composites; no stochastic fork unless pinned) |


FEL v0.1 satisfies R1–R5 without altering physics kernels.

---

## 4. FEL overview

FEL has three layers:

1. **Semantic core** — types, eval, metrics, objectives (§5).
2. **Attribution algebra** — Δ⁻ and Δ⁺ (§6).
3. **Evidence constructors** — structured bundles with schema IDs (§7).

Optional surface syntax (`.fel` files) is informative only; normative v0.1 is JSON schemas plus Python reference functions.

**Version tag:** `fel-v0.1` (`fragility_engine.fel.FEL_VERSION`).

---

## 5. Semantic core

### 5.1 Types


| Symbol | Sort         | Description                                                     |
| ------ | ------------ | --------------------------------------------------------------- |
| W      | World        | Pinned dynamics template and parameters                         |
| G      | Schedule     | Matrix in [0,1]^{H×2}: shock intensity and timing gate per step |
| σ      | Seed         | Integer rollout seed (optional defender genome)                 |
| R      | Rollout      | Result of evaluation                                            |
| I      | Intervention | Typed edit to W, G, or initial conditions                       |
| E      | Evidence     | Serialized artifact with schema ID                              |


### 5.2 Evaluation

R = \mathrm{eval}(W, G, \sigma)

**Law (Determinism).** On charter worlds with pinned seeds, eval is reproducible: identical (W, G, σ) yields identical R.

**Law (Schedule domain).** Entries of G lie in [0,1]; decoding to exogenous events is fixed by the world template (world/adversary separation: attacks enter only via schedules, not hidden hooks inside physics steps [1]).

### 5.3 Metrics

Extract metric tuple φ(R):

\phi(R) = \langle \text{integralinstability}, \text{attackcost}, \text{finalinstability}, \text{collapsed}, \text{collapsetimestep}, S(R) \rangle

where **S(R)** is the severity functional used in search (`severity_score` in code). FEL does not mandate a single severity formula across all future worlds; it requires that a documented functional exists per charter world.

### 5.4 Attack Pareto order

For two rollouts with severities S_A, S_B and costs c_A, c_B:

A \prec B \iff S_A \ge S_B \land c_A \le c_B \text{ with strict inequality on at least one axis}

Non-dominated indices form the attack Pareto front.

### 5.5 Hypervolume transform

Hypervolume indicators assume minimization in each coordinate. FEL maps:

(\tilde{s}, \tilde{c}) = (-S(R), \text{attackcost})

Reference points must dominate the set in minimization sense (both coordinates worse than all front points). Generic 2-D minimization hypervolume applies after this transform [6].

---

## 6. Dual attribution operators

FEL’s central design choice is to **name two subtraction conventions** instead of forcing one global sign.

### 6.1 Δ⁻ — Counterfactual (bundle) attribution

For baseline rollout R₀ and variant R₁ under intervention I:

\Delta^{-}(\phi_0, \phi_1) = \phi(R_0) - \phi(R_1)

**Reading:** Positive Δ⁻ on integral instability ⇒ variant **reduced** instability vs baseline.

**Used in:** counterfactual JSON bundles, star-merge attribution graphs (`attribution-merge-v1`), heterogeneous merge tooling.

**Reference:** `fel.delta_counterfactual(baseline, variant)`.

### 6.2 Δ⁺ — Path forward attribution

For consecutive rollouts R_i, R_{i+1} along a cumulative path (mutation chain prefix, epsilon sweep):

\Delta^{+}(\phi_i, \phi_{i+1}) = \phi(R_{i+1}) - \phi(R_i)

**Reading:** Positive Δ⁺ ⇒ metric **increased** when advancing along the path.

**Used in:** `explanation-mutation-chain-path-v1`, sweep traces.

**Reference:** `fel.delta_path_forward(predecessor, successor)`.

### 6.3 Composition rules


| Artifact kind         | Operator | Question answered                           |
| --------------------- | -------- | ------------------------------------------- |
| Counterfactual bundle | Δ⁻       | What changed under intervention I?          |
| Path trace edge       | Δ⁺       | What did step i contribute along the chain? |
| Epsilon sweep edge    | Δ⁺       | What changed when ε advanced?               |


**Law (Δ separation).** Do not attach Δ⁻ to path-edge schema slots or Δ⁺ to counterfactual bundle slots.

Interaction summaries sum branch Δ⁻ values arithmetically; they are **not** Shapley values or integrated gradients [7].

---

## 7. Evidence constructors

Each constructor carries a versioned `schema` string. FEL v0.1 registry (subset):


| Constructor             | Schema ID                              | Role                                             |
| ----------------------- | -------------------------------------- | ------------------------------------------------ |
| Rollout replay          | `schema_version` in replay dict        | Canonical R                                      |
| Pareto front            | `pareto-front-v1`                      | Non-dominated (S, c) archive                     |
| Attribution merge       | `attribution-merge-v1`                 | Star merge of Δ⁻ bundles sharing baseline        |
| Explanation DAG         | `explanation-dag-v1`                   | Minimization / dependency graph                  |
| Explanation trace       | `explanation-trace-v1`                 | Linear typed trace                               |
| Mutation chain path     | `explanation-mutation-chain-path-v1`   | Prefix rollouts + Δ⁺ edges                       |
| Fragility certificate   | `fragility-certificate-v1`             | Witness replay + front + environment fingerprint |
| Institutional composite | `fragility-institutional-composite-v4` | Same G on multiple W_i                           |
| Benchmark manifest      | `benchmark-manifest-v2`                | Pinned benchmark inventory digest                |


**Star merge.** Given baseline node B and variants V₁…V_k, edges (B → V_j) carry Δ⁻ metrics and intervention labels; baseline equality is validated strictly before merge.

**Certificate.** Existential witness (W, G, σ) with documented thresholds; bundles citeable as paper-appendix artifacts [8].

**Composite law (Independence).** Institutional composite evaluates {eval(W_i, G, σ)} in parallel; kernels do not exchange state within a timestep unless a single coupled world W explicitly models coupling.

---

## 8. Worked example (flagship pipeline)

The following chain is reproducible via `python scripts/run_flagship_demo.py` [8]:

1. **Search** — GA under aggregate world W_agg produces schedule G* and rollout R* = eval(W_agg, G*, σ).
2. **Front** — Archive `{R_j}` yields Pareto set F with schema `pareto-front-v1`; hypervolume uses (-S, c).
3. **Counterfactual** — Intervention I = remove shock at index k gives R₀, R₁; bundle stores Δ⁻ integrals and costs.
4. **Path** — Mutation chain prefixes R₀…R_m with Δ⁺ on edges (`explanation-mutation-chain-path-v1`).
5. **Certificate** — `fragility-certificate-v1` bundles replay, front, and environment digest for citation.

A reader comparing step 3 and step 4 must apply Δ⁻ and Δ⁺ readings respectively—a distinction FEL makes explicit in schema documentation and tests.

---

## 9. Implementation and validation

**Reference module:** `src/fragility_engine/fel/conventions.py` exports:

- `FEL_VERSION`, `SCHEMA_REGISTRY`
- `metrics_from_rollout`, `severity_functional`, `to_min_objectives`
- `attack_pareto_dominates`, `delta_counterfactual`, `delta_path_forward`
- `fel_laws_summary()` for machine-readable axioms

**Tests:** `tests/test_fel_conventions.py` verifies sign conventions, dominance logic, and the opposite signs of Δ⁻ vs Δ⁺ on the same rollout pair.

**Frozen benchmarks:** Phase H suite validates golden metrics including corrected attack-Pareto hypervolume semantics; manifest digest SHA-256 prevents silent drift [1].

FEL v0.1 does **not** include a `.fel` parser; Python APIs and JSON schemas are normative.

---

## 10. Limitations and future work

1. **No causal identifiability** — Schedule-mask counterfactuals are engineering interventions, not identified causal effects in observational data.
2. **Toy worlds** — Reference domains are structural analogies, not calibrated institution models.
3. **Path order sensitivity** — Δ⁺ mutation chains depend on mutation order; FEL documents but does not resolve order ambiguity.
4. **No Shapley axioms** — Branch sums lack fairness guarantees of cooperative game attributions.
5. **Surface syntax** — Future fel-v0.2 may add parsers; semantics remain primary.
6. **Coupled research fork** — Stochastic Gaussian steps in coupled fork worlds require explicit seed pinning outside charter determinism unless documented.

Future work: empirical study of misread rates before/after FEL labeling; PROV export mapping; alignment with emerging simulation audit standards.

---

## 11. Conclusion

Fragility Evidence Language (FEL) provides a small, honest semantic contract for simulation-based fragility discovery: name the evaluation entry point, separate counterfactual and path attributions, and version evidence constructors. It formalizes existing engine behavior rather than inventing new physics, making multi-artifact review and CI-backed reproducibility easier. We release FEL v0.1 with open-source reference code and invite simulation and software-engineering communities to adopt or extend the registry.

---

## References

[1] D. Peterson, Agentic Ops, *Fragility Discovery Engine* — repository, charter (`BOUNDARIES.md`), v0.5.0 release. [https://github.com/AgenticOp-io/fragility-discovery-engine](https://github.com/AgenticOp-io/fragility-discovery-engine) · [https://agenticop.io](https://agenticop.io)

[2] R. D. Peng, “Reproducible Research in Computational Science,” *Science*, vol. 334, no. 6060, pp. 1226–1227, 2011.

[3] J. Pearl, *Causality: Models, Reasoning, and Inference*, 2nd ed. Cambridge University Press, 2009.

[4] W3C PROV-DM: The PROV Data Model. [https://www.w3.org/TR/prov-dm/](https://www.w3.org/TR/prov-dm/)

[5] A. Zeller and R. Hildebrandt, “Simplifying and Isolating Failure-Inducing Input,” *IEEE Transactions on Software Engineering*, vol. 28, no. 2, pp. 183–200, 2002.

[6] E. Zitzler, M. Laumanns, and L. Thiele, “SPEA2: Improving the Strength Pareto Evolutionary Algorithm,” TI-K Report 103, ETH Zurich, 2001. (Hypervolume indicators in multi-objective optimization.)

[7] S. M. Lundberg and S.-I. Lee, “A Unified Approach to Interpreting Model Predictions,” in *Proc. NeurIPS*, 2017. (Path attribution methods in ML — contrast with FEL Δ⁺ on simulators.)

[8] Fragility Discovery Engine, `docs/PAPER_APPENDIX_WORKFLOW.md` — flagship demo and citation JSON pipeline.

---

## Appendix A — FEL laws (machine-readable summary)


| Law                    | Statement                                              |
| ---------------------- | ------------------------------------------------------ |
| Determinism            | Same (W, G, σ) ⇒ same R on charter worlds              |
| Schedule domain        | G ∈ [0,1]^{H×2}; decode fixed per W                    |
| Attack Pareto          | Dominate iff S ≥ and c ≤ with strict on one axis       |
| Hypervolume            | Use (-S, attack_cost) minimization coordinates         |
| Δ⁻                     | baseline − variant on bundle exports                   |
| Δ⁺                     | successor − predecessor on path/sweep edges            |
| Composite independence | Same G on multiple W_i; parallel eval unless coupled W |


---

## Appendix B — Example surface syntax (informative)

```fel
world network_charter_v1
seed 42

schedule G { horizon 64 }

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

Not parsed in v0.1; illustrates alignment between notation and Δ⁻ semantics.

---

## Acknowledgments

Prose drafting and structural editing used AI-assisted tools (Cursor, Composer language model). The author verified all definitions, operator signs, schema IDs, and implementation claims against the open-source reference code (`src/fragility_engine/fel/`, frozen benchmark suite, and `docs/FRAGILITY_EVIDENCE_LANGUAGE.md`).

---

*End of preprint fel-v0.1 · David Peterson, Founder, Agentic Ops (agenticop.io)*