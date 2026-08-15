select
    customer_id,
    trim(customer_name) as customer_name,
    nullif(trim(city), '') as city,
    nullif(trim(state), '') as state,
    upper(segment) as segment,
    created_at,
    batch_id,
    _loaded_at,
    _source_object
from {{ source('raw', 'customers') }}
