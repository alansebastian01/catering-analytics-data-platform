# 14 - End-to-end walkthrough for interviews

## Business problem

A catering marketplace needs a reproducible analytical pipeline that lands source-system extracts, maintains lineage and rerun safety, transforms them into a star schema, and exposes trusted KPIs.

## Architecture story

“I generate transactional source batches in Python and land them into partitioned S3-compatible MinIO objects. The ingestion job keeps an object-level manifest keyed by ETag, validates rows, quarantines invalid records, and writes accepted records into PostgreSQL raw tables with source-object lineage. Apache Hop is the orchestration layer. dbt builds and tests stable dimensions and facts in PostgreSQL. Superset connects with a read-only role for analytics. Audit tables and reconciliation checks make the pipeline observable and rerunnable.”

## Engineering decisions worth explaining

1. **Immutable landing files** make replay and audit easier.
2. **Object ETag manifest** prevents expensive/ambiguous repeated ingestion.
3. **Separate DB roles** demonstrate least privilege.
4. **dbt owns SQL modeling** while Hop owns orchestration, preventing tool overlap.
5. **Deterministic surrogate keys** stay stable as data grows.
6. **Quarantine plus constraints plus dbt tests** create layered data quality.
7. **Read-only BI account** prevents dashboard workloads from modifying warehouse data.
8. **Version pins** make the local demo reproducible.

## Suggested live demo

1. Show a new MinIO batch.
2. Run the pipeline.
3. Show the audit run and ingested object manifest in DBeaver.
4. Show `fact_orders` and `fact_order_items`.
5. Run the pipeline a second time and explain why old objects are skipped while the new generated batch is loaded.
6. Run `dbt build` and show tests passing.
7. Open Superset and show revenue/order KPIs.
8. Show `pg_stat_statements` or `EXPLAIN ANALYZE` for a warehouse query.
