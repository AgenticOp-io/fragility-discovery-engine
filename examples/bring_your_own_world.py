"""Tutorial artifact — wire a CUSTOM world into the fragility search loop.

This is the runnable companion to ``docs/BRING_YOUR_OWN_WORLD.md``. It is NOT a
seventh reference domain: it lives outside ``src/fragility_engine``, is not part
of the frozen benchmark charter, and exists only to show how little code a
custom world needs before the search, minimization, and replay tooling work.

The example world is a **bounded capacity pool** — the classic ops failure shape
shared by connection pools, address pools, worker pools, and license pools:

- Clients request units from a fixed pool and release them later.
- ``reserve_loss`` shocks model **demand surges** (mass reconnects, thundering herd).
- ``rumor`` shocks model **leak conditions** (failures that strand allocations,
  which are only reclaimed after a timeout).

The interesting question the search answers: what *phasing* of leaks and surges
wedges the pool fastest? A leak is harmless on its own — the stranded units come
back after the timeout. A surge is survivable on its own — the pool has headroom.
The damage lives in the timing interaction, which is exactly the kind of
combinatorial ordering the engine searches for.

Run (from repo root, after ``pip install -e ".[dev]"``):

    python examples/bring_your_own_world.py
    python examples/bring_your_own_world.py --export-replay artifacts/byow_replay.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from fragility_engine.adversary.encoding import decode_schedule, schedule_attack_cost
from fragility_engine.adversary.search import genetic_search
from fragility_engine.explain.minimal_collapse import minimize_schedule_with_rollout
from fragility_engine.runner import rollout_to_replay_dict, summarize_findings
from fragility_engine.types import ExogenousEvent, RolloutResult, TrajectoryStep

# ---------------------------------------------------------------------------
# 1. The world — this is the part YOU write for your own system.
#
# Contract (fragility_engine.world.base.WorldProtocol):
#   reset()               -> put the world back in a known start state
#   step(events, rng)     -> advance one timestep, return a TrajectoryStep
#   state_vector()        -> np.ndarray snapshot for logging / attribution
#   instability_score()   -> float, higher = closer to failure
#   is_collapsed()        -> bool, True ends the rollout
# Plus a ``max_steps`` attribute for the rollout loop.
#
# Determinism rule: use ONLY the rng passed into step() for randomness (this
# world is fully deterministic and ignores it). Hidden RNG breaks replays.
# ---------------------------------------------------------------------------


@dataclass
class CapacityPoolWorld:
    """Bounded allocation pool under demand surges and allocation leaks."""

    capacity: float = 1.0  # normalized pool size
    base_demand: float = 0.05  # steady-state allocation requests per step
    release_rate: float = 0.25  # fraction of active allocations released per step
    base_leak: float = 0.02  # fraction of releases stranded even in calm conditions
    surge_gain: float = 0.50  # reserve_loss magnitude -> extra demand this step
    leak_gain: float = 0.85  # rumor magnitude -> extra leak fraction this step
    orphan_ttl: int = 8  # stranded units are reclaimed after this many steps
    collapse_free_floor: float = 0.05  # collapse when free pool falls to this
    denial_collapse: float = 0.35  # collapse when one step denies this much demand (allocation outage)
    max_steps: int = 24

    _active: float = 0.0
    _orphans: list[tuple[int, float]] = field(default_factory=list)  # (reclaim_at, amount)
    _denied_last: float = 0.0
    _timestep: int = 0

    def reset(self, *, initial_active: float = 0.15) -> None:
        self._active = float(np.clip(initial_active, 0.0, self.capacity))
        self._orphans = []
        self._denied_last = 0.0
        self._timestep = 0

    # -- helpers -----------------------------------------------------------
    def _orphaned_total(self) -> float:
        return float(sum(amount for _, amount in self._orphans))

    def _free(self) -> float:
        return float(max(0.0, self.capacity - self._active - self._orphaned_total()))

    # -- WorldProtocol -----------------------------------------------------
    def state_vector(self) -> np.ndarray:
        return np.array(
            [self._active, self._orphaned_total(), self._free(), self._denied_last, float(self._timestep)],
            dtype=np.float64,
        )

    def instability_score(self) -> float:
        utilization = (self._active + self._orphaned_total()) / max(self.capacity, 1e-9)
        denial_pressure = self._denied_last / max(self.base_demand, 1e-9)
        return float(0.6 * min(utilization, 1.0) + 0.4 * min(denial_pressure, 2.5))

    def is_collapsed(self) -> bool:
        # Two failure faces of the same wedge: the pool is pinned (no free units
        # survive the release phase) or a demand spike hit a pool with no
        # headroom and bounced (an allocation outage from the client's view).
        return bool(self._free() <= self.collapse_free_floor or self._denied_last >= self.denial_collapse)

    def step(self, events: tuple[ExogenousEvent, ...], rng: np.random.Generator) -> TrajectoryStep:
        # Decode this step's shocks. The kind vocabulary is fixed by the engine
        # ("reserve_loss" / "rumor"); what they MEAN is up to your world.
        surge = 0.0
        leak_frac = self.base_leak
        for ev in events:
            mag = float(np.clip(ev.magnitude, 0.0, 1.0))
            if ev.kind == "reserve_loss":
                surge += self.surge_gain * mag
            elif ev.kind == "rumor":
                leak_frac = min(0.95, leak_frac + self.leak_gain * mag)

        # Reclaim stranded allocations whose timeout expired.
        self._orphans = [(t, amt) for (t, amt) in self._orphans if t > self._timestep]

        # Serve allocation demand from the free pool; excess demand is denied.
        demand = self.base_demand + surge
        granted = min(demand, self._free())
        self._denied_last = float(demand - granted)
        self._active += granted

        # Release a fraction of active allocations; a leak_frac portion is
        # stranded (holds pool units until orphan_ttl expires).
        released = self.release_rate * self._active
        self._active -= released
        leaked = leak_frac * released
        if leaked > 1e-12:
            self._orphans.append((self._timestep + self.orphan_ttl, float(leaked)))

        metrics = {
            "free_fraction": self._free() / max(self.capacity, 1e-9),
            "orphaned": self._orphaned_total(),
            "denied": self._denied_last,
            "instability": float(self.instability_score()),
        }
        t = self._timestep
        self._timestep += 1
        return TrajectoryStep(
            timestep=t,
            state_vector=self.state_vector(),
            events=events,
            agent_actions_summary={},
            metrics=metrics,
        )


# ---------------------------------------------------------------------------
# 2. The rollout function — genome in, RolloutResult out.
#
# This mirrors fragility_engine.runner rollouts: decode the genome into a shock
# schedule, replay it step by step, track peak/integral instability. Once this
# exists, every search/minimize/replay tool accepts it unchanged.
# ---------------------------------------------------------------------------


def rollout_capacity_pool(
    world: CapacityPoolWorld,
    genome: np.ndarray,
    *,
    seed: int,
    initial_active: float = 0.15,
) -> RolloutResult:
    world.reset(initial_active=initial_active)
    schedule = decode_schedule(genome)
    attack_cost = schedule_attack_cost(schedule)

    trajectory: list[TrajectoryStep] = []
    collapsed = False
    collapse_timestep: int | None = None
    peak_instability = 0.0
    integral_instability = 0.0

    for t in range(world.max_steps):
        events = schedule.get(t, ())
        step_rng = np.random.default_rng(seed + 17 * (t + 1))
        step = world.step(events, step_rng)
        trajectory.append(step)
        inst = float(step.metrics["instability"])
        peak_instability = max(peak_instability, inst)
        integral_instability += inst
        if world.is_collapsed():
            collapsed = True
            collapse_timestep = t
            break

    return RolloutResult(
        trajectory=trajectory,
        collapsed=collapsed,
        collapse_timestep=collapse_timestep,
        final_instability=peak_instability,
        seed=seed,
        attack_cost=attack_cost,
        simulation_mode="capacity_pool_example",
        integral_instability=integral_instability,
    )


# ---------------------------------------------------------------------------
# 3. Search + minimization + replay — all engine-provided from here down.
# ---------------------------------------------------------------------------


def main() -> None:
    p = argparse.ArgumentParser(description="Bring-your-own-world tutorial: GA search on a custom capacity pool.")
    p.add_argument("--generations", type=int, default=12)
    p.add_argument("--population-size", type=int, default=24)
    p.add_argument("--seed", type=int, default=411)
    p.add_argument("--horizon", type=int, default=16)
    p.add_argument("--export-replay", type=Path, default=None, help="Write best-rollout replay JSON.")
    args = p.parse_args()

    world = CapacityPoolWorld()

    def evaluator(genome: np.ndarray, seed: int) -> RolloutResult:
        return rollout_capacity_pool(world, genome, seed=seed)

    search = genetic_search(
        evaluator,
        horizon=int(args.horizon),
        generations=int(args.generations),
        population_size=int(args.population_size),
        seed=int(args.seed),
    )

    print("=== best schedule found ===")
    print(summarize_findings(search.best_rollout))
    print()
    print("decoded shocks (timestep -> kind, magnitude):")
    for t, events in sorted(decode_schedule(search.best_genome).items()):
        for e in events:
            print(f"  t={t:>2}  {e.kind:<12} mag={e.magnitude:.3f}")

    minimized, min_rollout = minimize_schedule_with_rollout(search.best_genome, evaluator, base_seed=515151)
    print()
    print("=== greedy minimization (smallest schedule that still collapses) ===")
    if min_rollout is None:
        print("baseline did not collapse; nothing to minimize")
    else:
        kept = minimized.get("minimal_events_by_timestep", {})
        print(f"kept {len(kept)} shock timesteps (still collapses at t={minimized.get('collapse_timestep')}):")
        for t, events in sorted(kept.items(), key=lambda kv: int(kv[0])):
            for e in events:
                print(f"  t={int(t):>2}  {e['kind']:<12} mag={e['magnitude']:.3f}")

    if args.export_replay is not None:
        replay = rollout_to_replay_dict(search.best_rollout)
        replay["meta"] = {
            "cli": "examples/bring_your_own_world",
            "note": "tutorial artifact - custom world outside the reference domain charter",
            "horizon": int(args.horizon),
            "ga_seed": int(args.seed),
        }
        args.export_replay.parent.mkdir(parents=True, exist_ok=True)
        args.export_replay.write_text(json.dumps(replay, indent=2), encoding="utf-8")
        print(f"\nwrote replay: {args.export_replay}")


if __name__ == "__main__":
    main()
