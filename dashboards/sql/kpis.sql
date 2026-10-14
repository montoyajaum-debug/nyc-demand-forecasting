-- Cifras clave del proyecto
-- Totales del periodo oct-2024 a mar-2025: viajes válidos, registros brutos, % descartado, % en el CBD, cargo cobrado y error del pronóstico. Lee quality_yellow_summary, gold_demand_daily_area y backtest_metrics.
-- Conector: MotherDuck · base nyc_demand · herramienta query

WITH q AS (SELECT sum(filas) AS registros_brutos, sum(filas) FILTER (WHERE resultado <> 'OK_valido') AS descartados FROM nyc_demand.main.quality_yellow_summary),
d AS (SELECT sum(trips) AS viajes_validos, sum(trips) FILTER (WHERE area = 'CBD (cargo)') AS viajes_cbd, sum(cbd_fee_collected) AS cargo_cbd_usd FROM nyc_demand.main.gold_demand_daily_area),
m AS (SELECT method, sum(wape * trips) / sum(trips) AS wape FROM nyc_demand.main.backtest_metrics WHERE segment = 'total' GROUP BY method)
SELECT d.viajes_validos, q.registros_brutos, round(q.descartados / q.registros_brutos, 4) AS share_descartado,
       round(d.viajes_cbd / d.viajes_validos, 4) AS share_cbd, round(d.cargo_cbd_usd, 0) AS cargo_cbd_usd,
       round((SELECT wape FROM m WHERE method = 'media_4_semanas'), 4) AS wape_produccion,
       round((SELECT min(wape) FROM m WHERE method LIKE 'lgbm%'), 4) AS wape_mejor_ml
FROM d, q
