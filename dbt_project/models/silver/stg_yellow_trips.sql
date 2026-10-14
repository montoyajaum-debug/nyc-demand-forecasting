{{ config(materialized='view') }}
-- Lectura de bronze: normaliza nombres a snake_case y calcula métricas derivadas.
-- No filtra nada: toda decisión de limpieza vive en int_yellow_trips_flagged.
select
    vendorid::integer                      as vendor_id,
    tpep_pickup_datetime                   as pickup_at,
    tpep_dropoff_datetime                  as dropoff_at,
    passenger_count::integer               as passenger_count,
    trip_distance::double                  as trip_distance_mi,
    ratecodeid::integer                    as rate_code_id,
    store_and_fwd_flag,
    pulocationid::integer                  as pu_location_id,
    dolocationid::integer                  as do_location_id,
    payment_type::integer                  as payment_type,
    fare_amount, extra, mta_tax, tip_amount, tolls_amount,
    improvement_surcharge, total_amount,
    congestion_surcharge,
    airport_fee,
    cbd_congestion_fee,
    date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime) / 60.0 as duration_min,
    year::integer                          as file_year,
    month::integer                         as file_month,
    filename                               as source_file
from read_parquet('{{ var("bronze_yellow_path") }}',
                  hive_partitioning = true, filename = true, union_by_name = true)
