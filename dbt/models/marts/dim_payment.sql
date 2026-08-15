select
    {{ sk('payment_id') }} as payment_key,
    payment_id,
    order_id,
    payment_method,
    payment_status,
    payment_amount,
    created_at,
    batch_id
from {{ ref('stg_payments') }}
