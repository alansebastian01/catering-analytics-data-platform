select *
from {{ ref('fact_order_items') }}
where line_amount < 0 or order_total_amount < 0 or quantity <= 0
