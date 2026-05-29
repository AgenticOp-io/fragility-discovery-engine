#!/usr/bin/env python3
"""Build wheel/sdist and run twine check before a PyPI upload."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _project_version() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def _tag_version(tag: str) -> str:
    t = tag.strip()
    if t.startswith("v"):
        t = t[1:]
    if not re.fullmatch(r"\d+\.\d+\.\d+([a-zA-Z0-9.]+)?", t):
        raise SystemExit(f"tag does not look like a semver release: {tag!r}")
    return t


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tag", type=str, default=None, help="Optional git tag (e.g. v0.5.0) must match pyproject version.")
    ap.add_argument("--skip-build", action="store_true", help="Only twine-check existing dist/ (must exist).")
    args = ap.parse_args()

    version = _project_version()
    if args.tag:
        tv = _tag_version(args.tag)
        if tv != version:
            raise SystemExit(f"pyproject version {version!r} != tag {tv!r}")

    dist = ROOT / "dist"
    if not args.skip_build:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "build", "twine"], check=True)
        if dist.is_dir():
            for p in dist.iterdir():
                if p.is_file():
                    p.unlink()
        subprocess.run([sys.executable, "-m", "build"], cwd=ROOT, check=True)

    wheels = list(dist.glob("*.whl")) if dist.is_dir() else []
    sdists = list(dist.glob("*.tar.gz")) if dist.is_dir() else []
    if not wheels or not sdists:
        raise SystemExit(f"missing dist artifacts under {dist} (run without --skip-build)")

    for name in (wheels[0].name, sdists[0].name):
        if version not in name:
            raise SystemExit(f"dist filename {name!r} does not contain version {version!r}")

    artifacts = sorted(dist.glob("*.whl")) + sorted(dist.glob("*.tar.gz"))
    subprocess.run([sys.executable, "-m", "twine", "check", *[str(p) for p in artifacts]], cwd=ROOT, check=True)

    print(
        json.dumps(
            {
                "ok": True,
                "version": version,
                "wheel": wheels[0].name,
                "sdist": sdists[0].name,
                "next": "Actions → Publish to PyPI → confirm publish (needs PYPI_API_TOKEN)",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
