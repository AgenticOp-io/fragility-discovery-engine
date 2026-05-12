# Local parity with .github/workflows/ci.yml "test" job (Windows PowerShell).
# Activate your venv first, then:  pwsh -File scripts/ci_local.ps1
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Error "python not on PATH — create a venv and activate it (see docs/HOW_TO_USE.md)."
}

python -m pip install -e ".[dev]"
python -m ruff check .
$env:FRAGILITY_PERF_GATE = "1"
if (-not $env:FRAGILITY_PERF_GATE_MS) { $env:FRAGILITY_PERF_GATE_MS = "240000" }
python -m pytest -q
Write-Host "ci_local: OK (ruff + pytest with FRAGILITY_PERF_GATE=1)"
