[CmdletBinding()]
param(
    [string]$EnergyPlusExecutable = $env:ENERGYPLUS_PATH,
    [string]$OutputDirectory = "data/outputs/baseline-hot-day"
)

$ErrorActionPreference = "Stop"
$workspaceRoot = Split-Path -Parent $PSScriptRoot
Set-Location $workspaceRoot

& .\.venv\Scripts\python.exe -m scripts.validate_baseline
if ($LASTEXITCODE -ne 0) {
    throw "Baseline asset validation failed. See docs/model-assumptions.md for required assets."
}

if ([string]::IsNullOrWhiteSpace($EnergyPlusExecutable)) {
    $EnergyPlusExecutable = (Get-Command energyplus -ErrorAction SilentlyContinue).Source
}
if ([string]::IsNullOrWhiteSpace($EnergyPlusExecutable)) {
    $bundledExecutable = Get-ChildItem "C:\EnergyPlusV*\energyplus.exe" -ErrorAction SilentlyContinue |
        Select-Object -First 1 -ExpandProperty FullName
    $EnergyPlusExecutable = $bundledExecutable
}
if ([string]::IsNullOrWhiteSpace($EnergyPlusExecutable)) {
    throw "EnergyPlus was not found. Set ENERGYPLUS_PATH to the executable or add it to PATH."
}

New-Item -ItemType Directory -Force $OutputDirectory | Out-Null
& $EnergyPlusExecutable `
    --weather ".\models\energyplus\weather.epw" `
    --output-directory $OutputDirectory `
    ".\models\energyplus\building.epJSON"

if ($LASTEXITCODE -ne 0) {
    throw "EnergyPlus baseline run failed with exit code $LASTEXITCODE. Inspect $OutputDirectory."
}

& .\.venv\Scripts\python.exe -c "from pathlib import Path; from scripts.validate_baseline import validate_completed_run; validate_completed_run(Path(r'$OutputDirectory/eplusout.sql'))"
if ($LASTEXITCODE -ne 0) {
    throw "Baseline output contract validation failed. Inspect $OutputDirectory."
}

Write-Host "Baseline simulation completed. Output directory: $OutputDirectory"
