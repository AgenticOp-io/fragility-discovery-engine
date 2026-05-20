"""Phase O — local static dashboard index (not hosted SaaS)."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "artifacts" / "dashboard" / "index.html"

VIEWERS = [
    ("Replay timeline", "artifacts/replay_viewer/index.html"),
    ("Pareto front", "artifacts/pareto_viewer/index.html"),
    ("Attribution / chains", "artifacts/attribution_viewer/index.html"),
    ("Institutional composite", "artifacts/composite_viewer/index.html"),
]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__ or "")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Optional benchmark_manifest.json to link in the page.",
    )
    args = ap.parse_args()

    manifest_link = ""
    if args.manifest and args.manifest.is_file():
        manifest_link = f'<p>Manifest: <code>{args.manifest.as_posix()}</code></p>'

    items = "\n".join(
        f'    <li><a href="../{href}">{title}</a></li>' for title, href in VIEWERS
    )
    built = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Fragility Discovery Engine — local dashboard</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; max-width: 52rem; }}
    code {{ background: #f4f4f4; padding: 0.1rem 0.3rem; }}
  </style>
</head>
<body>
  <h1>Fragility Discovery Engine</h1>
  <p>Local static index over bundled viewers. Serve repo root: <code>python -m http.server 8765</code></p>
  <p>Built: <code>{built}</code></p>
  {manifest_link}
  <h2>Viewers</h2>
  <ul>
{items}
  </ul>
  <h2>CLI entry points</h2>
  <ul>
    <li><code>python scripts/run_flagship_demo.py</code></li>
    <li><code>python scripts/run_benchmark_suite.py --validate</code></li>
    <li><code>python scripts/fragility_robustness_stretch.py --preset small --dry-run</code></li>
  </ul>
</body>
</html>
"""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="utf-8")
    print(json.dumps({"out": str(args.out), "built_utc": built}, indent=2))


if __name__ == "__main__":
    main()
