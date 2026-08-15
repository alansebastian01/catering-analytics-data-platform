# 03 - First run: exact procedure

## 1. Extract the project

Example:

```text
C:\data-engineering\catering-analytics
```

Open PowerShell in that directory.

## 2. Create local configuration

```powershell
.\scripts\windows\bootstrap.ps1
notepad .env
```

Change at least every `ChangeMe_*` value and replace `SUPERSET_SECRET_KEY` with a long random string. The defaults bind published ports to `127.0.0.1`, so they are accessible only from your laptop.

## 3. Start infrastructure

```powershell
.\scripts\windows\start.ps1
```

The first run downloads several images and may take time. Watch initialization with:

```powershell
docker compose logs -f superset-init
docker compose logs -f minio-init
```

Press `Ctrl+C` to stop following logs; it does not stop the containers.

## 4. Check health

```powershell
.\scripts\windows\health.ps1
```

## 5. Run the data pipeline

```powershell
.\scripts\windows\run-pipeline.ps1
```

Expected high-level output:

```text
uploaded s3://landing/...
generation completed batch_id=...
processed s3://landing/... inserted=...
ingestion completed {...}
reconciliation checks all zero
Running dbt build...
PASS ...
Pipeline completed successfully.
```

## 6. Validate in MinIO

Open `http://localhost:9001`. Sign in using the root credentials from `.env`. You should see `landing`, `curated`, and `quarantine` buckets.

## 7. Validate in DBeaver

Use the administrator connection from `.env` or the read-only BI account. See `docs/05-dbeaver.md`.

## 8. Validate Superset

Open `http://localhost:8088` and sign in with the Superset admin credentials from `.env`. Create a PostgreSQL connection using the `bi_reader` account. See `docs/08-superset.md`.
