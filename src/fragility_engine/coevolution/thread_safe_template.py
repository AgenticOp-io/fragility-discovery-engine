"""World clones with a **fresh** default population for concurrent fitness evaluation.

Rollouts call ``population.reset(...)`` on shared-agent mixtures; reusing the same
:class:`~fragility_engine.agents.stablecoin_agents.AgentPopulation` across threads races.
These helpers copy scalar physics/topology from a template but swap in
``default_stablecoin_population()`` so each evaluation owns mutable agent state.
"""

from __future__ import annotations

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.coevolution.defender import (
    clone_liquidity_ladder,
    clone_resource_cascade,
    clone_service_backlog,
    clone_stablecoin_network,
)
from fragility_engine.world.liquidity_ladder import LiquidityLadderWorld
from fragility_engine.world.resource_cascade import ResourceCascadeWorld
from fragility_engine.world.service_backlog import ServiceBacklogWorld
from fragility_engine.world.stablecoin_network import StablecoinNetworkWorld
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld


def thread_safe_peg_clone(template: StablecoinPegWorld) -> StablecoinPegWorld:
    return StablecoinPegWorld(
        population=default_stablecoin_population(),
        depeg_threshold=float(template.depeg_threshold),
        panic_decay=float(template.panic_decay),
        rumor_panic_gain=float(template.rumor_panic_gain),
        max_steps=int(template.max_steps),
    )


def thread_safe_network_clone(template: StablecoinNetworkWorld) -> StablecoinNetworkWorld:
    return clone_stablecoin_network(template, population=default_stablecoin_population())


def thread_safe_resource_cascade_clone(template: ResourceCascadeWorld) -> ResourceCascadeWorld:
    return clone_resource_cascade(template, population=default_stablecoin_population())


def thread_safe_service_backlog_clone(template: ServiceBacklogWorld) -> ServiceBacklogWorld:
    return clone_service_backlog(template, population=default_stablecoin_population())


def thread_safe_liquidity_ladder_clone(template: LiquidityLadderWorld) -> LiquidityLadderWorld:
    return clone_liquidity_ladder(template, population=default_stablecoin_population())
