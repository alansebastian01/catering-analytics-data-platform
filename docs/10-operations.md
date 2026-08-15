# 10 - Operations: start, stop, logs, backup, reset

## Status

```powershell
docker compose ps
```

## Logs

```powershell
docker compose logs -f postgres
docker compose logs -f minio
docker compose logs -f superset
docker compose logs -f hop-web
Get-Content .\logs\pipeline.log -Wait
```

Docker log rotation is configured to prevent unlimited JSON logs from consuming disk.

## Stop without deleting data

```powershell
.\scripts\windows\stop.ps1
```

## Start again

```powershell
.\scripts\windows\start.ps1
```

## PostgreSQL backup

```powershell
.\scripts\windows\backup.ps1
```

The script creates a PostgreSQL custom-format dump in `backups/`. A real production policy must also back up object storage, Superset metadata, encryption keys/secrets, and test restores regularly.

## Full destructive reset

```powershell
.\scripts\windows\reset.ps1
```

The script requires typing `RESET` and then removes all Docker volumes. This deletes local PostgreSQL, MinIO objects, Superset metadata, Redis data, and Hop volume data.
