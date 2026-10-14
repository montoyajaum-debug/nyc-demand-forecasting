-- Dimensión de zonas con área de análisis.
-- El perímetro del cargo por congestión (CBD) se DERIVA de los datos: proporción de viajes
-- intra-zona (origen = destino) que pagan cbd_congestion_fee después de su entrada en vigor.
-- Así no dependemos de una lista manual y el criterio es reproducible.
with intra as (
    select
        pu_location_id                                   as location_id,
        count(*)                                         as n_intra,
        avg((cbd_congestion_fee > 0)::int)               as share_cbd_fee
    from {{ ref('silver_yellow_trips') }}
    where pickup_date > date '{{ var("cbd_start_date") }}'   -- desde el día siguiente al inicio
      and pu_location_id = do_location_id
      and is_known_zone
    group by 1
)
select
    z.LocationID                                         as location_id,
    z.Borough                                            as borough,
    z.Zone                                               as zone,
    z.service_zone,
    round(i.share_cbd_fee, 3)                            as share_cbd_fee,
    coalesce(i.n_intra, 0)                               as n_intra_trips,
    case
        when z.LocationID in (1, 132, 138)                                   then 'Aeropuertos'
        when i.n_intra >= {{ var('cbd_min_trips') }}
         and i.share_cbd_fee >= {{ var('cbd_share_inside') }}                then 'CBD (cargo)'
        when i.n_intra >= {{ var('cbd_min_trips') }}
         and i.share_cbd_fee >= {{ var('cbd_share_border') }}                then 'Frontera CBD'
        when z.Borough = 'Manhattan'                                          then 'Manhattan resto'
        when z.LocationID in (264, 265)                                      then 'Desconocida'
        else 'Otros boroughs'
    end                                                  as area
from {{ ref('taxi_zone_lookup') }} z
left join intra i on i.location_id = z.LocationID
