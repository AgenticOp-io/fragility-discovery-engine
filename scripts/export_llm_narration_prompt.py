"""Phase L — versioned LLM prompt bundle for frozen engine JSON (optional OpenAI invoke).

Templates live under ``artifacts/llm_prompts/<pack>/`` (see ``--prompt-pack``).
Bundle schema: **llm-prompt-bundle-v1**. Output is **never** fed back into simulation.

Optional ``--invoke-openai`` posts to the Chat Completions API (stdlib ``urllib``; requires API key).
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

PROMPT_PACK_IDS: tuple[str, ...] = (
    "narration_v1",
    "reviewer_memo_v1",
    "paper_appendix_v1",
    "status_digest_v1",
    "institution_composite_v1",
    "institutional_composite_triple_v1",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _pack_dir(name: str) -> Path:
    if name not in PROMPT_PACK_IDS:
        raise SystemExit(f"--prompt-pack must be one of: {', '.join(PROMPT_PACK_IDS)}")
    d = _repo_root() / "artifacts" / "llm_prompts" / name
    if not d.is_dir():
        raise SystemExit(f"missing prompt pack directory: {d}")
    return d


def _read_pack_version(pack_dir: Path) -> str:
    vpath = pack_dir / "version.txt"
    try:
        return vpath.read_text(encoding="utf-8").strip()
    except OSError as e:
        raise SystemExit(f"missing template version file {vpath}: {e}") from e


def _read_pack_file(pack_dir: Path, name: str) -> str:
    p = pack_dir / name
    try:
        return p.read_text(encoding="utf-8")
    except OSError as e:
        raise SystemExit(f"missing template file {p}: {e}") from e


def build_prompt_bundle(
    artifact_path: Path,
    *,
    cite_digest: bool,
    prompt_pack: str,
) -> dict[str, Any]:
    pack_dir = _pack_dir(prompt_pack)
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

    system_prompt = _read_pack_file(pack_dir, "system.txt").strip()
    user_tpl = _read_pack_file(pack_dir, "user_template.txt")
    fmt: dict[str, str] = {
        "citation_block": cite_prefix,
        "deterministic_narration": narration.strip(),
    }
    if "{schema_hint}" in user_tpl:
        fmt["schema_hint"] = str(data.get("schema", ""))
    user_prompt = user_tpl.format(**fmt)

    disclaimer = (
        "LLM-generated prose is descriptive only. Do not parse model output into simulation inputs, "
        "CLI arguments, or code changes without independent verification."
    )

    bundle: dict[str, Any] = {
        "schema": BUNDLE_SCHEMA,
        "template_id": DEFAULT_TEMPLATE_ID,
        "prompt_pack": prompt_pack,
        "template_version": _read_pack_version(pack_dir),
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "input_path": str(resolved),
        "disclaimer": disclaimer,
    }
    if digest_hex is not None:
        bundle["input_sha256"] = digest_hex
    return bundle


def invoke_openai_chat(
    *,
    bundle: dict[str, Any],
    model: str,
    api_key: str,
    max_tokens: int,
    timeout_s: float = 120.0,
) -> str:
    body = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": bundle["system_prompt"]},
                {"role": "user", "content": bundle["user_prompt"]},
            ],
            "temperature": 0.2,
            "max_tokens": int(max_tokens),
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
        "--prompt-pack",
        choices=PROMPT_PACK_IDS,
        default="narration_v1",
        help="Which versioned template directory under artifacts/llm_prompts/ to use.",
    )
    ap.add_argument(
        "--invoke-openai",
        action="store_true",
        help="POST bundle to OpenAI Chat Completions (requires API key env).",
    )
    ap.add_argument("--model", type=str, default="gpt-4o-mini")
    ap.add_argument("--max-tokens", type=int, default=600, help="Completion budget when --invoke-openai.")
    ap.add_argument(
        "--api-key-env",
        type=str,
        default="OPENAI_API_KEY",
        help="Environment variable holding the OpenAI API key (when --invoke-openai).",
    )
    args = ap.parse_args()

    bundle = build_prompt_bundle(
        Path(args.artifact_json),
        cite_digest=bool(args.cite_digest),
        prompt_pack=str(args.prompt_pack),
    )
    args.out.write_text(json.dumps(bundle, indent=2), encoding="utf-8")

    if args.invoke_openai:
        key = os.environ.get(str(args.api_key_env), "").strip()
        if not key:
            raise SystemExit(f"Set {args.api_key_env} for --invoke-openai.")
        text = invoke_openai_chat(
            bundle=bundle,
            model=str(args.model),
            api_key=key,
            max_tokens=int(args.max_tokens),
        )
        print("--- LLM_NARRATION_BEGIN (do not feed to simulation) ---")
        print(text)
        print("--- LLM_NARRATION_END ---")


if __name__ == "__main__":
    main()
