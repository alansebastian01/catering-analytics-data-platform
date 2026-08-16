from __future__ import annotations

import csv
import io
import json
import os
import random
import uuid
from datetime import datetime, timedelta, timezone

from faker import Faker

from .common import configure_logging, s3_client

log = configure_logging()
RAW_BUCKET = os.getenv("MINIO_RAW_BUCKET", "landing")


def uid() -> str:
    return str(uuid.uuid4())


def upload_csv(client, key: str, rows: list[dict]) -> None:
    buffer = io.StringIO(newline="")

    writer = csv.DictWriter(
        buffer,
        fieldnames=list(rows[0].keys()),
    )

    writer.writeheader()
    writer.writerows(rows)

    client.put_object(
        Bucket=RAW_BUCKET,
        Key=key,
        Body=buffer.getvalue().encode("utf-8"),
        ContentType="text/csv",
    )

    log.info(
        "uploaded s3://%s/%s rows=%s",
        RAW_BUCKET,
        key,
        len(rows),
    )


def upload_jsonl(client, key: str, rows: list[dict]) -> None:
    body = "\n".join(
        json.dumps(
            row,
            default=str,
            separators=(",", ":"),
        )
        for row in rows
    ).encode("utf-8")

    client.put_object(
        Bucket=RAW_BUCKET,
        Key=key,
        Body=body,
        ContentType="application/x-ndjson",
    )

    log.info(
        "uploaded s3://%s/%s rows=%s",
        RAW_BUCKET,
        key,
        len(rows),
    )


def inject_bad_records(
    rows: list[dict],
    percent: float,
    corrupt_fn,
) -> int:
    """
    Intentionally corrupt a percentage of rows.

    This generator is used only for testing:
    - ingestion validation
    - audit.rejected_rows
    - MinIO quarantine
    - clean RAW-layer protection
    """

    if not rows or percent <= 0:
        return 0

    bad_count = max(
        1,
        int(len(rows) * (percent / 100.0)),
    )

    bad_count = min(
        bad_count,
        len(rows),
    )

    selected_rows = random.sample(
        rows,
        bad_count,
    )

    for row in selected_rows:
        corrupt_fn(row)

    return bad_count


def main() -> str:
    seed = int(
        os.getenv(
            "GENERATOR_SEED",
            "42",
        )
    ) + int(
        datetime.now(
            timezone.utc
        ).strftime("%j%H%M")
    )

    random.seed(seed)

    fake = Faker()
    Faker.seed(seed)

    order_count = int(
        os.getenv(
            "ORDER_COUNT",
            "5000",
        )
    )

    customer_count = int(
        os.getenv(
            "CUSTOMER_COUNT",
            "250",
        )
    )

    product_count = int(
        os.getenv(
            "PRODUCT_COUNT",
            "80",
        )
    )

    bad_record_percent = float(
        os.getenv(
            "BAD_RECORD_PERCENT",
            "2",
        )
    )

    if bad_record_percent <= 0:
        log.warning(
            "BAD_RECORD_PERCENT is %s. "
            "This bad-data generator will produce no invalid rows.",
            bad_record_percent,
        )

    now = datetime.now(
        timezone.utc
    )

    batch_id = (
        now.strftime(
            "%Y%m%dT%H%M%SZ"
        )
        + "-bad-"
        + uuid.uuid4().hex[:8]
    )

    partition = now.strftime(
        "ingest_date=%Y-%m-%d"
    )

    # ---------------------------------------------------------
    # Customers
    # ---------------------------------------------------------

    customers = [
        {
            "customer_id": uid(),
            "customer_name": fake.company(),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "segment": random.choice(
                [
                    "SMB",
                    "MID_MARKET",
                    "ENTERPRISE",
                ]
            ),
            "created_at": (
                now
                - timedelta(
                    days=random.randint(
                        30,
                        900,
                    )
                )
            ).isoformat(),
            "batch_id": batch_id,
        }
        for _ in range(
            customer_count
        )
    ]

    # ---------------------------------------------------------
    # Products
    # ---------------------------------------------------------

    categories = [
        "BREAKFAST",
        "LUNCH",
        "DINNER",
        "BEVERAGE",
        "DESSERT",
    ]

    products = [
        {
            "product_id": uid(),
            "product_name": (
                f"Menu Item {i + 1:03d}"
            ),
            "category": random.choice(
                categories
            ),
            "brand": random.choice(
                [
                    "KitchenCo",
                    "FreshBite",
                    "UrbanPlate",
                    "CaterPro",
                ]
            ),
            "unit_price": round(
                random.uniform(
                    8,
                    45,
                ),
                2,
            ),
            "updated_at": now.isoformat(),
            "batch_id": batch_id,
        }
        for i in range(
            product_count
        )
    ]

    # ---------------------------------------------------------
    # Orders / order items / payments / events
    # ---------------------------------------------------------

    orders = []
    order_items = []
    payments = []
    events = []

    for n in range(
        1,
        order_count + 1,
    ):
        order_id = uid()

        customer = random.choice(
            customers
        )

        order_ts = (
            now
            - timedelta(
                days=random.randint(
                    0,
                    179,
                ),
                seconds=random.randint(
                    0,
                    86399,
                ),
            )
        )

        selected = random.sample(
            products,
            k=random.randint(
                1,
                min(
                    5,
                    len(products),
                ),
            ),
        )

        total = 0.0

        for product in selected:
            quantity = random.randint(
                1,
                15,
            )

            line_amount = round(
                quantity
                * float(
                    product["unit_price"]
                ),
                2,
            )

            total += line_amount

            order_items.append(
                {
                    "order_item_id": uid(),
                    "order_id": order_id,
                    "product_id": product[
                        "product_id"
                    ],
                    "quantity": quantity,
                    "unit_price": product[
                        "unit_price"
                    ],
                    "line_amount": line_amount,
                    "batch_id": batch_id,
                }
            )

        total = round(
            total,
            2,
        )

        status = random.choices(
            [
                "DELIVERED",
                "CONFIRMED",
                "CANCELLED",
            ],
            weights=[
                80,
                15,
                5,
            ],
        )[0]

        payment_id = uid()

        payment_status = (
            "PAID"
            if status == "DELIVERED"
            else (
                "VOID"
                if status == "CANCELLED"
                else "AUTHORIZED"
            )
        )

        payments.append(
            {
                "payment_id": payment_id,
                "order_id": order_id,
                "payment_method": random.choice(
                    [
                        "CARD",
                        "ACH",
                        "INVOICE",
                    ]
                ),
                "payment_status": payment_status,
                "payment_amount": total,
                "created_at": (
                    order_ts
                    + timedelta(
                        minutes=2
                    )
                ).isoformat(),
                "batch_id": batch_id,
            }
        )

        orders.append(
            {
                "order_id": order_id,
                "order_number": (
                    f"{batch_id[:8]}"
                    f"-{n:08d}"
                    f"-{uuid.uuid4().hex[:4]}"
                ),
                "customer_id": customer[
                    "customer_id"
                ],
                "payment_id": payment_id,
                "order_ts": order_ts.isoformat(),
                "order_status": status,
                "total_amount": total,
                "currency": "USD",
                "batch_id": batch_id,
            }
        )

        events.append(
            {
                "event_id": uid(),
                "event_type": "order.created",
                "event_version": 1,
                "occurred_at": order_ts.isoformat(),
                "producer": (
                    "synthetic-source-generator-bad-data"
                ),
                "aggregate_type": "order",
                "aggregate_id": order_id,
                "tenant_id": customer[
                    "customer_id"
                ],
                "batch_id": batch_id,
                "payload": {
                    "payment_id": payment_id,
                    "total_amount": total,
                    "currency": "USD",
                    "order_status": status,
                },
            }
        )

    # ---------------------------------------------------------
    # Controlled bad-data injection
    #
    # These values intentionally match validation rules already
    # enforced by load_minio_to_postgres.py.
    # ---------------------------------------------------------

    injected_bad_records = {}

    injected_bad_records[
        "customers"
    ] = inject_bad_records(
        customers,
        bad_record_percent,
        lambda row: row.update(
            {
                "segment": "INVALID_SEGMENT"
            }
        ),
    )

    injected_bad_records[
        "products"
    ] = inject_bad_records(
        products,
        bad_record_percent,
        lambda row: row.update(
            {
                "unit_price": -99.99
            }
        ),
    )

    injected_bad_records[
        "orders"
    ] = inject_bad_records(
        orders,
        bad_record_percent,
        lambda row: row.update(
            {
                "order_status": "INVALID_STATUS"
            }
        ),
    )

    injected_bad_records[
        "order_items"
    ] = inject_bad_records(
        order_items,
        bad_record_percent,
        lambda row: row.update(
            {
                "quantity": -1
            }
        ),
    )

    injected_bad_records[
        "payments"
    ] = inject_bad_records(
        payments,
        bad_record_percent,
        lambda row: row.update(
            {
                "payment_amount": -999.99
            }
        ),
    )

    log.warning(
        "BAD-DATA TEST batch=%s percent=%s counts=%s",
        batch_id,
        bad_record_percent,
        injected_bad_records,
    )

    # ---------------------------------------------------------
    # Upload raw source objects to MinIO
    # ---------------------------------------------------------

    client = s3_client()

    datasets = {
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items,
        "payments": payments,
    }

    for entity, rows in datasets.items():
        upload_csv(
            client,
            (
                f"{entity}/"
                f"{partition}/"
                f"{entity}_{batch_id}.csv"
            ),
            rows,
        )

    upload_jsonl(
        client,
        (
            f"events/"
            f"order_created/"
            f"{partition}/"
            f"order_created_{batch_id}.jsonl"
        ),
        events,
    )

    # ---------------------------------------------------------
    # Manifest
    # ---------------------------------------------------------

    manifest = {
        "batch_id": batch_id,
        "batch_type": "BAD_DATA_TEST",
        "created_at": now.isoformat(),
        "row_counts": {
            key: len(value)
            for key, value
            in datasets.items()
        },
        "event_count": len(events),
        "bad_record_percent": (
            bad_record_percent
        ),
        "injected_bad_records": (
            injected_bad_records
        ),
    }

    client.put_object(
        Bucket=RAW_BUCKET,
        Key=(
            f"_manifests/"
            f"{partition}/"
            f"manifest_{batch_id}.json"
        ),
        Body=json.dumps(
            manifest,
            indent=2,
        ).encode(
            "utf-8"
        ),
        ContentType=(
            "application/json"
        ),
    )

    log.warning(
        "bad-data generation completed batch_id=%s",
        batch_id,
    )

    return batch_id


if __name__ == "__main__":
    print(main())