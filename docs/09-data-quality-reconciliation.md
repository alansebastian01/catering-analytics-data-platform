# 09 - Data quality, quarantine, and reconciliation

Data quality occurs at three layers.

## Ingestion checks

Python validates critical numeric values and known statuses before insert. Invalid rows are written to both `audit.rejected_rows` and the MinIO `quarantine` bucket. Database CHECK constraints provide an independent second line of defense.

## Reconciliation checks

`src/reconcile.py` validates:

- order items without an order,
- payments without an order,
- negative order totals,
- order-item arithmetic mismatches.

The pipeline exits non-zero if any reconciliation count is non-zero.

Run reconciliation by itself:

```powershell
docker compose --profile tools run --rm pipeline python -m src.reconcile
```

## dbt checks

`dbt build` checks model-level contracts including uniqueness, accepted values, relationships, and business assertions.

## How to demo a failure

For an interview demo, copy a source file to a test key, deliberately change a quantity or status, and rerun ingestion. Do not alter your only source copy. Show that the bad row appears in `audit.rejected_rows` and the quarantine bucket while valid rows continue loading.
