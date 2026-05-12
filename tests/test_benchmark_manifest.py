from fragility_engine.benchmarks.hypervolume import hypervolume_2d_min
from fragility_engine.benchmarks.manifest import MANIFEST_SCHEMA, build_benchmark_manifest


def test_build_benchmark_manifest_shape():
    m = build_benchmark_manifest()
    assert m["schema"] == MANIFEST_SCHEMA == "benchmark-manifest-v2"
    assert m["bundle_count"] == len(m["bundle_ids"])
    assert len(m["bundles"]) == len(m["bundle_ids"])
    assert all("topology" in b and "world" in b for b in m["bundles"])
    assert len(m["golden_metrics_sha256"]) == 64
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
