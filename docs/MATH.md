# Mathematics and conventions

Canonical reference for objectives, dominance, hypervolume, search algorithms, simulation updates, and explanation deltas in the Fragility Discovery Engine.

For algorithm provenance (original vs standard vs borrowed), see [Algorithms](/docs/algorithms.html). For CLI usage, see [How to Use](/docs/how-to-use.html).

---

## 1. Scope and honesty

This project uses **deliberately simple toy models**. They are:

- Deterministic on the charter path (fixed seeds → identical JSON)
- Not calibrated to any real institution, market, or regulatory standard
- Intended for **reproducible fragility search and explanation**, not forecasting

When a equation below cites a literature family (DeGroot contagion, queue backlog, margin spiral), it means **structural analogy**, not econometric fit.

---

## 2. Rollout metrics

Every simulation step reports `instability ∈ [0, ∞)` (typically `[0, 2]` in practice). A rollout aggregates:

| Metric | Definition |
|--------|------------|
| `integral_instability` | \(\sum_t \text{instability}_t\) |
| `mean_instability` | `integral_instability / n_steps` |
| `final_instability` | Instability at last step |
| `peak_instability` | \(\max_t \text{instability}_t\) |
| `attack_cost` | Weighted sum of shock magnitudes (see §5) |
| `collapsed` | Domain-specific failure predicate |
| `collapse_timestep` | First step where collapse holds, if any |

Code: `fragility_engine.runner`.

---

## 3. Search objectives

### 3.1 Severity (scalar)

\[
\text{severity}(r) = \text{final\_instability}(r) + \mathbb{1}_{\text{collapsed}} \cdot \frac{10}{1 + t_{\text{collapse}}}
\]

Early collapse adds a speed bonus. Code: `adversary/fitness.py::severity_score`.

### 3.2 Phase A fitness (severity only)

\[
f(r) = \text{severity}(r)
\]

### 3.3 Phase C fitness (severity minus cost)

\[
f(r) = \text{severity}(r) - w \cdot \text{attack\_cost}(r)
\]

\(w\) = `attack_cost_weight`. Code: `fitness_severity_minus_cost`.

### 3.4 Attack Pareto archive (two objectives)

For trade-off archives, a point **A** dominates **B** when:

\[
\text{severity}_A \ge \text{severity}_B \quad\text{and}\quad \text{cost}_A \le \text{cost}_B
\]

with strict inequality on at least one axis. **Maximize severity, minimize attack cost.**

Code: `adversary/pareto.py::pareto_indices`.

The GA search itself uses a **scalar** fitness; the Pareto archive is a **post-hoc** projection of evaluated individuals (`collect_pareto=True`), not NSGA-II.

---

## 4. Hypervolume

### 4.1 Generic 2-D minimization

Standard Zitzler & Thiele indicator for two **minimized** objectives \((f_1, f_2)\). Reference point \(\mathbf{r}\) must strictly dominate the front (both coordinates **larger** / worse than every point).

\[
HV(P, \mathbf{r}) = \text{area of union of rectangles } [p_1, r_1] \times [p_2, r_2] \text{ for } p \in ND(P)
\]

Implementation: sort by \(f_1\), sweep from right. Code: `benchmarks/hypervolume.py::hypervolume_2d_min`.

Regression fixtures `pinned_pareto_front_*.json` test this sweep on **generic** minimized axes — not attack archive layout.

### 4.2 Attack Pareto hypervolume (CI pins)

Attack archives maximize severity. Hypervolume requires minimization, so we transform:

\[
(f_1, f_2) = (-\text{severity},\; \text{attack\_cost})
\]

Then apply `hypervolume_2d_min` on the non-dominated set of transformed points. This preserves the **same partial order** as `pareto_indices`.

Code: `attack_pareto_to_min_points`, `hypervolume_2d_attack_pareto`, `default_attack_hypervolume_reference`.

Auto reference (when not pinned):

\[
r_i = \max(f_i) + \max(|\max(f_i)| \cdot 0.15,\; 0.01)
\]

Flagship bundled sample uses fixed reference \((15, 15)\) on transformed coordinates.

---

## 5. Stress schedules and attack cost

Genome shape: `(horizon, 2)` with entries in \([0, 1]^2\).

- Column 0 → shock kind selector (bucket into `{none, reserve_loss, rumor, …}`)
- Column 1 → magnitude clipped to \([0, 1]\)

Attack cost:

\[
\text{cost} = \sum_t w_{\text{kind}(t)} \cdot \text{mag}_t
\]

Default weights: `none=0`, `rumor=1.0`, `reserve_loss=2.5`. Code: `adversary/encoding.py`.

---

## 6. Genetic algorithm

Generational GA with:

| Operator | Rule |
|----------|------|
| Selection | Keep top `elite_frac × population` by scalar fitness |
| Crossover | Single-point on time axis between two elite parents |
| Mutation | Bernoulli mask rate + Gaussian noise, clip to \([0,1]\) |
| Monte Carlo | Uniform random genomes; keep argmax fitness |

Code: `adversary/search.py`. Matches Holland/Goldberg structure; not a production MOEA.

Defender search uses the same loop on a 4-D vector in \([0,1]^4\) (`genetic_vector_search`).

---

## 7. Co-evolution

Alternating rounds (Hillis-style competitive co-evolution):

1. Fix defender → evolve attacker maximizing `severity(r)`
2. Fix attacker → evolve defender minimizing `severity(r)` (fitness = `-severity`)

Defender genome affine-rescales resilience parameters (panic decay, rumor gain, depeg threshold, reserve boost). Code: `coevolution/alternating.py`, `coevolution/defender.py`.

---

## 8. Simulation worlds (charter)

All worlds: `reset()` → `step(events)` → metrics. Collapse predicates are explicit thresholds.

### 8.1 Aggregate peg

- Price: \(P = \text{reserves} / \max(\text{supply}, \epsilon)\)
- Reserve shock: \(\text{reserves} \leftarrow \text{reserves} \cdot (1 - \text{loss})\)
- Rumor: \(\text{panic} \leftarrow \clip(\text{panic} + g \cdot \text{mag})\)
- Instability: \(\text{panic} + 2 \max(0, \theta - P) + \max(0, 1 - P)\)

Toy bank-run / stablecoin stress. Code: `world/stablecoin_peg.py`.

### 8.2 Network contagion (DeGroot-style)

\[
p_i' = \clip\bigl((1-\beta)\, p_i + \beta \cdot \text{mean}_{j \in N(i)} p_j\bigr)
\]

Linear opinion dynamics on a directed graph ([DeGroot 1974](https://en.wikipedia.org/wiki/DeGroot_learning); MIT 14.15 Networks). Code: `network/contagion.py`.

### 8.3 Resource cascade

Two capacity layers \(h_0, h_1\) with overload \(O\). Coupling damps secondary headroom when primary is stressed and overload is high. Collapse when \(\min(h_0, h_1)\) falls below headroom floor. Motter–Lai-style cascade **reduction**. Code: `world/resource_cascade.py`.

### 8.4 Service backlog

Backlog \(B\), slack \(S\). Demand shocks increase \(B\); processing drains \(B\) proportional to \(S\). Collapse on backlog ceiling or slack floor. Queue-spiral **reduction**. Code: `world/service_backlog.py`.

### 8.5 Liquidity ladder

Margin utilization \(M\), market depth \(D\). Parallel structure to service backlog for funding stress. Code: `world/liquidity_ladder.py`.

### 8.6 Inventory buffer

Stock \(S\), fulfillment \(F\). Demand drains stock; fulfillment shocks erode \(F\). Collapse on stockout or fulfillment floor. Code: `world/inventory_buffer.py`.

---

## 9. Research fork (coupled institution)

Separate from charter. Peg panic \(P\) and overload \(O\) exchange signals each step:

\[
P \leftarrow P + 0.4 \cdot \text{loss} + \lambda \cdot O + \text{noise}
\]
\[
O \leftarrow O + 0.35 \cdot \text{rumor} + \lambda \cdot P + \text{noise}
\]

\(\lambda\) = coupling strength. **Gaussian noise** each step — stochastic unless seeds pin all RNG draws. Code: `forks/coupled_institution/`.

---

## 10. Explanation deltas

### 10.1 Counterfactual exports

\[
\Delta_{\text{cost}} = \text{cost}_{\text{baseline}} - \text{cost}_{\text{variant}}
\]
\[
\Delta_{\text{integral}} = \text{integral}_{\text{baseline}} - \text{integral}_{\text{variant}}
\]

Positive Δ means the variant improved that metric relative to baseline.

### 10.2 Mutation-chain path traces

Forward differences along a path use **variant minus predecessor** on the chain (opposite sign from §10.1). Read schema labels when comparing exports.

### 10.3 Interaction summaries

Branch deltas are **summed arithmetically** — not Shapley values or integrated gradients.

---

## 11. What this is not

- Not a proof of real-world fragility for any named institution
- Not a regulatory capital or stress-test certification
- Not a calibrated macro or market microstructure model
- Not guaranteed globally optimal search (GA / MC heuristics)

---

## 12. Validation

| Check | Command |
|-------|---------|
| Hypervolume sweep | `python -m pytest tests/test_hypervolume.py -q` |
| Attack-Pareto alignment | `python -m pytest tests/test_attack_pareto_hypervolume.py -q` |
| Bundled Pareto pins | `python scripts/check_bundled_pareto_hypervolume.py` |
| Full local CI | `powershell -File scripts/ci_local.ps1` |

Fix history: [MATH_FIX_GOALS.md](MATH_FIX_GOALS.md) (archived goals for the hypervolume objective-direction patch).
