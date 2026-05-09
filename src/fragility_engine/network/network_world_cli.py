"""Build ``StablecoinNetworkWorld`` from CLI-style topology flags (import from this submodule)."""

from __future__ import annotations

from pathlib import Path

from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.network.graph_cli import contagion_graph_from_cli
from fragility_engine.network.neighbor_io import load_neighbor_topology
from fragility_engine.world.stablecoin_network import (
    StablecoinNetworkWorld,
    default_whale_weights,
    neighbor_lists_topology_meta,
)


def build_stablecoin_network_world_cli(
    *,
    neighbor_json: Path | None,
    neighbor_weights_json: Path | None,
    nodes: int,
    graph_kind: str,
    graph_seed: int,
    er_p: float,
    ws_k: int,
    ws_p: float,
    beta: float,
    whale_frac: float,
    max_steps: int,
) -> tuple[StablecoinNetworkWorld, dict | None]:
    """
    Shared by CLIs that need a network world + JSON-friendly topology meta.

    Raises ``ValueError`` / ``OSError`` / ``json.JSONDecodeError`` from neighbor I/O or graph CLI.
    """

    if neighbor_json is not None:
        nl, nw = load_neighbor_topology(
            Path(neighbor_json),
            Path(neighbor_weights_json) if neighbor_weights_json else None,
        )
        n = len(nl)
        weights = default_whale_weights(n, whale_index=0, whale_frac=float(whale_frac))
        template = StablecoinNetworkWorld(
            population=default_stablecoin_population(),
            neighbor_lists=nl,
            neighbor_weights=nw,
            node_weights=weights,
            contagion_beta=float(beta),
            max_steps=int(max_steps),
        )
        topo = neighbor_lists_topology_meta(nl, weighted=nw is not None)
        return template, topo

    graph, gen_meta = contagion_graph_from_cli(
        graph_kind=str(graph_kind),
        nodes=int(nodes),
        graph_seed=int(graph_seed),
        er_p=float(er_p),
        ws_k=int(ws_k),
        ws_p=float(ws_p),
    )
    n = int(nodes)
    weights = default_whale_weights(n, whale_index=0, whale_frac=float(whale_frac))
    template = StablecoinNetworkWorld(
        population=default_stablecoin_population(),
        adjacency=graph,
        node_weights=weights,
        contagion_beta=float(beta),
        max_steps=int(max_steps),
    )
    topo = {
        **gen_meta,
        "undirected_edges": graph.undirected_edge_count(),
        "storage": "dense_adjacency",
    }
    return template, topo
