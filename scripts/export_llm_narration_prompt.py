"""Phase L — versioned LLM prompt bundle for frozen engine JSON (optional OpenAI invoke).

Templates live under ``artifacts/llm_prompts/narration_v1/``. Bundle schema: **llm-prompt-bundle-v1**.
Output is **never** fed back into simulation (see bundle disclaimer).

Optional ``--invoke-openai`` posts to the Chat Completions API (stdlib ``urllib`` only; requires API key).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from fragility_engine.explain.narration import load_frozen_json_artifact, narrate_frozen_artifact

BUNDLE_SCHEMA = "llm-prompt-bundle-v1"
DEFAULT_TEMPLATE_ID = "frozen_artifact_narration"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _prompt_pack_dir() -> Path:
    return _repo_root() / "artifacts" / "llm_prompts" / "narration_v1"


def _read_template_version() -> str:
    vpath = _prompt_pack_dir() / "version.txt"
    try:
        return vpath.read_text(encoding="utf-8").strip()
    except OSError as e:
        raise SystemExit(f"missing template version file {vpath}: {e}") from e


def _read_text(name: str) -> str:
    p = _prompt_pack_dir() / name
    try:
        return p.read_text(encoding="utf-8")
    except OSError as e:
        raise SystemExit(f"missing template file {p}: {e}") from e


def build_prompt_bundle(
    artifact_path: Path,
    *,
    cite_digest: bool,
) -> dict[str, Any]:
    resolved = artifact_path.resolve()
    digest_hex: str | None = None
    cite_prefix = ""
    if cite_digest:
        raw = resolved.read_bytes()
        digest_hex = hashlib.sha256(raw).hexdigest()
        cite_prefix = f"citation_sha256: {digest_hex}\ncitation_path: {resolved.as_posix()}"
    else:
        cite_prefix = f"citation_path: {resolved.as_posix()}"

    try:
        data = load_frozen_json_artifact(artifact_path)
    except ValueError as e:
        raise SystemExit(str(e)) from e

    narration = narrate_frozen_artifact(data, source=str(resolved), citation_prefix="")

    system_prompt = _read_text("system.txt").strip()
    user_tpl = _read_text("user_template.txt")
    user_prompt = user_tpl.format(citation_block=cite_prefix, deterministic_narration=narration.strip())

    disclaimer = (
        "LLM-generated prose is descriptive only. Do not parse model output into simulation inputs, "
        "CLI arguments, or code changes without independent verification."
    )

    bundle: dict[str, Any] = {
        "schema": BUNDLE_SCHEMA,
        "template_id": DEFAULT_TEMPLATE_ID,
        "template_version": _read_template_version(),
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "input_path": str(resolved),
        "disclaimer": disclaimer,
    }
    if digest_hex is not None:
        bundle["input_sha256"] = digest_hex
    return bundle


def invoke_openai_chat(*, bundle: dict[str, Any], model: str, api_key: str, timeout_s: float = 120.0) -> str:
    body = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": bundle["system_prompt"]},
                {"role": "user", "content": bundle["user_prompt"]},
            ],
            "temperature": 0.2,
            "max_tokens": 600,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        OPENAI_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"OpenAI HTTP {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise SystemExit(f"OpenAI request failed: {e}") from e

    try:
        return str(payload["choices"][0]["message"]["content"]).strip()
    except (KeyError, IndexError, TypeError) as e:
        raise SystemExit(f"unexpected OpenAI response shape: {payload!r}") from e


def main() -> None:
    ap = argparse.ArgumentParser(description="Export llm-prompt-bundle-v1 for frozen JSON (+ optional OpenAI call).")
    ap.add_argument("artifact_json", type=Path)
    ap.add_argument("--out", type=Path, required=True, help="Write llm-prompt-bundle-v1 JSON.")
    ap.add_argument("--cite-digest", action="store_true", help="Include SHA-256 of raw artifact bytes.")
    ap.add_argument(
        "--invoke-openai",
        action="store_true",
        help="POST bundle to OpenAI Chat Completions (requires API key env).",
    )
    ap.add_argument("--model", type=str, default="gpt-4o-mini")
    ap.add_argument(
        "--api-key-env",
        type=str,
        default="OPENAI_API_KEY",
        help="Environment variable holding the OpenAI API key (when --invoke-openai).",
    )
    args = ap.parse_args()

    bundle = build_prompt_bundle(Path(args.artifact_json), cite_digest=bool(args.cite_digest))
    args.out.write_text(json.dumps(bundle, indent=2), encoding="utf-8")

    if args.invoke_openai:
        key = os.environ.get(str(args.api_key_env), "").strip()
        if not key:
            raise SystemExit(f"Set {args.api_key_env} for --invoke-openai.")
        text = invoke_openai_chat(bundle=bundle, model=str(args.model), api_key=key)
        print("--- LLM_NARRATION_BEGIN (do not feed to simulation) ---")
        print(text)
        print("--- LLM_NARRATION_END ---")


if __name__ == "__main__":
    main()
