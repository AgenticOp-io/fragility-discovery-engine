from fragility_engine.benchmarks.manifest import manifest_summary_sha256


def test_manifest_summary_matches_pinned_fixture():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    pin = (root / "tests/fixtures/benchmarks/manifest_summary_sha256.txt").read_text(encoding="utf-8").strip()
    assert manifest_summary_sha256() == pin
