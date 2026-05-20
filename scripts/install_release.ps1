# Install fragility-engine from a git tag or GitHub Release wheel (no PyPI required).
param(
  [string]$Tag = "v0.5.0",
  [ValidateSet("auto", "editable", "git", "wheel")]
  [string]$Mode = $(if ($env:FRAGILITY_INSTALL_MODE) { $env:FRAGILITY_INSTALL_MODE } else { "auto" })
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Ver = $Tag -replace '^v', ''
$Repo = if ($env:FRAGILITY_REPO) { $env:FRAGILITY_REPO } else { "https://github.com/AgenticOp-io/fragility-discovery-engine" }

if ($Mode -eq "auto") {
  $pyproject = Join-Path $Root "pyproject.toml"
  if ((Test-Path $pyproject) -and (Select-String -Path $pyproject -Pattern "version = `"$Ver`"" -Quiet)) {
    $Mode = "editable"
  } else {
    $Mode = "wheel"
  }
}

switch ($Mode) {
  "editable" {
    Write-Host "==> pip install -e ${Root}[dev] (checkout at $Tag)"
    python -m pip install -e "${Root}[dev]"
  }
  "git" {
    Write-Host "==> pip install from git $Tag"
    python -m pip install "fragility-engine @ git+${Repo}.git@${Tag}"
  }
  "wheel" {
    $WheelUrl = "$Repo/releases/download/$Tag/fragility_engine-$Ver-py3-none-any.whl"
    Write-Host "==> pip install $WheelUrl"
    python -m pip install $WheelUrl
  }
}

python -c "import fragility_engine; print('import_ok', fragility_engine.__file__)"
