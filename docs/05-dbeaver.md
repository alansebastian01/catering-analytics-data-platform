# 05 - DBeaver guide

## Administrator connection

Use values from `.env`:

```text
Host: localhost
Port: 5432
Database: analytics
Username: platform_admin
Password: <POSTGRES_ADMIN_PASSWORD>
```

This account is for development administration only.

## BI read-only connection

```text
Host: localhost
Port: 5432
Database: analytics
Username: bi_reader
Password: <BI_READER_PASSWORD>
```

This is the account to demonstrate least-privilege reporting access.

## Schemas

- `raw`: ingested immutable-ish records with `_source_object` and `_loaded_at` lineage.
- `audit`: pipeline runs, ingested object manifest, rejected rows.
- `staging`: dbt staging views. dbt prefixes custom schemas with the target schema by default.
- `marts`: dbt dimensions/facts.

## Useful verification SQL

```sql
select * from audit.pipeline_runs order by started_at desc limit 20;
select * from audit.ingested_objects order by loaded_at desc limit 20;
select * from audit.rejected_rows order by rejected_at desc limit 20;

select count(*) from raw.orders;
select count(*) from marts.fact_orders;
select count(*) from marts.fact_order_items;

select
  date_trunc('month', order_ts) as month,
  sum(total_amount) as gross_order_value,
  count(*) as orders
from marts.fact_orders
where order_status <> 'CANCELLED'
group by 1
order by 1;
```

## Query-performance check

PostgreSQL is started with `pg_stat_statements`. As administrator:

```sql
select calls, total_exec_time, mean_exec_time, rows, left(query, 160) as query
from pg_stat_statements
order by total_exec_time desc
limit 20;
```

Use `EXPLAIN (ANALYZE, BUFFERS)` for specific queries when documenting indexing decisions.
