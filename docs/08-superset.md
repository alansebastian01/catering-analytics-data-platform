# 08 - Apache Superset setup

Open `http://localhost:8088` and sign in with the admin credentials from `.env`.

## Add PostgreSQL connection

From inside Docker, the PostgreSQL host is the Compose service name `postgres`, not `localhost`.

Use a SQLAlchemy URI in this form:

```text
postgresql+psycopg2://bi_reader:<BI_READER_PASSWORD>@postgres:5432/analytics
```

Use the read-only BI role. Do not connect Superset with the PostgreSQL administrator.

## Recommended datasets

Start with:

- `analytics_marts.fact_orders`
- `analytics_marts.fact_order_items`
- `analytics_marts.dim_customer`
- `analytics_marts.dim_product`

## First dashboard

Create these visualizations:

- Gross Order Value by month.
- Order count by status.
- Average order value.
- Revenue by customer segment.
- Revenue by product category.
- Top 10 products by revenue.
- Payment status distribution.

## Portfolio-quality dashboard notes

Use meaningful business labels, document filter semantics, include “last refreshed” information, avoid overloading one dashboard, and validate every KPI with a SQL query in DBeaver before presenting it.
