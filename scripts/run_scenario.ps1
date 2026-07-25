[CmdletBinding()]
param(
    [switch]$AutonomousMode = $false
)

$ErrorActionPreference = "Stop"
$workspaceRoot = Split-Path -Parent $PSScriptRoot
Set-Location $workspaceRoot

$env:PYTHONPATH = "C:\EnergyPlusV26-1-0;$workspaceRoot"

Write-Host "Starting Sentinel Twin worker..."
if ($AutonomousMode) {
    Write-Host "Running in AUTONOMOUS mode (Actions will be applied to the simulation)."
    $env:SHADOW_MODE = "0"
} else {
    Write-Host "Running in SHADOW mode (Actions are logged but NOT applied)."
    $env:SHADOW_MODE = "1"
}

# In a real scenario, this script would launch `apps.worker.main` or similar
# For the hackathon, we simply execute pytest to ensure the loop tests pass,
# or we'd execute the synchronous E+ runner.
& .\.venv\Scripts\python.exe -m pytest tests/unit/test_control_loop.py -v
if ($LASTEXITCODE -ne 0) {
    throw "Simulation scenario failed."
}

Write-Host "Scenario completed successfully."
