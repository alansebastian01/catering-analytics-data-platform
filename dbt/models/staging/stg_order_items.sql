select
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price::numeric(12,2) as unit_price,
    line_amount::numeric(14,2) as line_amount,
    batch_id,
    _loaded_at,
    _source_object
from {{ source('raw', 'order_items') }}
