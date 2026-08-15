select
    product_id,
    trim(product_name) as product_name,
    upper(category) as category,
    nullif(trim(brand), '') as brand,
    unit_price::numeric(12,2) as unit_price,
    updated_at,
    batch_id,
    _loaded_at,
    _source_object
from {{ source('raw', 'products') }}
