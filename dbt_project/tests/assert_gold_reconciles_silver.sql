-- Los totales de gold cuadran con silver (sin pérdidas ni duplicados en la grilla).
with s as (select count(*) as n from {{ ref('silver_yellow_trips') }} where is_known_zone),
     g as (select sum(trips) as n from {{ ref('gold_demand_zone_hour') }}),
     a as (select sum(trips) as n from {{ ref('gold_demand_daily_area') }}),
     s_all as (select count(*) as n from {{ ref('silver_yellow_trips') }})
select s.n as silver_known, g.n as gold_zone_hour, a.n as gold_daily, s_all.n as silver_all
from s, g, a, s_all
where s.n <> g.n or a.n <> s_all.n
