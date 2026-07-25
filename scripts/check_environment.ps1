[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

function Test-CommandAvailable {
    param([Parameter(Mandatory = $true)][string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Write-Check {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][bool]$Passed,
        [Parameter(Mandatory = $true)][string]$Detail
    )
    $status = if ($Passed) { "PASS" } else { "WARN" }
    Write-Host "[$status] $Name - $Detail"
}

$workspaceRoot = Split-Path -Parent $PSScriptRoot
$pythonAvailable = (Test-CommandAvailable "python") -or (Test-CommandAvailable "py")
Write-Check -Name "Python" -Passed $pythonAvailable -Detail "Python command is available"

$gitAvailable = Test-CommandAvailable "git"
Write-Check -Name "Git" -Passed $gitAvailable -Detail "Git command is available"

$energyPlusFromEnv = $env:ENERGYPLUS_PATH
$energyPlusCommand = Test-CommandAvailable "energyplus"
$energyPlusAvailable = $energyPlusCommand -or (-not [string]::IsNullOrWhiteSpace($energyPlusFromEnv))
Write-Check -Name "EnergyPlus" -Passed $energyPlusAvailable -Detail "Set ENERGYPLUS_PATH or add energyplus to PATH"

$envFile = Join-Path $workspaceRoot ".env"
Write-Check -Name "Environment file" -Passed (Test-Path $envFile) -Detail "Copy .env.example to .env before running local services"

$qwenUrl = if ($env:QWEN_BASE_URL) { $env:QWEN_BASE_URL } else { "http://127.0.0.1:8000/v1" }
try {
    $health = Invoke-WebRequest -Uri "$qwenUrl/models" -TimeoutSec 2 -UseBasicParsing
    Write-Check -Name "Qwen endpoint" -Passed ($health.StatusCode -ge 200 -and $health.StatusCode -lt 300) -Detail $qwenUrl
}
catch {
    Write-Check -Name "Qwen endpoint" -Passed $false -Detail "Optional at Milestone 1; endpoint unavailable at $qwenUrl"
}

Write-Host "Environment diagnostics complete. Warnings must be resolved before their dependent milestone."
