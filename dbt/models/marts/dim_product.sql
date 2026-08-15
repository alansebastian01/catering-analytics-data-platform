select
    {{ sk('product_id') }} as product_key,
    product_id,
    product_name,
    category,
    brand,
    unit_price,
    updated_at,
    batch_id
from {{ ref('stg_products') }}
