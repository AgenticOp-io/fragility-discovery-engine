#Requires -Version 5.1
<#
.SYNOPSIS
  Install Numba optional extra using a Windows **amd64** CPython (normal pip wheels).

.DESCRIPTION
  On Windows on ARM, **native ARM64** Python does not get Numba wheels from PyPI. The supported
  approach is the same as on x64 PCs: install the standard **Windows installer (64-bit)** from
  python.org. Windows runs that **x64** binary under built-in **x64 emulation** (automatic on WoA);
  this is not the old EXE Properties "Compatibility mode" dialog.

  This script picks an amd64 `python.exe` (see search order below) and runs
  `pip install -e ".[dev,accelerate]"` from the repo root.

.PARAMETER AccelerateOnly
  If set, runs `pip install -e ".[accelerate]"` only (skip dev extras).

.EXAMPLE
  .\scripts\install_accelerate_windows.ps1

.NOTES
  Override discovery with FRAGILITY_AMD64_PYTHON=C:\path\to\python.exe
#>
param(
    [switch]$AccelerateOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

function Test-IsAmd64Python([string]$PyPath) {
    if (-not (Test-Path -LiteralPath $PyPath)) {
        return $false
    }
    $tag = & $PyPath -c "import sys; print('AMD64' if '(AMD64)' in sys.version else 'NO')" 2>$null
    return ($tag -eq "AMD64")
}

$candidates = [System.Collections.Generic.List[string]]::new()

if ($env:FRAGILITY_AMD64_PYTHON) {
    $candidates.Add($env:FRAGILITY_AMD64_PYTHON.Trim())
}

$pyCmd = Get-Command py -ErrorAction SilentlyContinue
if ($pyCmd) {
    foreach ($spec in @("-3.13-64", "-3.12-64", "-3.11-64")) {
        try {
            $exe = & py $spec -c "import sys; print(sys.executable)" 2>$null
            if ($exe) {
                $candidates.Add(($exe | Out-String).Trim())
            }
        }
        catch {
            # ignore missing interpreter tags
        }
    }
}

$programsPython = Join-Path $env:LOCALAPPDATA "Programs\Python"
if (Test-Path -LiteralPath $programsPython) {
    Get-ChildItem -LiteralPath $programsPython -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^Python\d+-x64$' } |
        ForEach-Object {
            $exe = Join-Path $_.FullName "python.exe"
            $candidates.Add($exe)
        }
}

$pathPython = Get-Command python -ErrorAction SilentlyContinue
if ($pathPython) {
    $candidates.Add($pathPython.Source)
}

$chosen = $null
foreach ($c in $candidates) {
    if (-not $c) {
        continue
    }
    if (Test-IsAmd64Python $c) {
        $chosen = $c
        break
    }
}

if (-not $chosen) {
    $msg = @'
No Windows amd64 CPython found. On Windows on ARM, install the normal Windows installer (64-bit) from python.org; Windows runs that x64 Python under built-in x64 emulation. Re-run this script or set FRAGILITY_AMD64_PYTHON. Native ARM64 Python has no Numba wheels on PyPI.
'@
    throw $msg
}

Write-Host "Using amd64 Python: $chosen"
$extras = if ($AccelerateOnly) { ".[accelerate]" } else { ".[dev,accelerate]" }
& $chosen -m pip install -e $extras

Write-Host ""
Write-Host "Installed $extras. Example parity run:"
Write-Host "  & `"$chosen`" -m pytest tests/test_resource_cascade_numba_parity.py -q"
