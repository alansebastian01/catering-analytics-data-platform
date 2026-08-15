$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
New-Item -ItemType Directory -Force -Path backups | Out-Null
$envLines = Get-Content .env
$db = ($envLines | Select-String '^POSTGRES_DB=').ToString().Split('=')[1]
$user = ($envLines | Select-String '^POSTGRES_ADMIN_USER=').ToString().Split('=')[1]
$out = "backups\analytics_$timestamp.dump"
docker compose exec -T postgres pg_dump -U $user -d $db -Fc > $out
Write-Host "Created $out" -ForegroundColor Green
