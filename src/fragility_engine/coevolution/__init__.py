from fragility_engine.coevolution.defender import (
    build_defended_aggregate_world,
    build_defended_network_world,
    clone_stablecoin_network,
    decode_defender_genome,
    decode_defender_genome_params,
    random_defender_genome,
)

__all__ = [
    "alternating_coevolution",
    "alternating_coevolution_network",
    "alternating_coevolution_rollout",
    "build_defended_aggregate_world",
    "build_defended_network_world",
    "clone_stablecoin_network",
    "decode_defender_genome",
    "decode_defender_genome_params",
    "random_defender_genome",
]


def __getattr__(name: str):
    if name == "alternating_coevolution":
        from fragility_engine.coevolution.alternating import alternating_coevolution

        return alternating_coevolution
    if name == "alternating_coevolution_network":
        from fragility_engine.coevolution.alternating import alternating_coevolution_network

        return alternating_coevolution_network
    if name == "alternating_coevolution_rollout":
        from fragility_engine.coevolution.alternating import alternating_coevolution_rollout

        return alternating_coevolution_rollout
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
