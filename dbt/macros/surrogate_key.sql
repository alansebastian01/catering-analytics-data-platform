{% macro sk(value) -%}
md5(cast({{ value }} as text))
{%- endmacro %}
