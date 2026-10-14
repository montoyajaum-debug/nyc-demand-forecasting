-- Descartes de limpieza por mes
-- Porcentaje de registros descartados por mes, separando los reversos con tarifa negativa del resto de reglas. Lee quality_yellow_summary.
-- Conector: MotherDuck · base nyc_demand · herramienta query

SELECT make_date(file_year, file_month, 1) AS mes, sum(filas) AS registros,
  round(sum(pct) FILTER (WHERE resultado <> 'OK_valido') / 100, 4) AS share_descartado,
  round(sum(pct) FILTER (WHERE resultado = 'R07_tarifa_negativa') / 100, 4) AS share_tarifa_negativa,
  round(sum(pct) FILTER (WHERE resultado NOT IN ('OK_valido', 'R07_tarifa_negativa')) / 100, 4) AS share_otras_reglas
FROM nyc_demand.main.quality_yellow_summary GROUP BY ALL ORDER BY mes
