from fragility_engine.benchmarks.manifest import MANIFEST_SCHEMA, build_benchmark_manifest


def test_build_benchmark_manifest_shape():
    m = build_benchmark_manifest()
    assert m["schema"] == MANIFEST_SCHEMA
    assert m["bundle_count"] == len(m["bundle_ids"])
    assert "replay_schema_version" in m
