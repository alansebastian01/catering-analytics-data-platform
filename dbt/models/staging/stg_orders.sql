select
    order_id,
    order_number,
    customer_id,
    payment_id,
    order_ts,
    upper(order_status) as order_status,
    total_amount::numeric(14,2) as total_amount,
    upper(currency) as currency,
    batch_id,
    _loaded_at,
    _source_object
from {{ source('raw', 'orders') }}
