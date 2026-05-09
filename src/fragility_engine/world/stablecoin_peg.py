from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fragility_engine.agents.stablecoin_agents import AgentPopulation
from fragility_engine.types import ExogenousEvent, TrajectoryStep


@dataclass
class StablecoinState:
    """Toy peg-defense pool: backing ratio drives fear; redemptions drain reserves."""

    reserves: float
    supply: float
    panic: float
    timestep: int


@dataclass
class StablecoinPegWorld:
    """
    Highly simplified stablecoin stress model (research toy, not market calibrated).

    - Price proxy: reserves / supply
    - Collapse: backing falls below `depeg_threshold` OR reserves exhausted
    - Agents pull fractional redemption demand based on archetypes
    """

    population: AgentPopulation
    depeg_threshold: float = 0.94
    panic_decay: float = 0.15
    rumor_panic_gain: float = 0.35
    max_steps: int = 48
    _state: StablecoinState | None = None

    def reset(self, initial_reserves: float, initial_supply: float, initial_panic: float = 0.05) -> None:
        self._state = StablecoinState(
            reserves=float(initial_reserves),
            supply=float(initial_supply),
            panic=float(initial_panic),
            timestep=0,
        )
        # Caller should invoke `population.reset(...)` with a seeded RNG for reproducibility.

    def state_vector(self) -> np.ndarray:
        s = self._require_state()
        price = s.reserves / max(s.supply, 1e-9)
        return np.array([s.reserves, s.supply, price, s.panic, float(s.timestep)], dtype=np.float64)

    def instability_score(self) -> float:
        s = self._require_state()
        price = s.reserves / max(s.supply, 1e-9)
        depeg_penalty = max(0.0, self.depeg_threshold - price)
        reserve_ratio = s.reserves / max(s.supply, 1e-9)
        return float(s.panic + 2.0 * depeg_penalty + max(0.0, 1.0 - reserve_ratio))

    def is_collapsed(self) -> bool:
        s = self._require_state()
        price = s.reserves / max(s.supply, 1e-9)
        return bool(s.reserves <= 1e-6 or price < self.depeg_threshold)

    def step(self, events: tuple[ExogenousEvent, ...], rng: np.random.Generator) -> TrajectoryStep:
        s = self._require_state()

        # Exogenous shocks (world interprets physics only).
        for ev in events:
            if ev.kind == "reserve_loss":
                loss = float(np.clip(ev.magnitude, 0.0, 1.0))
                s.reserves *= 1.0 - loss
            elif ev.kind == "rumor":
                bump = self.rumor_panic_gain * float(np.clip(ev.magnitude, 0.0, 1.0))
                s.panic = float(np.clip(s.panic + bump, 0.0, 1.0))

        # Agent redemption cycle.
        observation = {
            "reserves": s.reserves,
            "supply": s.supply,
            "panic": s.panic,
            "price": s.reserves / max(s.supply, 1e-9),
            "timestep": s.timestep,
        }
        redeem_fraction = self.population.aggregate_redeem_fraction(observation, rng)
        redeem_fraction = float(np.clip(redeem_fraction, 0.0, 1.0))
        redeem_amount = redeem_fraction * s.supply

        paid = min(redeem_amount, s.reserves)
        s.supply -= paid
        s.reserves -= paid

        # Panic decay after actions.
        s.panic = float(np.clip(s.panic * (1.0 - self.panic_decay), 0.0, 1.0))

        metrics = {
            "price": float(s.reserves / max(s.supply, 1e-9)),
            "backing_ratio": float(s.reserves / max(s.supply, 1e-9)),
            "redeem_fraction": redeem_fraction,
            "paid_out": float(paid),
        }

        s.timestep += 1
        step = TrajectoryStep(
            timestep=s.timestep - 1,
            state_vector=self.state_vector(),
            events=events,
            agent_actions_summary={"aggregate_redeem_fraction": redeem_fraction},
            metrics=metrics,
        )
        return step

    def _require_state(self) -> StablecoinState:
        if self._state is None:
            raise RuntimeError("World not initialized; call reset() before stepping.")
        return self._state
