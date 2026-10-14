-- Una sola fila por zona y hora.
select location_id, hour_ts, count(*) as n
from {{ ref('gold_demand_zone_hour') }}
group by 1, 2
having count(*) > 1
