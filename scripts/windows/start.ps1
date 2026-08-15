$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")

docker compose pull postgres minio-init hop-web superset-meta redis
docker compose build minio pipeline superset superset-init
docker compose up -d postgres minio minio-init superset-meta redis superset-init superset hop-web

docker compose ps
Write-Host "Services started. Run .\scripts\windows\health.ps1 before the first pipeline." -ForegroundColor Green
