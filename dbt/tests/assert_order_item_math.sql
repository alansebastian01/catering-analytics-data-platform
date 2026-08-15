select *
from {{ ref('fact_order_items') }}
where abs(line_amount - round(quantity * unit_price, 2)) > 0.01
