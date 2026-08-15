$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")
$answer = Read-Host "This deletes ALL local PostgreSQL, MinIO, Superset, Redis, and Hop volumes. Type RESET to continue"
if ($answer -ne "RESET") { Write-Host "Cancelled."; exit 0 }
docker compose down -v --remove-orphans
Write-Host "Local environment deleted." -ForegroundColor Yellow
