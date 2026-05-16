from fragility_engine.benchmarks.hypervolume import hypervolume_2d_min
from fragility_engine.benchmarks.manifest import (
    MANIFEST_SCHEMA,
    build_benchmark_manifest,
    format_benchmark_manifest_summary,
)


def test_format_benchmark_manifest_summary():
    m = build_benchmark_manifest()
    text = format_benchmark_manifest_summary(m)
    assert "benchmark_manifest_summary" in text
    assert MANIFEST_SCHEMA in text
    assert "golden_metrics_sha256=" in text
    assert "aggregate_rollout_v1" in text
    assert "replay_schema_version=" in text


def test_build_benchmark_manifest_shape():
    m = build_benchmark_manifest()
    assert m["schema"] == MANIFEST_SCHEMA == "benchmark-manifest-v2"
    assert m["bundle_count"] == len(m["bundle_ids"])
    assert len(m["bundles"]) == len(m["bundle_ids"])
    assert all("topology" in b and "world" in b for b in m["bundles"])
    assert len(m["golden_metrics_sha256"]) == 64
    bands = m["bundle_integral_bands"]
    assert "service_backlog_rollout_v1" in bands
    assert bands["service_backlog_rollout_v1"]["integral_instability_max"] == 2.0
    assert m["provenance"]["python_version"]
    assert m["provenance"]["fragility_engine_version"]
    assert "replay_schema_version" in m
    rb = m["resource_cascade_backend"]
    assert set(rb) == {"resource_cascade_backend_env", "resource_cascade_backend_effective"}
    assert rb["resource_cascade_backend_effective"] in ("numpy", "numba")
    assert m["hypervolume_2d_min"]["symbol"] == "hypervolume_2d_min"
    fx = m["hypervolume_2d_min"]["regression_fixture"]
    assert fx["expected_hypervolume"] == hypervolume_2d_min(
        [tuple(p) for p in fx["points"]],
        tuple(fx["reference"]),
    )
    art = m["artifact_schemas"]
    assert art["pareto_front"] == "pareto-front-v1"
    assert "fragility-institutional-composite-v3" in art["institutional_composite"]
    assert m["explanation_dag"]["schema"] == "explanation-dag-v1"
    pf = m["pareto_hypervolume_fixtures"]
    assert len(pf) == 3
    assert pf[0]["path"].endswith("pinned_pareto_front_minimal.json")
    assert pf[1]["path"].endswith("pinned_pareto_front_two_branch.json")
    assert pf[2]["path"].endswith("artifacts/flagship/bundled/pareto_front.json")
    assert pf[2]["case"] == "flagship_bundled_pareto_hypervolume"
    bundled = m.get("bundled_artifact_paths")
    assert isinstance(bundled, list) and len(bundled) >= 11
    assert "liquidity_ladder_rollout_v1" in m.get("bundle_ids", [])
    assert m.get("bundled_artifact_checks") == "scripts/check_bundled_artifacts.py"
