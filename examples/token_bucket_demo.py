"""Token bucket BYOW tutorial — prefer ``fragility search --example token-bucket``."""

from __future__ import annotations

from fragility_engine.cli.main import main


def _entry() -> int:
    import sys

    return main(["search", "--example", "token-bucket", *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(_entry())
