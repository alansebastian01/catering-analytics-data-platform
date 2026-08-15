with bounds as (
    select min(order_ts::date) as min_date, max(order_ts::date) as max_date
    from {{ ref('stg_orders') }}
), dates as (
    select generate_series(min_date, max_date, interval '1 day')::date as full_date
    from bounds
    where min_date is not null
)
select
    to_char(full_date, 'YYYYMMDD')::integer as date_key,
    full_date,
    extract(day from full_date)::integer as day,
    extract(month from full_date)::integer as month,
    extract(quarter from full_date)::integer as quarter,
    extract(year from full_date)::integer as year,
    extract(isodow from full_date)::integer as iso_day_of_week,
    to_char(full_date, 'Dy') as day_name,
    to_char(full_date, 'Mon') as month_name
from dates
