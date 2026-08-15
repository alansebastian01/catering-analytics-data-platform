# 06 - dbt transformation, tests, and lineage

The dbt project transforms the PostgreSQL `raw` schema into staging views and analytics marts.

## Run the complete dbt build

```powershell
.\scripts\windows\dbt-build.ps1
```

Equivalent command:

```powershell
docker compose --profile tools run --rm pipeline dbt build --project-dir /app/dbt --profiles-dir /app/dbt
```

`dbt build` executes models and tests in dependency order.

## Layering

```text
raw.*
  -> staging views
      -> dim_date
      -> dim_customer
      -> dim_product
      -> dim_payment
      -> fact_orders
      -> fact_order_items
```

## Why deterministic keys

Dimension keys are `md5(UUID)`, not `row_number()`. A row number can change when historical rows are reloaded or sort order changes; a deterministic hash remains stable for the same business key.

## Included tests

The project checks uniqueness/not-null business keys, accepted status values, dimensional referential integrity, non-negative amounts, and arithmetic consistency between quantity, unit price, and line amount.

## Generate dbt documentation

```powershell
docker compose --profile tools run --rm pipeline dbt docs generate --project-dir /app/dbt --profiles-dir /app/dbt
```

To browse docs interactively, run a temporary container with a published port or copy `dbt/target` to your host and serve it with a local web server. The production pattern is to publish generated dbt artifacts from CI.

## Future upgrade

When the project moves to Snowflake, retain the staging/mart contracts and replace the profile/warehouse-specific SQL as needed. The Andela reference explicitly places dbt in the analytical data platform, so this separation is intentional.
