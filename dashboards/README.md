# Dashboard en Claude Dashboards

Dashboard construido con **Claude Dashboards** sobre la base `nyc_demand` en **MotherDuck** (publicada con `src/publish/to_motherduck.py`).
Cada gráfico es una consulta SQL en vivo; el código de cada una está en [`sql/`](sql/) y es el mismo que se ve en el panel *Sources* del dashboard.

| Consulta | Qué alimenta |
|---|---|
| [`backtest_weekly.sql`](sql/backtest_weekly.sql) | Error del backtest por semana |
| [`forecast_hourly.sql`](sql/forecast_hourly.sql) | Pronóstico por hora |
| [`forecast_top.sql`](sql/forecast_top.sql) | Zonas con más demanda prevista |
| [`kpis.sql`](sql/kpis.sql) | Cifras clave del proyecto |
| [`quality_monthly.sql`](sql/quality_monthly.sql) | Descartes de limpieza por mes |
| [`weekly_area.sql`](sql/weekly_area.sql) | Viajes por semana y área |

## Cómo se validó

- Cada consulta se ejecutó en MotherDuck antes de publicarse y sus totales se compararon con los de la base local:
  21.420.346 viajes válidos, 58,1% en el perímetro del cargo, WAPE de producción 18,3% y 261 zonas en el pronóstico.
- El gráfico de *variación por área tras el cargo* se dejó fuera a propósito: sin separar los registros `payment_type = 0`
  repetiría la conclusión falsa (+56% en otros boroughs) que el EDA desmiente.

## Acceso

Las consultas se ejecutan con el acceso a MotherDuck de quien abre el dashboard; la base es privada, por eso el repositorio
muestra capturas en lugar de un enlace público.
