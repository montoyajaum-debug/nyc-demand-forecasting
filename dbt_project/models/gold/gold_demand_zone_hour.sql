-- Demanda por zona de recogida y hora. Grilla COMPLETA zona x hora:
-- las horas sin viajes aparecen con trips = 0 (indispensable para el modelo predictivo;
-- sin esto el modelo nunca vería la demanda cero y sobreestimaría).
with t as (
    select * from {{ ref('silver_yellow_trips') }} where is_known_zone
),
agg as (
    select
        pu_location_id                                              as location_id,
        date_trunc('hour', pickup_at)                               as hour_ts,
        count(*)                                                    as trips,
        avg(fare_amount)        filter (where is_valid_fare)        as avg_fare,
        avg(trip_distance_mi)   filter (where is_valid_distance)    as avg_distance_mi,
        avg(duration_min)       filter (where is_valid_duration)    as avg_duration_min
    from t
    group by 1, 2
),
hours as (
    select unnest(generate_series(
        (select date_trunc('hour', min(pickup_at)) from t),
        (select date_trunc('hour', max(pickup_at)) from t),
        interval 1 hour)) as hour_ts
),
zones as (select distinct location_id from agg)
select
    z.location_id,
    d.area,
    d.borough,
    h.hour_ts,
    cast(h.hour_ts as date)                         as date,
    hour(h.hour_ts)                                 as hour,
    isodow(h.hour_ts)                               as dow,
    coalesce(a.trips, 0)                            as trips,
    round(a.avg_fare, 2)                            as avg_fare,
    round(a.avg_distance_mi, 2)                     as avg_distance_mi,
    round(a.avg_duration_min, 2)                    as avg_duration_min,
    (h.hour_ts >= timestamp '{{ var("cbd_start_date") }}') as is_post_cbd
from zones z
cross join hours h
left join agg a on a.location_id = z.location_id and a.hour_ts = h.hour_ts
left join {{ ref('dim_zone') }} d on d.location_id = z.location_id
