# Start backend (Windows PowerShell)
# Run from project root
$venv = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$backendDir = Join-Path $PSScriptRoot "hotel_backend"
$port = 8000

if (-Not (Test-Path $venv)) {
    Write-Host "Virtualenv python not found at $venv. Activate your venv or adjust path."
    exit 1
}

if (-Not (Test-Path $backendDir)) {
    Write-Host "Backend directory not found at $backendDir"
    exit 1
}

$listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($listener) {
    Write-Host "Port $port is already in use by PID $($listener.OwningProcess)."
    $isHealthy = $false
    try {
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:$port/" -Method Get -TimeoutSec 3 -ErrorAction Stop
        if ($resp.message) { $isHealthy = $true }
    }
    catch {
        $isHealthy = $false
    }

    if ($isHealthy) {
        Write-Host "Backend is already running at http://127.0.0.1:$port"
        exit 0
    }
    Write-Host "Port is occupied but health check failed. Stop the process using PID $($listener.OwningProcess) and retry."
    exit 1
}

Push-Location $backendDir
try {
    & $venv -m uvicorn main:app --host 127.0.0.1 --port $port
}
finally {
    Pop-Location
}
