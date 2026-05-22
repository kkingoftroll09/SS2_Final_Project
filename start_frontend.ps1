# Start frontend static server (Windows PowerShell)
# Run from project root
Set-Location -Path (Join-Path $PSScriptRoot 'frontend booking hotel management')
python -m http.server 5500
