"""Phase H bundle search evaluator isolation + determinism."""

from __future__ import annotations

import numpy as np

from fragility_engine.adversary.search import genetic_search
from fragility_engine.benchmarks.suite import BUNDLE_IDS, PINNED_SCHEDULE_HORIZON, bundle_search_evaluator


def test_bundle_search_evaluator_genetic_workers_match_for_each_bundle():
    kwargs = dict(horizon=PINNED_SCHEDULE_HORIZON, generations=2, population_size=8, seed=120_120)
    for bid in BUNDLE_IDS:
        ev1 = bundle_search_evaluator(bid, eval_workers=1)
        ev4 = bundle_search_evaluator(bid, eval_workers=4)
        s1 = genetic_search(ev1, eval_workers=1, **kwargs)
        s4 = genetic_search(ev4, eval_workers=4, **kwargs)
        assert np.allclose(s1.best_genome, s4.best_genome), bid
        assert s1.best_fitness == s4.best_fitness, bid
