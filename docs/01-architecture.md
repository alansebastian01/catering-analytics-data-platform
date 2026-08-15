# 01 - Architecture and responsibilities

## Target local architecture

```text
Synthetic OLTP Generator (Python)
              |
              v
       MinIO LANDING bucket
              |
              v
      Apache Hop orchestration
              |
              v
     PostgreSQL RAW + AUDIT
              |
              v
        dbt staging layer
              |
              v
      dbt dimensional MARTS
              |
              v
        Apache Superset
              |
              v
       Business dashboards
```

The design separates responsibilities deliberately:

- **Python** creates reproducible source batches and writes raw files to object storage.
- **MinIO** is the local S3-compatible landing/quarantine/curated object store.
- **Apache Hop** is the workflow/orchestration layer, not the main SQL modeling engine.
- **PostgreSQL raw** is the warehouse ingestion boundary and retains lineage metadata.
- **dbt** owns SQL transformations, dimensional modeling, lineage, documentation, and tests.
- **PostgreSQL marts** hold analytics-ready facts and dimensions.
- **Superset** reads the marts through a read-only BI database role.
- **Audit tables** record pipeline runs, ingested objects, and rejected rows.

## Why this is stronger than a simple ETL demo

The ingestion loader tracks each MinIO object by bucket, key, and ETag. A rerun therefore skips already-processed immutable source files rather than repeatedly scanning and attempting inserts. Data quality failures are separated from good rows, written to `audit.rejected_rows`, and copied to a quarantine bucket. dbt uses deterministic hash surrogate keys rather than row numbers, avoiding dimension-key churn when data grows.

## Local versus real production

This package is a **production-style local reference implementation**, not a claim that a single Windows laptop is a production platform. In real production you would add managed PostgreSQL/Snowflake, managed S3, centralized secrets, TLS, SSO/RBAC, network isolation, HA, monitoring/alerting, backups with restore drills, CI/CD, and a supported scheduler/runtime.
