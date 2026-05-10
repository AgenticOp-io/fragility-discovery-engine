"""One-shot “flagship” artifact bundle: short GA + Pareto slice + ``fragility-certificate-v1``."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from fragility_engine.adversary.search import genetic_search
from fragility_engine.agents.stablecoin_agents import default_stablecoin_population
from fragility_engine.benchmarks.certificate import build_fragility_certificate
from fragility_engine.coevolution.thread_safe_template import thread_safe_peg_clone
from fragility_engine.runner import REPLAY_SCHEMA_VERSION, rollout_stablecoin, rollout_to_replay_dict
from fragility_engine.world.stablecoin_peg import StablecoinPegWorld

_REPO_ROOT = Path(__file__).resolve().parents[3]


def run_flagship_demo(
    output_dir: Path,
    *,
    validate_bundles_first: bool = True,
    horizon: int = 14,
    generations: int = 3,
    population_size: int = 12,
    ga_seed: int = 424_242,
    max_steps: int = 36,
    eval_workers: int = 1,
) -> dict[str, Any]:
    """
    Write under ``output_dir``:

    - ``best_replay.json`` — best GA rollout (replay schema).
    - ``pareto_front.json`` — ``pareto-front-v1`` from the same GA (``collect_pareto=True``).
    - ``fragility_certificate.json`` — :data:`~fragility_engine.benchmarks.certificate.FRAGILITY_CERTIFICATE_SCHEMA`.
    - ``README_FLAGSHIP.txt`` — human index of files and how to cite.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    bench_meta: dict[str, Any] | None = None
    if validate_bundles_first:
        from fragility_engine.benchmarks.suite import validate_benchmark_suite

        try:
            validate_benchmark_suite()
            bench_meta = {"status": "passed", "gate": "validate_benchmark_suite"}
        except AssertionError as e:
            bench_meta = {"status": "failed", "error": str(e)[:2000]}

    template = StablecoinPegWorld(population=default_stablecoin_population(), max_steps=max_steps)
    ew = max(1, int(eval_workers))

    def evaluator(genome: np.ndarray, seed: int):
        world = thread_safe_peg_clone(template) if ew > 1 else template
        return rollout_stablecoin(world, genome, seed=seed, initial_panic=0.05)

    search = genetic_search(
        evaluator,
        horizon=int(horizon),
        generations=int(generations),
        population_size=int(population_size),
        seed=int(ga_seed),
        collect_pareto=True,
        eval_workers=ew,
    )

    replay_path = output_dir / "best_replay.json"
    pareto_path = output_dir / "pareto_front.json"
    cert_path = output_dir / "fragility_certificate.json"

    replay = rollout_to_replay_dict(search.best_rollout)
    replay["meta"] = {
        "replay_schema": REPLAY_SCHEMA_VERSION,
        "cli": "run_flagship_demo",
        "flagship": True,
        "ga_seed": int(ga_seed),
        "horizon": int(horizon),
        "generations": int(generations),
        "population_size": int(population_size),
        "eval_workers": ew,
    }
    replay_path.write_text(json.dumps(replay, indent=2), encoding="utf-8")

    pareto_payload: dict[str, Any] = {
        "schema": "pareto-front-v1",
        "best_fitness": float(search.best_fitness),
        "eval_workers": ew,
        "archive": [
            {
                "severity": float(p.severity),
                "attack_cost": float(p.attack_cost),
                "collapsed": bool(p.collapsed),
                "integral_instability": float(p.integral_instability),
                "genome": p.genome.tolist(),
            }
            for p in search.pareto_archive
        ],
        "domain": "aggregate_flagship",
    }
    pareto_path.write_text(json.dumps(pareto_payload, indent=2), encoding="utf-8")

    flagship_run = {
        "mode": "aggregate_stablecoin_peg",
        "horizon": int(horizon),
        "generations": int(generations),
        "population_size": int(population_size),
        "ga_seed": int(ga_seed),
        "best_fitness": float(search.best_fitness),
        "artifacts": {
            "best_replay": str(replay_path.name),
            "pareto_front": str(pareto_path.name),
        },
    }
    cert = build_fragility_certificate(
        artifact_paths=[replay_path, pareto_path],
        include_benchmark_manifest=True,
        benchmark_validation=bench_meta,
        flagship_run=flagship_run,
        repo_root=_REPO_ROOT,
        notes="Synthetic flagship bundle for reviewer walkthrough; not a forecast of any real institution.",
    )
    cert_path.write_text(json.dumps(cert, indent=2), encoding="utf-8")

    readme = output_dir / "README_FLAGSHIP.txt"
    readme.write_text(
        "\n".join(
            [
                "Flagship demo bundle (fragility-discovery-engine)",
                "",
                "Files:",
                f"  - {replay_path.name}  — best GA rollout (open in artifacts/replay_viewer/index.html)",
                f"  - {pareto_path.name}   — Pareto archive slice (artifacts/pareto_viewer/index.html)",
                f"  - {cert_path.name}    — fragility-certificate-v1 (citation / reproducibility)",
                "",
                "Cite: git_commit + certificate_content_sha256 from fragility_certificate.json",
                "Workflow: docs/PAPER_APPENDIX_WORKFLOW.md",
                "",
            ]
        ),
        encoding="utf-8",
    )

    return {
        "output_dir": str(output_dir.resolve()),
        "files": [str(replay_path), str(pareto_path), str(cert_path), str(readme)],
        "certificate": cert,
    }
