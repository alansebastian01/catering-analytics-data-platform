from __future__ import annotations

import json
import os
import psycopg


def main() -> None:
    dsn = os.environ["INGEST_DSN"]
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        checks = {
            "orders_vs_order_items_orphans": """
                SELECT count(*) FROM raw.order_items i
                LEFT JOIN raw.orders o ON o.order_id=i.order_id
                WHERE o.order_id IS NULL
            """,
            "payments_vs_orders_orphans": """
                SELECT count(*) FROM raw.payments p
                LEFT JOIN raw.orders o ON o.order_id=p.order_id
                WHERE o.order_id IS NULL
            """,
            "negative_order_totals": "SELECT count(*) FROM raw.orders WHERE total_amount < 0",
            "order_item_amount_mismatch": "SELECT count(*) FROM raw.order_items WHERE line_amount <> round(quantity * unit_price, 2)",
        }
        result = {}
        failed = False
        for name, query in checks.items():
            cur.execute(query)
            count = cur.fetchone()[0]
            result[name] = count
            failed = failed or count != 0
        print(json.dumps(result, indent=2))
        if failed:
            raise SystemExit("Reconciliation failed: one or more checks are non-zero")


if __name__ == "__main__":
    main()
