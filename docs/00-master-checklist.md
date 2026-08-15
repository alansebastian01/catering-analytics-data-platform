# 00 - Master implementation checklist

Use this as the project completion tracker.

## Environment

- [ ] Docker Desktop starts with the WSL2 backend.
- [ ] `docker version` and `docker compose version` work.
- [ ] Project is extracted outside OneDrive.
- [ ] `.env` exists and all default `ChangeMe_*` values are replaced.
- [ ] `SUPERSET_SECRET_KEY` is replaced with a long random value.

## Infrastructure

- [ ] PostgreSQL is healthy.
- [ ] MinIO is healthy and has landing/curated/quarantine buckets.
- [ ] Pipeline MinIO user exists.
- [ ] Apache Hop Web opens.
- [ ] Superset opens and login works.
- [ ] DBeaver connects to PostgreSQL.

## Pipeline

- [ ] Python generates a new batch.
- [ ] New files appear under date-partitioned MinIO keys.
- [ ] Loader processes only previously unseen object versions.
- [ ] `audit.pipeline_runs` has a SUCCESS row.
- [ ] `audit.ingested_objects` contains the batch source objects.
- [ ] Reconciliation exits successfully.
- [ ] `dbt build` passes.
- [ ] `marts.fact_orders` and `marts.fact_order_items` contain rows.

## BI

- [ ] Superset connects with the `bi_reader` role, not admin.
- [ ] At least one dataset is created from a mart table.
- [ ] KPI dashboard contains revenue, orders, AOV, and category/segment cuts.
- [ ] Dashboard results are cross-checked in DBeaver.

## Reliability demo

- [ ] Run the pipeline twice.
- [ ] Existing object versions are skipped using `audit.ingested_objects`.
- [ ] New generated batch loads successfully.
- [ ] Backup script creates a dump.
- [ ] Full reset is understood before use.

## Portfolio documentation

- [ ] Architecture diagram included.
- [ ] README has exact startup commands.
- [ ] Data quality and idempotency are explained.
- [ ] Tool responsibilities are explicit: Hop=orchestration, dbt=SQL transformation.
- [ ] Production gaps and next-step Kafka/Snowflake roadmap are documented.
