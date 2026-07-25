[CmdletBinding()]
param(
    [switch]$InstallDevTools
)

$ErrorActionPreference = "Stop"
$workspaceRoot = Split-Path -Parent $PSScriptRoot
Set-Location $workspaceRoot

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example. Update ENERGYPLUS_PATH when necessary."
}

if (-not (Test-Path ".venv")) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        py -3.11 -m venv .venv
    }
    else {
        python -m venv .venv
    }
    Write-Host "Created .venv."
}

if ($InstallDevTools) {
    & .\.venv\Scripts\python.exe -m pip install --upgrade pip
    & .\.venv\Scripts\python.exe -m pip install pytest ruff mypy
}

& "$PSScriptRoot\check_environment.ps1"
