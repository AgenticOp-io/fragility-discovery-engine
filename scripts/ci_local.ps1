# Local parity with .github/workflows/ci.yml "test" job (Windows PowerShell).
# Activate your venv first, then:
#   pwsh -File scripts/ci_local.ps1
# or (Windows PowerShell 5):
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ci_local.ps1
# Optional: set env FRAGILITY_CI_LOCAL_BUILD=1 to also run ``python -m build`` (CI build job).
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Error "python not on PATH - create a venv and activate it (see docs/HOW_TO_USE.md)."
}

# Single-quoted extras so Windows PowerShell 5 does not parse `.[dev]` as a type expression.
python -m pip install -e '.[dev]'
python -m ruff check .
$env:FRAGILITY_PERF_GATE = "1"
if (-not $env:FRAGILITY_PERF_GATE_MS) { $env:FRAGILITY_PERF_GATE_MS = "240000" }
python -m pytest -q
python scripts/run_benchmark_suite.py --validate
python scripts/check_manifest_digest.py
python scripts/check_manifest_inventory.py
python scripts/check_flagship_bundled.py
python scripts/check_manifest_summary.py
python scripts/validate_viewer_presets.py
if ($env:FRAGILITY_CI_LOCAL_BUILD) {
  python -m pip install -q build
  python -m build
}
Write-Host 'ci_local: OK (ruff + pytest + benchmark --validate + manifest pins; FRAGILITY_PERF_GATE=1)'
