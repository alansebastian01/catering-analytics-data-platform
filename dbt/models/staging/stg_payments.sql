select
    payment_id,
    order_id,
    upper(payment_method) as payment_method,
    upper(payment_status) as payment_status,
    payment_amount::numeric(14,2) as payment_amount,
    created_at,
    batch_id,
    _loaded_at,
    _source_object
from {{ source('raw', 'payments') }}
