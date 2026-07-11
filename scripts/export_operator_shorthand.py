#!/usr/bin/env python3
"""Export FDE operator Intelligence Shorthand corpus (Chrysalis-inspired)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fragility_engine.shorthand.resolve import export_corpus


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/operator_shorthand/fde-shorthands.v1.json"),
    )
    args = p.parse_args()
    corpus = export_corpus()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(corpus, indent=2), encoding="utf-8")
    print(f"wrote {args.out} ({len(corpus['shorthands'])} capsules)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
