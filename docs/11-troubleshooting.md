# 11 - Troubleshooting

## Port already in use

Check:

```powershell
Get-NetTCPConnection -State Listen | Where-Object LocalPort -in 5432,8080,8088,9000,9001
```

Change the corresponding port in `.env` if another application owns it.

## Superset is not ready

```powershell
docker compose ps
docker compose logs superset-init
docker compose logs superset
```

The one-shot `superset-init` container should exit with code 0. If credentials or the secret key changed after metadata was initialized, review the logs before resetting data.

## MinIO login works but pipeline receives AccessDenied

```powershell
docker compose logs minio-init
```

Confirm the pipeline identity and policy were created. If you changed bucket names after the first deployment, also update `minio/policies/pipeline-rw.json` because the policy contains bucket ARNs.

## PostgreSQL tables do not exist

Initialization scripts run only when the PostgreSQL volume is created. If you modified `postgres/init` after first boot, either apply changes manually or use the destructive reset script in a disposable environment.

## dbt relationship test fails

Inspect source ingestion counts and orphan checks first. Relationship failures often indicate partial/raw ingestion, not a dbt defect.

## Docker Desktop is slow

Keep the project outside OneDrive, ensure WSL2 is enabled, assign sufficient RAM/CPU, and avoid very large synthetic batches until the pipeline works at small scale.
