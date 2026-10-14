-- Ninguna fila se pierde: bronze = silver + rechazadas (por mes).
with b as (select file_year, file_month, count(*) n from {{ ref('stg_yellow_trips') }} group by all),
     s as (select file_year, file_month, count(*) n from {{ ref('silver_yellow_trips') }} group by all),
     r as (select file_year, file_month, count(*) n from {{ ref('silver_yellow_rejected') }} group by all)
select b.*, s.n as silver, r.n as rejected
from b
left join s using (file_year, file_month)
left join r using (file_year, file_month)
where b.n <> coalesce(s.n, 0) + coalesce(r.n, 0)
