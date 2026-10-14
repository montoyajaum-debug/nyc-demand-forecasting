-- Aplica las reglas de limpieza aprobadas (ver reports/quality/DECISIONES_LIMPIEZA.md).
-- reject_reason NULL = viaje válido. El orden del CASE define la prioridad de la causa.
with base as (
    select * from {{ ref('stg_yellow_trips') }}
),

-- Cobros positivos que tienen un reverso exacto (mismo viaje, tarifa con signo opuesto)
reversed as (
    select distinct p.vendor_id, p.pickup_at, p.dropoff_at, p.pu_location_id, p.fare_amount
    from base p
    join base n
      on  n.vendor_id      = p.vendor_id
      and n.pickup_at      = p.pickup_at
      and n.dropoff_at     = p.dropoff_at
      and n.pu_location_id = p.pu_location_id
      and n.fare_amount    = -p.fare_amount
    where p.fare_amount > 0
)

select
    b.*,
    case
        when b.pickup_at <  make_timestamp(b.file_year, b.file_month, 1, 0, 0, 0)
          or b.pickup_at >= make_timestamp(b.file_year, b.file_month, 1, 0, 0, 0) + interval 1 month
                                                                     then 'R01_fuera_de_mes'
        when b.fare_amount < 0                                       then 'R07_tarifa_negativa'
        when b.dropoff_at < b.pickup_at                              then 'R02_tiempo_invalido'
        -- dropoff = pickup: se conserva si hay recorrido y cobro (falta la hora de llegada;
        -- patrón de VendorID 7 desde 2025). Si no, no es un viaje.
        when b.dropoff_at = b.pickup_at
         and not (b.trip_distance_mi > 0 and b.fare_amount > 0)      then 'R02_tiempo_invalido'
        when b.duration_min > {{ var('max_duration_min') }}          then 'R03_duracion_excesiva'
        when b.duration_min > 0
         and b.trip_distance_mi / (b.duration_min / 60.0) > {{ var('max_speed_mph') }}
                                                                     then 'R06_velocidad_imposible'
        when b.trip_distance_mi <= 0
         and b.duration_min < {{ var('min_duration_ghost_min') }}    then 'R04_viaje_fantasma'
    end as reject_reason,
    (r.vendor_id is not null) as was_reversed
from base b
left join reversed r
  on  r.vendor_id      = b.vendor_id
  and r.pickup_at      = b.pickup_at
  and r.dropoff_at     = b.dropoff_at
  and r.pu_location_id = b.pu_location_id
  and r.fare_amount    = b.fare_amount
