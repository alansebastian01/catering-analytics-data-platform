select
    {{ sk('customer_id') }} as customer_key,
    customer_id,
    customer_name,
    city,
    state,
    segment,
    created_at,
    batch_id
from {{ ref('stg_customers') }}
