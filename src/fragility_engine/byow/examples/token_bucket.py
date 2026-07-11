"""Tutorial world: token bucket with arrival bursts and drain shocks."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fragility_engine.byow.rollout import run_rollout
from fragility_engine.types import ExogenousEvent, RolloutResult, TrajectoryStep

SIMULATION_MODE = "token_bucket_example"


@dataclass
class TokenBucketWorld:
    """
    Tokens refill each step up to ``capacity``; arrivals consume tokens.

    ``reserve_loss`` = arrival burst; ``rumor`` = drain / processing slowdown.
    Collapse when the bucket empties during a step or queue backlog exceeds limit.
    """

    capacity: float = 1.0
    refill_rate: float = 0.12
    base_arrival: float = 0.04
    burst_gain: float = 0.55
    drain_gain: float = 0.40
    queue_limit: float = 0.45
    max_steps: int = 22

    _tokens: float = 0.0
    _queue: float = 0.0
    _timestep: int = 0

    def reset(self, *, initial_tokens: float = 0.6) -> None:
        self._tokens = float(np.clip(initial_tokens, 0.0, self.capacity))
        self._queue = 0.0
        self._timestep = 0

    def state_vector(self) -> np.ndarray:
        return np.array([self._tokens, self._queue, float(self._timestep)], dtype=np.float64)

    def instability_score(self) -> float:
        util = 1.0 - self._tokens / max(self.capacity, 1e-9)
        qnorm = self._queue / max(self.queue_limit, 1e-9)
        return float(0.55 * min(util, 1.0) + 0.45 * min(qnorm, 2.0))

    def is_collapsed(self) -> bool:
        return bool(self._queue >= self.queue_limit or self._tokens <= 1e-6)

    def step(self, events: tuple[ExogenousEvent, ...], rng: np.random.Generator) -> TrajectoryStep:
        del rng
        arrival = self.base_arrival
        drain = 0.0
        for ev in events:
            mag = float(np.clip(ev.magnitude, 0.0, 1.0))
            if ev.kind == "reserve_loss":
                arrival += self.burst_gain * mag
            elif ev.kind == "rumor":
                drain += self.drain_gain * mag

        self._tokens = min(self.capacity, self._tokens + self.refill_rate)
        self._tokens = max(0.0, self._tokens - drain)

        served = min(arrival, self._tokens)
        self._tokens -= served
        self._queue = max(0.0, self._queue * 0.85 + (arrival - served))

        metrics = {
            "tokens": self._tokens,
            "queue": self._queue,
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


def make_world() -> TokenBucketWorld:
    return TokenBucketWorld()


def rollout(world: TokenBucketWorld, genome: np.ndarray, seed: int) -> RolloutResult:
    return run_rollout(
        world,
        genome,
        seed=seed,
        simulation_mode=SIMULATION_MODE,
        reset=lambda: world.reset(initial_tokens=0.6),
    )
