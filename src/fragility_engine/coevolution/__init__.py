from fragility_engine.coevolution.defender import (
    build_defended_aggregate_world,
    decode_defender_genome,
    random_defender_genome,
)

__all__ = [
    "alternating_coevolution",
    "build_defended_aggregate_world",
    "decode_defender_genome",
    "random_defender_genome",
]


def __getattr__(name: str):
    if name == "alternating_coevolution":
        from fragility_engine.coevolution.alternating import alternating_coevolution

        return alternating_coevolution
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
