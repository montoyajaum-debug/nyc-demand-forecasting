-- Error del backtest por semana
-- WAPE del pronóstico a 7 días por semana de prueba y método (total de zonas). Lee backtest_metrics.
-- Conector: MotherDuck · base nyc_demand · herramienta query

SELECT cast(cutoff AS date) AS semana, method AS metodo, round(sum(wape * trips) / sum(trips), 4) AS wape
FROM nyc_demand.main.backtest_metrics WHERE segment = 'total' GROUP BY ALL ORDER BY semana, metodo
