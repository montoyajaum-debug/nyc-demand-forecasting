-- Capa silver: un registro = un viaje real. Los campos dudosos se conservan con banderas
-- para que cada análisis filtre según lo que necesita (demanda vs. tarifas).
with t as (
    select * from {{ ref('int_yellow_trips_flagged') }}
    where reject_reason is null
),
z as (select * from {{ ref('taxi_zone_lookup') }})

select
    t.vendor_id,
    t.pickup_at,
    t.dropoff_at,
    cast(t.pickup_at as date)                   as pickup_date,
    hour(t.pickup_at)                           as pickup_hour,
    isodow(t.pickup_at)                         as pickup_dow,       -- 1 = lunes
    case when t.duration_min > 0 then round(t.duration_min, 2) end as duration_min,  -- NULL = hora de llegada no registrada

    t.pu_location_id,
    pu.Borough                                  as pu_borough,
    pu.Zone                                     as pu_zone,
    t.do_location_id,
    dz.Borough                                  as do_borough,
    dz.Zone                                     as do_zone,

    -- Pasajeros: 0 o nulo = desconocido (no se imputa para no sesgar)
    case when t.passenger_count between 1 and 9 then t.passenger_count end as passenger_count,

    t.trip_distance_mi,
    t.rate_code_id,
    case t.rate_code_id
        when 1 then 'Tarifa estándar'
        when 2 then 'JFK'
        when 3 then 'Newark'
        when 4 then 'Nassau/Westchester'
        when 5 then 'Tarifa negociada'
        when 6 then 'Viaje compartido'
        else 'Desconocido'
    end                                         as rate_code,
    t.payment_type,
    case t.payment_type
        when 1 then 'Tarjeta'
        when 2 then 'Efectivo'
        when 3 then 'Sin cargo'
        when 4 then 'Disputa'
        when 5 then 'Desconocido'
        else 'Sin registro (0)'
    end                                         as payment_method,

    t.fare_amount, t.extra, t.mta_tax, t.tip_amount, t.tolls_amount,
    t.improvement_surcharge, t.congestion_surcharge, t.airport_fee,
    t.cbd_congestion_fee, t.total_amount,

    -- Banderas de calidad
    (t.duration_min > 0)                                                             as is_valid_duration,
    (t.fare_amount > 0 and t.fare_amount <= {{ var('max_fare_usd') }})              as is_valid_fare,
    (t.trip_distance_mi > 0 and t.trip_distance_mi <= {{ var('max_distance_mi') }}) as is_valid_distance,
    (t.passenger_count is null or t.passenger_count = 0)                             as is_pax_unknown,
    (t.pu_location_id not in (264, 265) and t.do_location_id not in (264, 265))     as is_known_zone,
    (t.payment_type = 0)                                                             as is_payment_type_0,
    (t.payment_type = 1)                                                             as is_tip_recorded,
    t.was_reversed,

    t.file_year,
    t.file_month
from t
left join z pu on pu.LocationID = t.pu_location_id
left join z dz on dz.LocationID = t.do_location_id
