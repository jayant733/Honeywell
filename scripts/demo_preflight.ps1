Write-Host "Sentinel Twin - Demo Preflight Check"
Write-Host "====================================="

$services = @(
    @{ Name="FastAPI Backend"; Port=8000; URL="http://localhost:8000/docs" }
    @{ Name="Next.js Dashboard"; Port=3000; URL="http://localhost:3000" }
)

$all_pass = $true

foreach ($svc in $services) {
    Write-Host "Checking $($svc.Name) on port $($svc.Port)..." -NoNewline
    $connection = Test-NetConnection -ComputerName localhost -Port $svc.Port -WarningAction SilentlyContinue
    if ($connection.TcpTestSucceeded) {
        Write-Host " [OK]" -ForegroundColor Green
    } else {
        Write-Host " [FAIL]" -ForegroundColor Red
        $all_pass = $false
    }
}

if ($all_pass) {
    Write-Host "`nPreflight complete. All services are GO for demo." -ForegroundColor Green
} else {
    Write-Host "`nPreflight failed. Start missing services before demo." -ForegroundColor Red
}
