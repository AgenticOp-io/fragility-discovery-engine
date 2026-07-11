"""Ranked-store falsification tutorial — prefer ``fragility falsify search``."""

from __future__ import annotations

from fragility_engine.cli.main import main


def _entry() -> int:
    import sys

    return main(["falsify", "search", "--example", "ranked-store", *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(_entry())
