from __future__ import annotations

import csv
import io
import json
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import psycopg
from psycopg import sql

from .common import configure_logging, ingest_dsn, s3_client

log = configure_logging()
RAW_BUCKET = os.getenv("MINIO_RAW_BUCKET", "landing")
QUARANTINE_BUCKET = os.getenv("MINIO_QUARANTINE_BUCKET", "quarantine")

TABLES = {
    "customers": {
        "columns": ["customer_id", "customer_name", "city", "state", "segment", "created_at", "batch_id"],
        "ddl": """
            CREATE TABLE IF NOT EXISTS raw.customers (
                customer_id UUID PRIMARY KEY,
                customer_name TEXT NOT NULL,
                city TEXT,
                state TEXT,
                segment TEXT NOT NULL CHECK (segment IN ('SMB','MID_MARKET','ENTERPRISE')),
                created_at TIMESTAMPTZ NOT NULL,
                batch_id TEXT NOT NULL,
                _loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                _source_object TEXT NOT NULL
            )
        """,
    },
    "products": {
        "columns": ["product_id", "product_name", "category", "brand", "unit_price", "updated_at", "batch_id"],
        "ddl": """
            CREATE TABLE IF NOT EXISTS raw.products (
                product_id UUID PRIMARY KEY,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                brand TEXT,
                unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
                updated_at TIMESTAMPTZ NOT NULL,
                batch_id TEXT NOT NULL,
                _loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                _source_object TEXT NOT NULL
            )
        """,
    },
    "orders": {
        "columns": ["order_id", "order_number", "customer_id", "payment_id", "order_ts", "order_status", "total_amount", "currency", "batch_id"],
        "ddl": """
            CREATE TABLE IF NOT EXISTS raw.orders (
                order_id UUID PRIMARY KEY,
                order_number TEXT UNIQUE NOT NULL,
                customer_id UUID NOT NULL,
                payment_id UUID NOT NULL,
                order_ts TIMESTAMPTZ NOT NULL,
                order_status TEXT NOT NULL CHECK (order_status IN ('DELIVERED','CONFIRMED','CANCELLED')),
                total_amount NUMERIC(14,2) NOT NULL CHECK (total_amount >= 0),
                currency CHAR(3) NOT NULL,
                batch_id TEXT NOT NULL,
                _loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                _source_object TEXT NOT NULL
            )
        """,
    },
    "order_items": {
        "columns": ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "line_amount", "batch_id"],
        "ddl": """
            CREATE TABLE IF NOT EXISTS raw.order_items (
                order_item_id UUID PRIMARY KEY,
                order_id UUID NOT NULL,
                product_id UUID NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
                line_amount NUMERIC(14,2) NOT NULL CHECK (line_amount >= 0),
                batch_id TEXT NOT NULL,
                _loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                _source_object TEXT NOT NULL
            )
        """,
    },
    "payments": {
        "columns": ["payment_id", "order_id", "payment_method", "payment_status", "payment_amount", "created_at", "batch_id"],
        "ddl": """
            CREATE TABLE IF NOT EXISTS raw.payments (
                payment_id UUID PRIMARY KEY,
                order_id UUID NOT NULL,
                payment_method TEXT NOT NULL CHECK (payment_method IN ('CARD','ACH','INVOICE')),
                payment_status TEXT NOT NULL CHECK (payment_status IN ('PAID','AUTHORIZED','VOID')),
                payment_amount NUMERIC(14,2) NOT NULL CHECK (payment_amount >= 0),
                created_at TIMESTAMPTZ NOT NULL,
                batch_id TEXT NOT NULL,
                _loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                _source_object TEXT NOT NULL
            )
        """,
    },
}


def validate(entity: str, row: dict) -> str | None:
    try:
        if entity == "customers" and row.get("segment") not in {"SMB", "MID_MARKET", "ENTERPRISE"}:
            return "invalid customer segment"
        if entity == "orders":
            if row.get("order_status") not in {"DELIVERED", "CONFIRMED", "CANCELLED"}:
                return "invalid order status"
            if Decimal(row.get("total_amount", "-1")) < 0:
                return "negative total_amount"
        if entity == "order_items":
            if int(row.get("quantity", "0")) <= 0:
                return "quantity must be positive"
            if Decimal(row.get("line_amount", "-1")) < 0:
                return "negative line_amount"
        if entity == "payments" and Decimal(row.get("payment_amount", "-1")) < 0:
            return "negative payment_amount"
        if entity == "products" and Decimal(row.get("unit_price", "-1")) < 0:
            return "negative unit_price"
    except (ValueError, TypeError, InvalidOperation):
        return "numeric/type validation failed"
    return None


def ensure_tables(conn) -> None:
    with conn.cursor() as cur:
        for cfg in TABLES.values():
            cur.execute(cfg["ddl"])
        cur.execute("CREATE INDEX IF NOT EXISTS ix_raw_orders_order_ts ON raw.orders(order_ts)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_raw_orders_customer_id ON raw.orders(customer_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_raw_order_items_order_id ON raw.order_items(order_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_raw_order_items_product_id ON raw.order_items(product_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_raw_payments_order_id ON raw.payments(order_id)")
    conn.commit()


def already_loaded(conn, key: str, etag: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM audit.ingested_objects WHERE bucket_name=%s AND object_key=%s AND etag=%s",
            (RAW_BUCKET, key, etag),
        )
        return cur.fetchone() is not None


def quarantine(client, run_id: str, entity: str, source_key: str, rejects: list[dict]) -> None:
    if not rejects:
        return
    key = f"{entity}/run_id={run_id}/{source_key.rsplit('/', 1)[-1]}.rejects.jsonl"
    body = "\n".join(json.dumps(r, default=str) for r in rejects).encode("utf-8")
    client.put_object(Bucket=QUARANTINE_BUCKET, Key=key, Body=body, ContentType="application/x-ndjson")
    log.warning("quarantined rows=%s to s3://%s/%s", len(rejects), QUARANTINE_BUCKET, key)


def load_object(conn, client, run_id: str, entity: str, cfg: dict, key: str, etag: str) -> tuple[int, int]:
    response = client.get_object(Bucket=RAW_BUCKET, Key=key)
    reader = csv.DictReader(io.StringIO(response["Body"].read().decode("utf-8-sig")))
    columns = cfg["columns"]
    insert_cols = columns + ["_source_object"]
    placeholders = sql.SQL(", ").join(sql.Placeholder() for _ in insert_cols)
    stmt = sql.SQL("INSERT INTO raw.{} ({}) VALUES ({}) ON CONFLICT DO NOTHING").format(
        sql.Identifier(entity), sql.SQL(", ").join(map(sql.Identifier, insert_cols)), placeholders
    )

    inserted = 0
    rejects: list[dict] = []
    with conn.cursor() as cur:
        for row_number, row in enumerate(reader, start=2):
            reason = validate(entity, row)
            if reason:
                rejects.append({"row_number": row_number, "reason": reason, "record": row})
                cur.execute(
                    "INSERT INTO audit.rejected_rows(run_id,entity_name,source_object,row_number,raw_record,reason) VALUES(%s,%s,%s,%s,%s::jsonb,%s)",
                    (run_id, entity, key, row_number, json.dumps(row), reason),
                )
                continue
            values = [row.get(c) if row.get(c) != "" else None for c in columns] + [key]
            cur.execute(stmt, values)
            inserted += cur.rowcount

        cur.execute(
            "INSERT INTO audit.ingested_objects(bucket_name,object_key,etag,entity_name,row_count,run_id) VALUES(%s,%s,%s,%s,%s,%s)",
            (RAW_BUCKET, key, etag, entity, inserted, run_id),
        )
    quarantine(client, run_id, entity, key, rejects)
    log.info("processed s3://%s/%s inserted=%s rejected=%s", RAW_BUCKET, key, inserted, len(rejects))
    return inserted, len(rejects)


def main(batch_id: str | None = None) -> dict:
    run_id = str(uuid.uuid4())
    client = s3_client()
    total_rows = 0
    objects_processed = 0
    total_rejects = 0
    with psycopg.connect(ingest_dsn()) as conn:
        ensure_tables(conn)
        with conn.cursor() as cur:
            cur.execute("INSERT INTO audit.pipeline_runs(run_id,batch_id,status) VALUES(%s,%s,'RUNNING')", (run_id, batch_id))
        conn.commit()
        try:
            for entity, cfg in TABLES.items():
                paginator = client.get_paginator("list_objects_v2")
                for page in paginator.paginate(Bucket=RAW_BUCKET, Prefix=f"{entity}/"):
                    for obj in page.get("Contents", []):
                        key = obj["Key"]
                        if not key.endswith(".csv"):
                            continue
                        etag = obj["ETag"].strip('"')
                        if already_loaded(conn, key, etag):
                            continue
                        inserted, rejected = load_object(conn, client, run_id, entity, cfg, key, etag)
                        conn.commit()
                        total_rows += inserted
                        total_rejects += rejected
                        objects_processed += 1

            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE audit.pipeline_runs
                       SET status='SUCCESS', completed_at=%s, rows_loaded=%s, objects_processed=%s, message=%s
                       WHERE run_id=%s""",
                    (datetime.now(timezone.utc), total_rows, objects_processed, f"rejected_rows={total_rejects}", run_id),
                )
            conn.commit()
            result = {"run_id": run_id, "rows_loaded": total_rows, "objects_processed": objects_processed, "rejected_rows": total_rejects}
            log.info("ingestion completed %s", result)
            return result
        except Exception as exc:
            conn.rollback()
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE audit.pipeline_runs SET status='FAILED', completed_at=%s, message=%s WHERE run_id=%s",
                    (datetime.now(timezone.utc), str(exc)[:4000], run_id),
                )
            conn.commit()
            raise


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
