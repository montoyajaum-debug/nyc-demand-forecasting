"""
Construcción de variables para el modelo de demanda zona-hora.

Regla clave (anti-fuga de información): el modelo predice hasta 7 días (168 h) hacia
adelante, así que TODAS las variables de historia usan rezagos >= 168 h. Con un rezago
de 1 h el backtest saldría espectacular y el modelo sería inútil en producción.

La tabla gold ya es una grilla completa (horas sin viajes = 0), por lo que un LAG de
168 filas por zona equivale exactamente a "la misma hora de la semana anterior".
"""
from __future__ import annotations

import duckdb

HORIZON_H = 168  # horizonte de pronóstico: 7 días

# Festivos con efecto conocido en la demanda (oct-2024 a abr-2025).
# Mantener actualizado si se amplía el periodo.
HOLIDAYS = [
    "2024-10-14",  # Columbus / Indigenous Peoples' Day
    "2024-11-11",  # Veterans Day
    "2024-11-28",  # Thanksgiving
    "2024-11-29",  # Día después de Thanksgiving
    "2024-12-24", "2024-12-25", "2024-12-31",
    "2025-01-01",
    "2025-01-20",  # Martin Luther King Jr. Day
    "2025-02-17",  # Presidents' Day
]

FEATURES = [
    "location_id", "area_code", "hour", "dow", "is_weekend", "is_holiday",
    "is_xmas_period", "is_post_cbd",
    "lag_168", "lag_336", "lag_504", "lag_672", "mean_4w_same_hour",
    "zone_mean_prev_week",
]
# Probadas y descartadas (empeoraron el WAPE del backtest de 18,7% a 19,0%):
# median_4w_same_hour, zone_trend, city_mean_prev_week, city_trend.
# Se siguen calculando en ml_features para poder analizarlas.
CATEGORICAL = ["location_id", "area_code"]


def build_features(con: duckdb.DuckDBPyConnection, add_future: bool = True) -> None:
    """Crea la tabla `ml_features`. Si add_future, agrega las 168 h siguientes al último
    dato observado (trips = NULL) para generar el pronóstico."""
    hol = ", ".join(f"DATE '{d}'" for d in HOLIDAYS)
    future = f"""
        union all
        select z.location_id, z.area, h.hour_ts, null as trips
        from (select distinct location_id, area from gold_demand_zone_hour) z
        cross join (
            select unnest(generate_series(
                (select max(hour_ts) from gold_demand_zone_hour) + interval 1 hour,
                (select max(hour_ts) from gold_demand_zone_hour) + interval {HORIZON_H} hour,
                interval 1 hour)) as hour_ts) h
    """ if add_future else ""

    con.execute(f"""
    create or replace table ml_features as
    with base as (
        select location_id, area, hour_ts, trips from gold_demand_zone_hour
        {future}
    ),
    -- Nivel de toda la ciudad (suma de zonas por hora): captura tendencia general y festivos
    city as (
        select hour_ts,
            avg(sum(trips)) over (order by hour_ts rows between 335 preceding and 168 preceding) as city_mean_prev_week,
            avg(sum(trips)) over (order by hour_ts rows between 503 preceding and 336 preceding) as city_mean_2w
        from base group by hour_ts
    ),
    w as (
        select b.*,
            lag(trips, 168) over z as lag_168,
            lag(trips, 336) over z as lag_336,
            lag(trips, 504) over z as lag_504,
            lag(trips, 672) over z as lag_672,
            -- media de la zona en la semana que termina 168 h antes (ventana [t-335, t-168])
            avg(trips) over (partition by location_id order by b.hour_ts
                             rows between 335 preceding and 168 preceding) as zone_mean_prev_week,
            avg(trips) over (partition by location_id order by b.hour_ts
                             rows between 503 preceding and 336 preceding) as zone_mean_2w,
            c.city_mean_prev_week, c.city_mean_2w
        from base b join city c using (hour_ts)
        window z as (partition by location_id order by b.hour_ts)
    )
    select
        location_id,
        dense_rank() over (order by area) - 1                     as area_code,
        area,
        hour_ts,
        hour(hour_ts)                                            as hour,
        isodow(hour_ts)                                          as dow,
        (isodow(hour_ts) >= 6)::int                              as is_weekend,
        (cast(hour_ts as date) in ({hol}))::int                  as is_holiday,
        (cast(hour_ts as date) between date '2024-12-21' and date '2025-01-01')::int as is_xmas_period,
        (hour_ts >= timestamp '2025-01-05')::int                 as is_post_cbd,
        lag_168, lag_336, lag_504, lag_672,
        (lag_168 + lag_336 + lag_504 + lag_672) / 4.0            as mean_4w_same_hour,
        -- mediana de las 4 semanas: robusta a una semana festiva
        list_median([lag_168, lag_336, lag_504, lag_672])        as median_4w_same_hour,
        zone_mean_prev_week,
        zone_mean_prev_week / nullif(zone_mean_2w, 0)            as zone_trend,
        city_mean_prev_week,
        city_mean_prev_week / nullif(city_mean_2w, 0)            as city_trend,
        trips
    from w
    """)
