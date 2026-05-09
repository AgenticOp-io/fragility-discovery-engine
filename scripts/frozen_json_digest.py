"""SHA-256 fingerprints for frozen JSON artifacts (Phase L citation helper)."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description="Print SHA-256 hex digest for each JSON file (stable bytes on disk).")
    ap.add_argument("paths", type=Path, nargs="+", help="JSON files to digest.")
    ap.add_argument("--json-out", type=Path, default=None, help="Write [{path, sha256}, ...] JSON.")
    args = ap.parse_args()

    rows: list[dict[str, str]] = []
    for p in args.paths:
        try:
            raw = p.read_bytes()
        except OSError as e:
            print(f"{p}: {e}", file=sys.stderr)
            raise SystemExit(2) from e
        h = hashlib.sha256(raw).hexdigest()
        rows.append({"path": str(p.resolve()), "sha256": h})
        print(f"{h}  {p}")

    if args.json_out is not None:
        payload = {"schema": "frozen-json-digest-v1", "files": rows}
        args.json_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
