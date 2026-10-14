-- Pronóstico por hora
-- Viajes por hora en toda la ciudad: pronóstico del 1 al 7 de abril de 2025 y la misma hora de la semana anterior. Lee pred_demand_zone_hour y gold_demand_zone_hour.
-- Conector: MotherDuck · base nyc_demand · herramienta query

SELECT p.hour_ts AS hora, round(sum(p.pred_trips), 0) AS pronostico, sum(g.trips) AS real_semana_previa
FROM nyc_demand.main.pred_demand_zone_hour p
LEFT JOIN nyc_demand.main.gold_demand_zone_hour g ON g.location_id = p.location_id AND g.hour_ts = p.hour_ts - INTERVAL 168 HOUR
GROUP BY 1 ORDER BY 1
