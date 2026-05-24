<# PowerShell helper to create the PostgreSQL schema from ORM models #>
Set-StrictMode -Version Latest
Push-Location $PSScriptRoot
try {
    python render_migrate.py
} finally {
    Pop-Location
}
