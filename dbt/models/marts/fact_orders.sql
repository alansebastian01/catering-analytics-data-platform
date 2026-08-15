select
    o.order_id,
    o.order_number,
    to_char(o.order_ts::date, 'YYYYMMDD')::integer as date_key,
    {{ sk('o.customer_id') }} as customer_key,
    {{ sk('o.payment_id') }} as payment_key,
    o.order_status,
    o.currency,
    o.total_amount,
    count(i.order_item_id) as line_count,
    sum(i.quantity) as item_quantity,
    o.order_ts,
    o.batch_id
from {{ ref('stg_orders') }} o
join {{ ref('stg_order_items') }} i on i.order_id = o.order_id
group by 1,2,3,4,5,6,7,8,11,12
