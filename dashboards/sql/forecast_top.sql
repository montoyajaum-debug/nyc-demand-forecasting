-- Zonas con más demanda prevista
-- Las 15 zonas con más viajes previstos del 1 al 7 de abril de 2025 frente a los 7 días anteriores. Lee pred_demand_zone_hour y gold_demand_zone_hour.
-- Conector: MotherDuck · base nyc_demand · herramienta query

WITH f AS (SELECT location_id, zone, area, sum(pred_trips) AS pronostico FROM nyc_demand.main.pred_demand_zone_hour GROUP BY ALL),
r AS (SELECT location_id, sum(trips) AS real FROM nyc_demand.main.gold_demand_zone_hour
      WHERE hour_ts > (SELECT max(hour_ts) FROM nyc_demand.main.gold_demand_zone_hour) - INTERVAL 168 HOUR GROUP BY 1)
SELECT f.zone AS zona, f.area, round(f.pronostico, 0) AS pronostico_7d, r.real AS real_semana_previa,
       round(f.pronostico / r.real - 1, 4) AS variacion
FROM f JOIN r USING (location_id) ORDER BY pronostico_7d DESC LIMIT 15
