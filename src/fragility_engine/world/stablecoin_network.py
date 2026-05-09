from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fragility_engine.agents.stablecoin_agents import AgentPopulation
from fragility_engine.network.contagion import contagion_step
from fragility_engine.types import ExogenousEvent, TrajectoryStep


@dataclass
class StablecoinNetworkWorld:
    """
    Global reserves/supply with **per-node panic** on a contagion graph.

    Redemption demand is a weighted average of per-node demands; each node observes the
    same global price but **local panic**. Optional whale concentrates weights on early indices.
    """

    population: AgentPopulation
    adjacency: np.ndarray
    node_weights: np.ndarray
    contagion_beta: float = 0.35
    depeg_threshold: float = 0.94
    panic_decay: float = 0.15
    rumor_panic_gain: float = 0.35
    max_steps: int = 48
    _panic: np.ndarray | None = None
    _reserves: float = 0.0
    _supply: float = 0.0
    _timestep: int = 0

    def __post_init__(self) -> None:
        self.adjacency = np.asarray(self.adjacency, dtype=np.int8)
        nw = np.asarray(self.node_weights, dtype=np.float64)
        self.node_weights = nw / np.maximum(nw.sum(), 1e-12)

    def reset(self, initial_reserves: float, initial_supply: float, base_panic: float = 0.05) -> None:
        n = int(self.adjacency.shape[0])
        self._reserves = float(initial_reserves)
        self._supply = float(initial_supply)
        self._timestep = 0
        self._panic = np.full(n, float(base_panic), dtype=np.float64)

    def state_vector(self) -> np.ndarray:
        p = self._require_panic()
        price = self._price()
        return np.array(
            [
                self._reserves,
                self._supply,
                price,
                float(np.mean(p)),
                float(np.max(p)),
                float(np.std(p)),
                float(self._timestep),
            ],
            dtype=np.float64,
        )

    def instability_score(self) -> float:
        price = self._price()
        mean_p = float(np.mean(self._require_panic()))
        depeg_penalty = max(0.0, self.depeg_threshold - price)
        reserve_ratio = price
        contagion_spread = float(np.std(self._require_panic()))
        return float(mean_p + 2.0 * depeg_penalty + max(0.0, 1.0 - reserve_ratio) + 0.5 * contagion_spread)

    def is_collapsed(self) -> bool:
        price = self._price()
        return bool(self._reserves <= 1e-6 or price < self.depeg_threshold)

    def step(self, events: tuple[ExogenousEvent, ...], rng: np.random.Generator) -> TrajectoryStep:
        p = self._require_panic()
        n = p.shape[0]

        for ev in events:
            if ev.kind == "reserve_loss":
                loss = float(np.clip(ev.magnitude, 0.0, 1.0))
                self._reserves *= 1.0 - loss
            elif ev.kind == "rumor":
                bump = self.rumor_panic_gain * float(np.clip(ev.magnitude, 0.0, 1.0))
                k = max(1, int(np.ceil(float(ev.magnitude) * n)))
                targeted = np.arange(min(k, n))
                p[targeted] = np.clip(p[targeted] + bump, 0.0, 1.0)

        p[:] = contagion_step(p, self.adjacency, self.contagion_beta)

        price = self._price()
        global_obs = {
            "reserves": self._reserves,
            "supply": self._supply,
            "panic": float(np.dot(self.node_weights, p)),
            "price": price,
            "timestep": self._timestep,
        }

        redeem_fraction = 0.0
        for i in range(n):
            obs_i = {**global_obs, "panic": float(p[i])}
            redeem_fraction += float(
                self.node_weights[i] * self.population.aggregate_redeem_fraction(obs_i, rng)
            )

        redeem_fraction = float(np.clip(redeem_fraction, 0.0, 1.0))
        redeem_amount = redeem_fraction * self._supply
        paid = min(redeem_amount, self._reserves)
        self._supply -= paid
        self._reserves -= paid

        p[:] = np.clip(p * (1.0 - self.panic_decay), 0.0, 1.0)

        metrics = {
            "price": float(self._price()),
            "backing_ratio": float(self._price()),
            "redeem_fraction": redeem_fraction,
            "paid_out": float(paid),
            "panic_mean": float(np.mean(p)),
            "panic_max": float(np.max(p)),
            "panic_std": float(np.std(p)),
            "instability": float(self.instability_score()),
        }

        self._timestep += 1
        return TrajectoryStep(
            timestep=self._timestep - 1,
            state_vector=self.state_vector(),
            events=events,
            agent_actions_summary={
                "aggregate_redeem_fraction": redeem_fraction,
                "panic_mean": metrics["panic_mean"],
                "panic_std": metrics["panic_std"],
            },
            metrics=metrics,
        )

    def _price(self) -> float:
        return float(self._reserves / max(self._supply, 1e-9))

    def _require_panic(self) -> np.ndarray:
        if self._panic is None:
            raise RuntimeError("Network world not initialized; call reset() first.")
        return self._panic


def default_whale_weights(n: int, whale_index: int = 0, whale_frac: float = 0.22) -> np.ndarray:
    w = np.full(n, (1.0 - whale_frac) / max(n - 1, 1), dtype=np.float64)
    if n > 0:
        w[whale_index] = whale_frac
    if n == 1:
        w[...] = 1.0
    return w
