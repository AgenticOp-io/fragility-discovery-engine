"""Process-pool GA on picklable Phase H bundle rollout (Windows spawn-safe pattern)."""

from __future__ import annotations

from functools import partial

import numpy as np

from fragility_engine.adversary.search import genetic_search
from fragility_engine.benchmarks.suite import PINNED_SCHEDULE_HORIZON, rollout_bundle_with_genome


def test_genetic_search_process_pool_matches_threads_on_bundle():
    rollout = partial(rollout_bundle_with_genome, "aggregate_rollout_v1", isolate=True)
    kwargs = dict(horizon=PINNED_SCHEDULE_HORIZON, generations=2, population_size=8, seed=30303)
    st = genetic_search(rollout, eval_workers=2, eval_pool="threads", **kwargs)
    pr = genetic_search(rollout, eval_workers=2, eval_pool="processes", **kwargs)
    assert np.allclose(st.best_genome, pr.best_genome)
    assert st.best_fitness == pr.best_fitness
