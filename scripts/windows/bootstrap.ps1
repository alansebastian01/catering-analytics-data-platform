$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example." -ForegroundColor Yellow
    Write-Host "Edit .env and replace every ChangeMe_* value before sharing or exposing services." -ForegroundColor Yellow
}

New-Item -ItemType Directory -Force -Path "logs", "backups" | Out-Null

docker compose config --quiet
Write-Host "Compose configuration is valid." -ForegroundColor Green
Write-Host "Next: .\scripts\windows\start.ps1" -ForegroundColor Cyan
