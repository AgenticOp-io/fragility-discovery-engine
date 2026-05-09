"""Smoke + GA on the graph contagion world."""

from __future__ import annotations

import json

from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.network.topology import adjacency_erdos_renyi
from fragility_engine.runner import rollout_stablecoin_network, rollout_to_replay_dict
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld, default_whale_weights


def main() -> None:
    n = 48
    adj = adjacency_erdos_renyi(n, p=0.12, seed=2026)
    weights = default_whale_weights(n, whale_index=0, whale_frac=0.24)
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=adj,
        node_weights=weights,
        contagion_beta=0.38,
        max_steps=40,
    )
    horizon = 20

    def evaluator(genome: np.ndarray, seed: int):
        return rollout_stablecoin_network(template, genome, seed=seed)

    ga = genetic_search(evaluator, horizon=horizon, generations=10, population_size=20, seed=131)
    replay = rollout_to_replay_dict(ga.best_rollout)
    print(json.dumps({"best_fitness": ga.best_fitness, "replay_summary": replay["trajectory"][-1]}, indent=2))


if __name__ == "__main__":
    main()
