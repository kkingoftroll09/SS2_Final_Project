<# PowerShell helper to run Alembic migrations from the backend folder #>
Set-StrictMode -Version Latest
Push-Location $PSScriptRoot
try {
    alembic upgrade head
} finally {
    Pop-Location
}
