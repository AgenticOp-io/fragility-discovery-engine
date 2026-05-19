"""Deterministic text narration over frozen engine JSON (Phase L).

Output is descriptive only — never fed back into simulation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_frozen_json_artifact(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as e:
        raise ValueError(str(e)) from e
    except json.JSONDecodeError as e:
        raise ValueError(f"{path}: {e}") from e
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def narrate_frozen_artifact(data: dict[str, Any], *, source: str, citation_prefix: str = "") -> str:
    schema = data.get("schema")
    schema_ver = data.get("schema_version")
    lines = []
    if citation_prefix:
        lines.append(citation_prefix.rstrip())
        lines.append("---")
    lines.append(f"source: {source}")
    lines.append("---")

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

    bs = data.get("baseline")
    cf = data.get("counterfactual")
    if (
        isinstance(bs, dict)
        and isinstance(cf, dict)
        and data.get("intervention") is not None
        and "integral_instability" in bs
        and "integral_instability" in cf
        and schema != "attribution-merge-v1"
    ):
        lines.append("kind: counterfactual bundle (baseline vs variant rollout snapshots)")
        lines.append(f"intervention: {data.get('intervention')}")
        lines.append(
            f"baseline integral_instability: {bs.get('integral_instability')}  "
            f"attack_cost: {bs.get('attack_cost')}"
        )
        lines.append(
            f"counterfactual integral_instability: {cf.get('integral_instability')}  "
            f"attack_cost: {cf.get('attack_cost')}"
        )
        if data.get("delta_integral_instability") is not None:
            lines.append(f"delta_integral_instability (base - var): {data.get('delta_integral_instability')}")
        if data.get("delta_attack_cost") is not None:
            lines.append(f"delta_attack_cost (base - var): {data.get('delta_attack_cost')}")
        if data.get("interpretation_hint"):
            lines.append(f"hint: {data.get('interpretation_hint')}")
        meta = data.get("meta")
        if isinstance(meta, dict) and meta.get("cli"):
            lines.append(f"meta.cli: {meta.get('cli')}")
        return "\n".join(lines)

    if schema in (
        "fragility-institutional-composite-v1",
        "fragility-institutional-composite-v2",
        "fragility-institutional-composite-v3",
        "fragility-institutional-composite-v4",
    ):
        lines.append("kind: institutional composite (decoupled kernels, one shock schedule)")
        lines.append(f"schema: {schema}")
        for branch in ("aggregate", "network", "resource_cascade", "service_backlog", "liquidity_ladder"):
            b = data.get(branch)
            if isinstance(b, dict):
                lines.append(
                    f"  {branch}: collapsed={b.get('collapsed')} "
                    f"integral_instability={b.get('integral_instability')} "
                    f"attack_cost={b.get('attack_cost')} simulation_mode={b.get('simulation_mode')}"
                )
        if data.get("genome_shape") is not None:
            lines.append(f"genome_shape: {data.get('genome_shape')}")
        return "\n".join(lines)

    if schema == "explanation-dag-v1":
        lines.append("kind: explanation DAG (mechanical)")
        lines.append(f"dag_kind: {data.get('kind')}")
        nodes = data.get("nodes") or []
        edges = data.get("edges") or []
        lines.append(f"nodes: {len(nodes)}  edges: {len(edges)}")
        for e in edges[:12]:
            if isinstance(e, dict):
                lines.append(
                    f"  edge {e.get('from')} -> {e.get('to')}: {e.get('kind')}"
                    + (f" ({e.get('intervention')})" if e.get("intervention") is not None else "")
                )
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
        if data.get("simulation_mode") == "liquidity_ladder" and isinstance(meta, dict):
            if meta.get("initial_margin") is not None:
                lines.append(f"meta.initial_margin: {meta.get('initial_margin')}")
        return "\n".join(lines)

    lines.append("kind: unknown JSON (no recognized schema)")
    lines.append(f"top_keys: {sorted(data.keys())[:24]}")
    return "\n".join(lines)


# Backwards-compatible alias
narrate = narrate_frozen_artifact
