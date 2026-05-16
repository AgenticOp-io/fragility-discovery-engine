from fragility_engine.benchmarks.manifest import build_benchmark_manifest
from fragility_engine.benchmarks.manifest_inventory import manifest_inventory_sha256


def test_manifest_inventory_matches_pinned_fixture():
    expected = (
        "tests/fixtures/benchmarks/manifest_inventory_sha256.txt"
    )
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    pin = (root / expected).read_text(encoding="utf-8").strip()
    assert manifest_inventory_sha256(build_benchmark_manifest()) == pin
