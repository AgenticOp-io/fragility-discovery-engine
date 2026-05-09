"""Phase L wrapper: human-readable narration over frozen engine JSON (replay, Pareto, attribution merge).

Output is **not** fed back into simulation — summaries cite artifact keys only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as e:
        raise SystemExit(str(e)) from e
    except json.JSONDecodeError as e:
        raise SystemExit(f"{path}: {e}") from e
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: expected JSON object")
    return data


def narrate(data: dict[str, Any], *, source: str) -> str:
    schema = data.get("schema")
    schema_ver = data.get("schema_version")
    lines = [f"source: {source}", "---"]

    if schema == "attribution-merge-v1":
        lines.append("kind: attribution merge (star graph)")
        lines.append(f"branches: {data.get('branch_count')}")
        lines.append(f"strict_baseline: {data.get('strict_baseline')}")
        for i, e in enumerate(data.get("edges") or []):
            if isinstance(e, dict):
                lines.append(
                    f"  edge[{i}] intervention={e.get('intervention')} "
                    f"d_integral={e.get('delta_integral_instability')} d_cost={e.get('delta_attack_cost')}"
                )
        meta = data.get("meta")
        if isinstance(meta, dict):
            lines.append(f"meta.cli: {meta.get('cli')}")
        return "\n".join(lines)

    if schema == "counterfactual-epsilon-sweep-v1":
        lines.append("kind: epsilon sweep")
        lines.append(f"mode: {data.get('mode')}  axis: {data.get('axis')}")
        runs = data.get("runs") or []
        lines.append(f"runs: {len(runs)}")
        summ = data.get("summary") or {}
        if isinstance(summ, dict):
            lines.append(
                f"summary: collapse_count={summ.get('collapse_count')} "
                f"integral [{summ.get('integral_instability_min')}, {summ.get('integral_instability_max')}]"
            )
        return "\n".join(lines)

    if schema == "pareto-front-v1":
        lines.append("kind: Pareto archive dump")
        lines.append(f"best_fitness: {data.get('best_fitness')}")
        arch = data.get("archive") or []
        lines.append(f"archive_points: {len(arch)}")
        if data.get("domain"):
            lines.append(f"domain: {data.get('domain')}")
        if data.get("initial_overload") is not None:
            lines.append(f"initial_overload: {data.get('initial_overload')}")
        return "\n".join(lines)

    if isinstance(schema_ver, str) and data.get("trajectory") is not None:
        lines.append("kind: replay rollout")
        lines.append(f"schema_version: {schema_ver}")
        lines.append(f"simulation_mode: {data.get('simulation_mode')}")
        lines.append(f"collapsed: {data.get('collapsed')}  timestep: {data.get('collapse_timestep')}")
        lines.append(f"integral_instability: {data.get('integral_instability')}")
        lines.append(f"attack_cost: {data.get('attack_cost')}")
        traj = data.get("trajectory") or []
        lines.append(f"trajectory_steps: {len(traj)}")
        meta = data.get("meta")
        if isinstance(meta, dict) and meta.get("cli"):
            lines.append(f"meta.cli: {meta.get('cli')}")
        return "\n".join(lines)

    lines.append("kind: unknown JSON (no recognized schema)")
    lines.append(f"top_keys: {sorted(data.keys())[:24]}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Print short narration for frozen replay / Pareto / merge JSON.")
    ap.add_argument("json_path", type=Path, help="Path to .json artifact.")
    ap.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Optional path for narration-summary-v1 JSON (machine-readable).",
    )
    args = ap.parse_args()

    data = _load(args.json_path)
    text = narrate(data, source=str(args.json_path))
    print(text)

    if args.json_out is not None:
        summary = {
            "schema": "narration-summary-v1",
            "input": str(args.json_path),
            "text": text,
        }
        args.json_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
