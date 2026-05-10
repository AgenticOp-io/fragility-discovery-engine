"""Batch evaluation helpers for independent deterministic rollouts (Phase K).

``ThreadPoolExecutor.map`` preserves **input order** in the returned list. Each ``fn(item)`` should
avoid mutating **shared mutable simulation state** (notably
:class:`~fragility_engine.agents.stablecoin_agents.AgentPopulation` on a reused world template): clones
share ``population`` by reference. Prefer constructing a **fresh**
world inside ``fn``, or serialize tasks so one template is never advanced concurrently.

This module does **not** change search semantics; it is an optional scheduling convenience.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


def thread_pool_map_ordered(fn: Callable[[T], R], items: Sequence[T], *, max_workers: int | None = None) -> list[R]:
    """
    Run ``fn`` over ``items`` in a thread pool; results align with ``items`` indices.

    Uses at least one worker; caps workers by pool default when ``max_workers`` is ``None``.
    For empty ``items``, returns ``[]`` without spawning threads.
    """

    if not items:
        return []
    n = len(items)
    if max_workers is None:
        workers = min(32, n + 4)
    else:
        workers = max_workers
    workers = max(1, min(workers, n))
    if workers == 1:
        return [fn(x) for x in items]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))


def process_pool_map_ordered(fn: Callable[[T], R], items: Sequence[T], *, max_workers: int | None = None) -> list[R]:
    """
    Same ordering contract as :func:`thread_pool_map_ordered`, using ``ProcessPoolExecutor``.

    ``fn`` must be **pickle-safe** (typically a module-level function). Closures, lambdas, and
    bound methods often fail on Windows (spawn). Prefer threads (:func:`thread_pool_map_ordered`)
    for rollout closures unless profiling shows a win from multiprocessing.
    """

    from concurrent.futures import ProcessPoolExecutor

    if not items:
        return []
    n = len(items)
    if max_workers is None:
        workers = min(32, n + 4)
    else:
        workers = max_workers
    workers = max(1, min(workers, n))
    if workers == 1:
        return [fn(x) for x in items]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))
