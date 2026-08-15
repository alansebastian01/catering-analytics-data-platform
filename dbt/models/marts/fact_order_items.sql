select
    i.order_item_id,
    o.order_id,
    to_char(o.order_ts::date, 'YYYYMMDD')::integer as date_key,
    {{ sk('o.customer_id') }} as customer_key,
    {{ sk('i.product_id') }} as product_key,
    {{ sk('o.payment_id') }} as payment_key,
    o.order_number,
    o.order_status,
    o.currency,
    i.quantity,
    i.unit_price,
    i.line_amount,
    o.total_amount as order_total_amount,
    o.order_ts,
    o.batch_id
from {{ ref('stg_order_items') }} i
join {{ ref('stg_orders') }} o on i.order_id = o.order_id
