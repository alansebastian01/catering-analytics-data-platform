# B2B Catering Analytics Platform - Production-Style Windows Reference

A complete, reproducible local data-engineering project for Windows + Docker Desktop:

**Python synthetic source -> MinIO landing -> Apache Hop orchestration -> PostgreSQL raw/audit -> dbt staging/marts -> Apache Superset BI**

> This is a **production-style learning/reference environment**, not a single-node production deployment. It uses production concepts such as least privilege, version pinning, health checks, audit manifests, quarantine, deterministic keys, data tests, backups, and read-only BI access while remaining runnable on one laptop.

## Start here

1. Read `docs/02-windows-prerequisites.md`.
2. Run:

```powershell
.\scripts\windows\bootstrap.ps1
notepad .env
.\scripts\windows\start.ps1
.\scripts\windows\health.ps1
.\scripts\windows\run-pipeline.ps1
```

3. Open:

- MinIO: `http://localhost:9001`
- Apache Hop Web: `http://localhost:8080`
- Apache Superset: `http://localhost:8088`
- PostgreSQL/DBeaver: `localhost:5432`

## Documentation map

- `docs/00-master-checklist.md` - end-to-end completion checklist.
- `docs/01-architecture.md` - responsibilities and end-to-end design.
- `docs/02-windows-prerequisites.md` - Windows/Docker preparation.
- `docs/03-first-run.md` - exact first-run instructions.
- `docs/04-data-generation-and-minio.md` - synthetic source and landing layout.
- `docs/05-dbeaver.md` - database connections and validation SQL.
- `docs/06-dbt.md` - dbt models, tests, and docs.
- `docs/07-apache-hop.md` - Hop orchestration design and container-boundary guidance.
- `docs/08-superset.md` - BI connection and dashboard plan.
- `docs/09-data-quality-reconciliation.md` - reject/quarantine/reconciliation strategy.
- `docs/10-operations.md` - logs, backup, stop/start/reset.
- `docs/11-troubleshooting.md` - common Windows/Docker failures.
- `docs/12-security-production-readiness.md` - what is production-like and what still must change.
- `docs/13-version-policy.md` - current version choices and MinIO caveat.
- `docs/14-project-walkthrough.md` - interview/demo narrative.
- `docs/15-roadmap-to-andela-reference.md` - next steps toward database-per-service + Kafka + Snowflake.
- `docs/16-dashboard-kpis.md` - KPI definitions and validation SQL.

## Repository layout

```text
.
|-- compose.yaml
|-- .env.example
|-- src/                         Python source generation, ingestion, reconciliation
|-- dbt/                         staging + dimensional marts + tests
|-- postgres/init/               extensions, roles, audit schema
|-- minio/policies/              pipeline least-privilege policy
|-- docker/minio/                source-built pinned MinIO server
|-- docker/pipeline/             reproducible Python/dbt runtime
|-- docker/superset/             pinned Superset image + Postgres driver
|-- hop/                         Hop orchestration guidance/project folder
|-- scripts/windows/             bootstrap/start/health/run/backup/reset
|-- docs/                        complete implementation and operations guide
|-- diagrams/                    architecture reference image
|-- backups/                     local backup output (gitignored)
`-- logs/                        pipeline logs (gitignored)
```

## Normal daily workflow

```powershell
# Start services
.\scripts\windows\start.ps1

# Run one new batch end to end
.\scripts\windows\run-pipeline.ps1

# Build/test dbt only
.\scripts\windows\dbt-build.ps1

# Stop containers while preserving volumes
.\scripts\windows\stop.ps1
```

## What success looks like

After a successful pipeline run:

- a new date-partitioned source batch exists in MinIO `landing`;
- each accepted source object is registered in `audit.ingested_objects`;
- invalid rows, if any, appear in `audit.rejected_rows` and MinIO `quarantine`;
- raw PostgreSQL tables contain source lineage fields;
- `staging` and `marts` contain dbt models;
- `dbt build` passes;
- Superset can read the marts through the `bi_reader` account;
- rerunning is safe because previously ingested object versions are skipped.

Read `docs/03-first-run.md` before starting.
