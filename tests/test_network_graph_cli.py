from __future__ import annotations

import pytest

from fragility_engine.network.graph_cli import contagion_graph_from_cli


def test_cli_erdos_renyi_shape():
    g, meta = contagion_graph_from_cli(
        graph_kind="erdos_renyi",
        nodes=15,
        graph_seed=3,
        er_p=0.2,
        ws_k=4,
        ws_p=0.1,
    )
    assert g.n_nodes == 15
    assert meta["kind"] == "erdos_renyi"


def test_cli_watts_strogatz_requires_even_k_and_k_lt_n():
    g, meta = contagion_graph_from_cli(
        graph_kind="watts_strogatz",
        nodes=12,
        graph_seed=1,
        er_p=0.1,
        ws_k=4,
        ws_p=0.2,
    )
    assert g.n_nodes == 12
    assert meta["kind"] == "watts_strogatz" and meta["k"] == 4

    with pytest.raises(ValueError, match="even"):
        contagion_graph_from_cli(
            graph_kind="watts_strogatz",
            nodes=12,
            graph_seed=1,
            er_p=0.1,
            ws_k=5,
            ws_p=0.2,
        )
    with pytest.raises(ValueError, match="nodes"):
        contagion_graph_from_cli(
            graph_kind="watts_strogatz",
            nodes=6,
            graph_seed=1,
            er_p=0.1,
            ws_k=6,
            ws_p=0.2,
        )
