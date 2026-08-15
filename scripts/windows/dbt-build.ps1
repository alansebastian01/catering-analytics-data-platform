$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")
docker compose --profile tools run --rm pipeline dbt build --project-dir /app/dbt --profiles-dir /app/dbt
