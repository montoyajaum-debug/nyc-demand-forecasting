-- Alerta si un mes descarta más del 10%: señal de cambio en la fuente o de regla mal calibrada.
select file_year, file_month, sum(pct) as pct_rechazo
from {{ ref('quality_yellow_summary') }}
where resultado <> 'OK_valido'
group by file_year, file_month
having sum(pct) > 10
