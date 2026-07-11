"""Discrete-time STL subset for trajectory robustness (falsification guide).

Supported formulas (parsed from a small DSL string):

- ``x[i] > c`` / ``x[i] < c`` / ``x[i] >= c`` / ``x[i] <= c`` — predicates on
  ``state_vector[i]``
- ``G[a,b] phi`` — always (globally) on discrete window [a,b]
- ``F[a,b] phi`` — eventually (finally) on [a,b]
- ``phi U[a,b] psi`` — until (limited)

Robustness follows standard discrete quantitative semantics (Fainekos/Pappas style):
predicate ``x-c``, Always = min, Eventually = max.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np

from fragility_engine.adversary.fitness import severity_score
from fragility_engine.adversary.search import genetic_search
from fragility_engine.types import RolloutResult, SearchResult, TrajectoryStep

STL_ROBUSTNESS_SCHEMA = "stl-robustness-v1"


@dataclass(frozen=True)
class Pred:
    channel: int
    op: str
    const: float


@dataclass(frozen=True)
class Always:
    a: int
    b: int
    child: Any


@dataclass(frozen=True)
class Eventually:
    a: int
    b: int
    child: Any


@dataclass(frozen=True)
class Until:
    a: int
    b: int
    left: Any
    right: Any


Formula = Pred | Always | Eventually | Until

_PRED = re.compile(
    r"^\s*x\[(\d+)\]\s*(>=|<=|>|<)\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*$"
)
_G = re.compile(r"^\s*G\[(\d+)\s*,\s*(\d+)\]\s*(.+)$", re.DOTALL)
_F = re.compile(r"^\s*F\[(\d+)\s*,\s*(\d+)\]\s*(.+)$", re.DOTALL)
_U = re.compile(
    r"^\s*(.+?)\s+U\[(\d+)\s*,\s*(\d+)\]\s+(.+)\s*$",
    re.DOTALL,
)


def parse_stl(expr: str) -> Formula:
    """Parse a minimal discrete STL expression."""

    s = expr.strip()
    m = _G.match(s)
    if m:
        return Always(int(m.group(1)), int(m.group(2)), parse_stl(m.group(3)))
    m = _F.match(s)
    if m:
        return Eventually(int(m.group(1)), int(m.group(2)), parse_stl(m.group(3)))
    m = _U.match(s)
    if m:
        return Until(int(m.group(2)), int(m.group(3)), parse_stl(m.group(1)), parse_stl(m.group(4)))
    m = _PRED.match(s)
    if m:
        return Pred(int(m.group(1)), m.group(2), float(m.group(3)))
    raise ValueError(f"Unsupported STL fragment: {expr!r}")


def _pred_rob(step: TrajectoryStep, pred: Pred) -> float:
    vec = np.asarray(step.state_vector, dtype=np.float64).reshape(-1)
    if pred.channel < 0 or pred.channel >= vec.shape[0]:
        raise IndexError(f"channel x[{pred.channel}] out of range for state_vector len={vec.shape[0]}")
    x = float(vec[pred.channel])
    c = pred.const
    if pred.op == ">":
        return x - c
    if pred.op == ">=":
        return x - c
    if pred.op == "<":
        return c - x
    if pred.op == "<=":
        return c - x
    raise ValueError(pred.op)


def robustness(formula: Formula, trajectory: list[TrajectoryStep], *, t0: int = 0) -> float:
    """Quantitative robustness at discrete time ``t0`` (higher ⇒ more satisfied)."""

    n = len(trajectory)
    if n == 0:
        return float("-inf")

    if isinstance(formula, Pred):
        if t0 < 0 or t0 >= n:
            return float("-inf")
        return _pred_rob(trajectory[t0], formula)

    if isinstance(formula, Always):
        a, b = formula.a, formula.b
        vals = [
            robustness(formula.child, trajectory, t0=t0 + k)
            for k in range(a, b + 1)
            if 0 <= t0 + k < n
        ]
        return float(min(vals)) if vals else float("-inf")

    if isinstance(formula, Eventually):
        a, b = formula.a, formula.b
        vals = [
            robustness(formula.child, trajectory, t0=t0 + k)
            for k in range(a, b + 1)
            if 0 <= t0 + k < n
        ]
        return float(max(vals)) if vals else float("-inf")

    if isinstance(formula, Until):
        # phi U[a,b] psi : exists k in [a,b] s.t. psi at t0+k and phi on [t0+a .. t0+k)
        a, b = formula.a, formula.b
        best = float("-inf")
        for k in range(a, b + 1):
            tk = t0 + k
            if tk < 0 or tk >= n:
                continue
            rob_psi = robustness(formula.right, trajectory, t0=tk)
            rob_phi = float("inf")
            for j in range(a, k):
                tj = t0 + j
                if 0 <= tj < n:
                    rob_phi = min(rob_phi, robustness(formula.left, trajectory, t0=tj))
            if rob_phi == float("inf"):
                rob_phi = 0.0
            best = max(best, min(rob_psi, rob_phi))
        return float(best)

    raise TypeError(type(formula))


def rollout_robustness(rollout: RolloutResult, formula: Formula | str) -> float:
    phi = parse_stl(formula) if isinstance(formula, str) else formula
    return robustness(phi, rollout.trajectory, t0=0)


@dataclass(frozen=True)
class StlFalsifyResult:
    search: SearchResult
    formula: str
    robustness: float
    violated: bool


def stl_falsify_search(
    rollout_fn: Callable[[np.ndarray, int], RolloutResult],
    formula: str,
    *,
    horizon: int,
    seed: int,
    generations: int = 10,
    population_size: int = 20,
) -> StlFalsifyResult:
    """Search schedules that *minimize* robustness (find violations of ``formula``)."""

    phi = parse_stl(formula)

    def fitness_fn(r: RolloutResult) -> float:
        # Maximize negative robustness (= minimize satisfaction)
        rob = robustness(phi, r.trajectory, t0=0)
        # Tie-break with severity so search still progresses on flat STL landscapes
        return float(-rob + 0.01 * severity_score(r))

    result = genetic_search(
        rollout_fn,
        horizon=horizon,
        generations=generations,
        population_size=population_size,
        seed=seed,
        fitness_fn=fitness_fn,
    )
    rob = rollout_robustness(result.best_rollout, phi)
    return StlFalsifyResult(
        search=result,
        formula=formula,
        robustness=rob,
        violated=rob < 0.0,
    )


def stl_robustness_payload(res: StlFalsifyResult) -> dict[str, Any]:
    r = res.search.best_rollout
    return {
        "schema": STL_ROBUSTNESS_SCHEMA,
        "formula": res.formula,
        "robustness": res.robustness,
        "violated": res.violated,
        "best_fitness": res.search.best_fitness,
        "collapsed": bool(r.collapsed),
        "severity": float(severity_score(r)),
        "note": (
            "Discrete-time STL subset (G/F/U + channel predicates). "
            "Negative robustness ⇒ formula falsified on the best schedule."
        ),
        "genome": res.search.best_genome.tolist(),
    }
