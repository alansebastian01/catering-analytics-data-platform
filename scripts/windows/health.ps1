$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")

docker compose ps
Write-Host "Checking PostgreSQL..."
docker compose exec -T postgres pg_isready -U $((Get-Content .env | Select-String '^POSTGRES_ADMIN_USER=').ToString().Split('=')[1]) -d $((Get-Content .env | Select-String '^POSTGRES_DB=').ToString().Split('=')[1])
Write-Host "Checking MinIO..."
try { Invoke-WebRequest -UseBasicParsing http://localhost:9000/minio/health/live | Out-Null; Write-Host "MinIO OK" -ForegroundColor Green } catch { Write-Warning "MinIO not ready yet" }
Write-Host "Checking Superset..."
try { Invoke-WebRequest -UseBasicParsing http://localhost:8088/health | Out-Null; Write-Host "Superset OK" -ForegroundColor Green } catch { Write-Warning "Superset may still be initializing; inspect docker compose logs superset-init" }
