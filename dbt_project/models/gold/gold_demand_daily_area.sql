-- Demanda e ingresos diarios por área: base del análisis de impacto del cargo por congestión
-- y de los dashboards.
select
    s.pickup_date                                                   as date,
    d.area,
    count(*)                                                        as trips,
    round(sum(s.fare_amount)    filter (where s.is_valid_fare), 2)  as fare_revenue,
    round(avg(s.fare_amount)    filter (where s.is_valid_fare), 2)  as avg_fare,
    round(avg(s.trip_distance_mi) filter (where s.is_valid_distance), 2) as avg_distance_mi,
    round(avg(s.duration_min)   filter (where s.is_valid_duration), 2)   as avg_duration_min,
    round(sum(coalesce(s.cbd_congestion_fee, 0)), 2)                as cbd_fee_collected,
    count(*) filter (where s.cbd_congestion_fee > 0)                as trips_with_cbd_fee,
    (s.pickup_date >= date '{{ var("cbd_start_date") }}')           as is_post_cbd
from {{ ref('silver_yellow_trips') }} s
left join {{ ref('dim_zone') }} d on d.location_id = s.pu_location_id
group by all
