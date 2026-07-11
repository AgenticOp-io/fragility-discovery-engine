# Bring your own world

The six reference domains are deliberately toy models — they demonstrate the engine, they do not model your system. **All of the engine's value on a real problem comes from a world *you* write.** This page shows that the world is a small adapter, not a research project: four methods and a rollout function, and every search, minimization, attribution, and replay tool works unchanged.

Runnable companions:

| Example | Module | CLI |
|---------|--------|-----|
| Capacity pool | `fragility_engine.byow.examples.capacity_pool` | `fragility search --example capacity-pool` |
| Token bucket | `fragility_engine.byow.examples.token_bucket` | `fragility search --example token-bucket` |
| Ranked store (falsify) | `fragility_engine.falsify.examples.ranked_store` | `fragility falsify search --example ranked-store` |

Scripts: [`../examples/bring_your_own_world.py`](../examples/bring_your_own_world.py), [`../examples/token_bucket_demo.py`](../examples/token_bucket_demo.py), [`../examples/falsification_ranked_store.py`](../examples/falsification_ranked_store.py).

Installable tutorial worlds live in **`fragility_engine.byow.examples`** — not charter reference domains.

---

## Is it worth wiring up? (the one-day test)

Before writing anything, apply this bar:

> The engine earns its keep only when the worst-case **ordering** of shocks is non-obvious — when the damage comes from a combinatorial interaction (timing × decay × capacity) you would not have predicted. If the search just rediscovers "everything at once is bad," you already knew that, and the engine added nothing.

The honest way to find out costs about a day:

1. Pick the failure you keep hitting in production — the one whose dynamics you already understand from incidents.
2. Write it as a ~100-line discrete-time sim (the contract below).
3. Run the GA against it and read the minimized schedule.
4. If the minimized schedule surprises you, the engine has earned a second subsystem. If it replays the obvious, you spent a day and learned this tool is not for that problem.

Good candidates share three properties: **resettable** (you can reconstruct a known start state), **steppable** (state advances in discrete ticks), and **non-obvious interaction** (at least two coupled mechanisms — a leak *and* a surge, a timeout *and* a queue — whose phasing matters).

---

## The contract (what you write)

A world is any object satisfying `fragility_engine.world.base.WorldProtocol` plus `reset()` and a `max_steps` attribute:

| Member | Role |
|--------|------|
| `reset(**kwargs)` | Restore the known start state. Every rollout begins here. |
| `step(events, rng) -> TrajectoryStep` | Advance one tick under this step's shocks. |
| `state_vector() -> np.ndarray` | Numeric snapshot for logging and attribution. |
| `instability_score() -> float` | Higher = closer to failure. Drives fitness. |
| `is_collapsed() -> bool` | `True` ends the rollout — your damage definition. |
| `max_steps` | Rollout horizon. |

Two rules keep replays trustworthy:

1. **Determinism** — use only the `rng` passed into `step()` for randomness (or none at all). Hidden RNG or wall-clock reads break replay JSON.
2. **World/adversary separation** — shocks enter only through `events`. Do not encode attacker logic inside the physics ([`BOUNDARIES.md`](../BOUNDARIES.md)).

The shock *vocabulary* is fixed by the encoding (`reserve_loss`, `rumor` — see `fragility_engine.adversary.encoding`); what the kinds **mean** is up to your world. Treat them as two orthogonal stress axes and document your mapping. In the example below: `reserve_loss` = demand surge, `rumor` = leak condition.

## The example: a bounded capacity pool

[`examples/bring_your_own_world.py`](../examples/bring_your_own_world.py) models the classic ops failure shape shared by connection pools, address pools, worker pools, and license pools:

- Clients allocate units from a fixed pool; a fraction of active allocations release each step.
- **Demand surges** (`reserve_loss`) add allocation requests; excess over free capacity is denied.
- **Leak conditions** (`rumor`) strand a fraction of released units, which hold capacity until a timeout (`orphan_ttl`) reclaims them.
- **Collapse** = the free pool is pinned below a floor, or a single step denies more than `denial_collapse` worth of demand (an allocation outage).

No single mechanism is fatal: leaks come back after the TTL, and surges are absorbed when there is headroom. The wedge is the *phasing*, which is what the search finds. A typical minimized schedule from the GA:

```text
kept 6 shock timesteps (still collapses at t=12):
  t= 6  reserve_loss mag=0.714   <- fill the pool
  t= 8  reserve_loss mag=0.758   <- keep it full
  t= 9  rumor        mag=0.989   <- strand released units while volume is high
  t=10  rumor        mag=1.000
  t=11  reserve_loss mag=0.787   <- surge into a pool the leaks have pinned
  t=12  reserve_loss mag=1.000   <- denied demand exceeds the outage threshold
```

Surge first, *then* leak, *then* surge again — leaking early wastes the TTL window, surging without a prior leak gets absorbed. That ordering constraint is the kind of result that justifies the wiring; if your world's minimized schedule carries no such structure, see the one-day test above.

## The rollout function (genome → RolloutResult)

The search loop only needs `rollout_fn(genome, seed) -> RolloutResult`. The pattern is ~30 lines and identical for every world (compare `fragility_engine.runner`):

```python
def rollout_my_world(world, genome, *, seed):
    world.reset()
    schedule = decode_schedule(genome)            # genome -> {timestep: events}
    attack_cost = schedule_attack_cost(schedule)  # abstract budget units

    trajectory, collapsed, collapse_t = [], False, None
    peak = integral = 0.0
    for t in range(world.max_steps):
        step = world.step(schedule.get(t, ()), np.random.default_rng(seed + 17 * (t + 1)))
        trajectory.append(step)
        inst = float(step.metrics["instability"])
        peak = max(peak, inst)
        integral += inst
        if world.is_collapsed():
            collapsed, collapse_t = True, t
            break

    return RolloutResult(
        trajectory=trajectory, collapsed=collapsed, collapse_timestep=collapse_t,
        final_instability=peak, seed=seed, attack_cost=attack_cost,
        simulation_mode="my_world_v1", integral_instability=integral,
    )
```

Include an `"instability"` key in each step's `metrics` and pick a stable `simulation_mode` string — replay tooling branches on it.

## What you get for free

Once the rollout function exists, the engine side is done:

| Tool | Call |
|------|------|
| GA / Monte Carlo search | `genetic_search(rollout_fn, horizon=…, …)` / `monte_carlo_search(…)` from `fragility_engine.adversary.search` |
| Minimal failing schedule | `minimize_schedule_with_rollout(best_genome, rollout_fn, base_seed=…)` from `fragility_engine.explain.minimal_collapse` |
| Shock-kind ablation | `ablate_event_kind(…)` from the same module |
| Replay JSON (viewer-compatible) | `rollout_to_replay_dict(result)` from `fragility_engine.runner` |
| Cost/damage Pareto archive | pass `collect_pareto=True` to either search |

Run the whole pipeline:

```powershell
pip install -e ".[dev]"
fragility search --example capacity-pool --export-replay artifacts/byow_replay.json
fragility minimize --example capacity-pool --export-replay artifacts/byow_min.json
fragility check-world --example token-bucket
# Falsification (predicate damage): docs/FALSIFICATION_HARNESS.md
fragility falsify search --example ranked-store --export-replay artifacts/falsify_replay.json
```

Legacy script: `python examples/bring_your_own_world.py`

---

## Beyond simulations: the falsification-harness pattern

Nothing in the contract says "world" must mean *physics*. The engine is, generically, an adversarial search over perturbation sequences against any system that can **reset**, **step**, and **report damage**. That admits a second use: red-teaming a system's *invariants* instead of simulating its dynamics.

The mapping:

| World contract | Falsification harness |
|----------------|----------------------|
| `reset()` | Restore a snapshot (database dump, git state, container image) |
| `step(events, rng)` | Apply one operation — an ingest, a request, a config change — where `events` parameterize the adversarial part |
| `instability_score()` | Distance-to-violation heuristic (0 if you have none; collapse still drives the search) |
| `is_collapsed()` | **A claim predicate returning `True` when an invariant you defend is violated** |

Damage as a predicate is the key move. Instead of "reserves hit zero," collapse can be *"the retrieval layer failed to return a record that should be findable,"* *"a stale entry outranked a fresh one that contradicts it,"* or *"an access-control check passed that should have failed."* If you currently defend such claims with a handful of manual spot checks, a schedule search is a machine for finding the cheapest input sequence that breaks one — and the replay JSON is a reproducible bug report when it does.

See [`FALSIFICATION_HARNESS.md`](FALSIFICATION_HARNESS.md) for the full predicate-harness pattern and CLI.
