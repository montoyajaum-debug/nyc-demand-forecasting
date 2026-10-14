-- Resumen de calidad por mes: alimenta el dashboard de calidad de datos.
with c as (
    select file_year, file_month,
           coalesce(reject_reason, 'OK_valido') as resultado,
           count(*) as filas
    from {{ ref('int_yellow_trips_flagged') }}
    group by 1, 2, 3
)
select *, round(100.0 * filas / sum(filas) over (partition by file_year, file_month), 3) as pct
from c
order by file_year, file_month, filas desc
