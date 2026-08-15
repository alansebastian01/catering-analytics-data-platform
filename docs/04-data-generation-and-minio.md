# 04 - Synthetic source and MinIO landing

The synthetic generator is `src/generate_and_land.py`. Each invocation creates a new immutable batch with a unique `batch_id`, then writes CSV source objects and an NDJSON event file directly to the `landing` bucket.

Object layout:

```text
landing/
  customers/ingest_date=YYYY-MM-DD/customers_<batch>.csv
  products/ingest_date=YYYY-MM-DD/products_<batch>.csv
  orders/ingest_date=YYYY-MM-DD/orders_<batch>.csv
  order_items/ingest_date=YYYY-MM-DD/order_items_<batch>.csv
  payments/ingest_date=YYYY-MM-DD/payments_<batch>.csv
  events/order_created/ingest_date=YYYY-MM-DD/order_created_<batch>.jsonl
  _manifests/ingest_date=YYYY-MM-DD/manifest_<batch>.json
```

The date partition is operational metadata; the business event time remains in the row. That distinction matters when late data arrives.

## Generate only

```powershell
docker compose --profile tools run --rm pipeline python -m src.generate_and_land
```

## Scale a batch

Edit `.env`:

```text
ORDER_COUNT=50000
CUSTOMER_COUNT=2000
PRODUCT_COUNT=500
```

Then generate again. For laptop testing, increase gradually.

## Security model

The pipeline does not use the MinIO root account. `minio-init` creates a separate `pipeline` identity and attaches an object read/write policy. This is a least-privilege pattern suitable for a portfolio demonstration.
