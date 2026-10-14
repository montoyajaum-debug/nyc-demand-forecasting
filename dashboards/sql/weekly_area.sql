-- Viajes por semana y área
-- Viajes por semana completa (lunes a domingo) y área de recogida. Lee gold_demand_daily_area.
-- Conector: MotherDuck · base nyc_demand · herramienta query

SELECT date_trunc('week', date)::date AS semana, area, sum(trips) AS viajes
FROM nyc_demand.main.gold_demand_daily_area
WHERE area <> 'Desconocida'
GROUP BY ALL
HAVING count(DISTINCT date) = 7
ORDER BY semana, area
