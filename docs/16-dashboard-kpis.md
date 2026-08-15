# 16 - Dashboard KPIs and validation SQL

Build the first Superset dashboard from `marts.fact_orders` and `marts.fact_order_items`. Validate each KPI in DBeaver before creating the chart.

## Gross Order Value

```sql
select sum(total_amount) as gross_order_value
from marts.fact_orders
where order_status <> 'CANCELLED';
```

## Order count

```sql
select count(*) as order_count
from marts.fact_orders
where order_status <> 'CANCELLED';
```

## Average order value

```sql
select avg(total_amount) as average_order_value
from marts.fact_orders
where order_status <> 'CANCELLED';
```

## Monthly trend

```sql
select date_trunc('month', order_ts) as month,
       sum(total_amount) as gross_order_value,
       count(*) as order_count
from marts.fact_orders
where order_status <> 'CANCELLED'
group by 1
order by 1;
```

## Revenue by customer segment

```sql
select c.segment, sum(f.total_amount) as gross_order_value
from marts.fact_orders f
join marts.dim_customer c using (customer_key)
where f.order_status <> 'CANCELLED'
group by 1
order by 2 desc;
```

## Product revenue

```sql
select p.category, p.product_name, sum(f.line_amount) as product_revenue
from marts.fact_order_items f
join marts.dim_product p using (product_key)
where f.order_status <> 'CANCELLED'
group by 1,2
order by 3 desc
limit 20;
```

## Cancellation rate

```sql
select
  round(100.0 * count(*) filter (where order_status='CANCELLED') / nullif(count(*),0), 2) as cancellation_rate_pct
from marts.fact_orders;
```

A strong portfolio dashboard should include a date filter, customer segment filter, product category filter, KPI cards, one time-series chart, and two or three dimensional breakdowns.
