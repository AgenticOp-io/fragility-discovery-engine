#!/usr/bin/env python3
"""Create and publish a new Zenodo version for a GitHub software release.

Requires ``ZENODO_TOKEN`` (Zenodo → Account → Applications → Personal access tokens
with ``deposit:write`` and ``deposit:actions``).

Example::

    $env:ZENODO_TOKEN = "..."
    python -m build
    python scripts/publish_zenodo_version.py --tag v0.6.0 --latest-recid 20455689 --attach-dist --publish
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LATEST = "20455689"  # fel-v0.1.1 version record
API = "https://zenodo.org/api"


def _token() -> str:
    token = (os.environ.get("ZENODO_TOKEN") or os.environ.get("ZENODO_API_TOKEN") or "").strip()
    if not token:
        raise SystemExit("Set ZENODO_TOKEN (deposit:write + deposit:actions).")
    return token


def _url(path: str, token: str) -> str:
    sep = "&" if "?" in path else "?"
    return f"{API}{path}{sep}access_token={urllib.parse.quote(token)}"


def _req(method: str, path: str, token: str, data: dict | None = None) -> dict:
    body = None if data is None else json.dumps(data).encode("utf-8")
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(_url(path, token), data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=180) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"{method} {path} -> {exc.code}: {detail}") from exc


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tag", required=True, help="GitHub release tag, e.g. v0.6.0")
    ap.add_argument(
        "--latest-recid",
        default=DEFAULT_LATEST,
        help="Most recent published Zenodo record id in the concept chain",
    )
    ap.add_argument("--publish", action="store_true", help="Publish immediately (else leave draft)")
    ap.add_argument("--attach-dist", action="store_true", help="Upload wheel/sdist from dist/")
    args = ap.parse_args()

    token = _token()
    version = args.tag[1:] if args.tag.startswith("v") else args.tag

    # newversion returns a link to the unpublished draft deposition
    created = _req("POST", f"/deposit/depositions/{args.latest_recid}/actions/newversion", token)
    draft_url = created.get("links", {}).get("latest_draft")
    if not draft_url:
        raise SystemExit(f"newversion did not return latest_draft: {json.dumps(created)[:500]}")
    draft_id = draft_url.rstrip("/").split("/")[-1]
    print(f"draft deposition: {draft_id}")

    dep = _req("GET", f"/deposit/depositions/{draft_id}", token)
    metadata = dict(dep.get("metadata") or {})
    metadata.update(
        {
            "title": "Fragility Discovery Engine",
            "upload_type": "software",
            "description": (
                f"<p>Software release <strong>{args.tag}</strong>: BYOW CLI "
                "(<code>fragility</code>), falsification harness, six toy regression oracles.</p>"
                "<p><code>pip install fragility-engine</code> · "
                f"<a href=\"https://github.com/AgenticOp-io/fragility-discovery-engine/releases/tag/{args.tag}\">"
                f"GitHub {args.tag}</a></p>"
                "<p>Apache 2.0. Concept DOI: 10.5281/zenodo.20455688.</p>"
            ),
            "creators": [{"name": "Peterson, David", "affiliation": "Agentic Ops"}],
            "version": version,
            "keywords": [
                "simulation",
                "stress testing",
                "reproducibility",
                "counterfactual attribution",
                "bring-your-own-world",
            ],
            "related_identifiers": [
                {
                    "identifier": f"https://github.com/AgenticOp-io/fragility-discovery-engine/tree/{args.tag}",
                    "relation": "isSupplementTo",
                    "resource_type": "software",
                    "scheme": "url",
                }
            ],
            "access_right": "open",
            "license": "Apache-2.0",
        }
    )
    _req("PUT", f"/deposit/depositions/{draft_id}", token, {"metadata": metadata})

    if args.attach_dist:
        bucket = dep.get("links", {}).get("bucket")
        if not bucket:
            raise SystemExit("deposition missing bucket link")
        dist = ROOT / "dist"
        files = sorted(dist.glob(f"fragility_engine-{version}*"))
        if not files:
            raise SystemExit(f"no dist/fragility_engine-{version}* — run python -m build first")
        for path in files:
            print(f"uploading {path.name}")
            data = path.read_bytes()
            req = urllib.request.Request(
                f"{bucket}/{urllib.parse.quote(path.name)}",
                data=data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/octet-stream",
                },
                method="PUT",
            )
            with urllib.request.urlopen(req, timeout=300) as resp:
                resp.read()

    if args.publish:
        published = _req("POST", f"/deposit/depositions/{draft_id}/actions/publish", token)
        doi = published.get("doi") or published.get("metadata", {}).get("doi")
        html = published.get("links", {}).get("html") or f"https://zenodo.org/records/{published.get('id')}"
        print(json.dumps({"ok": True, "doi": doi, "record": html, "id": published.get("id")}, indent=2))
    else:
        print(
            json.dumps(
                {
                    "ok": True,
                    "draft_id": draft_id,
                    "review_url": f"https://zenodo.org/uploads/{draft_id}",
                    "next": "Review metadata, then re-run with --publish or click Publish on Zenodo",
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
