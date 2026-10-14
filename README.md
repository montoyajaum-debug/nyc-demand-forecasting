# NYC Demand Forecasting — Pipeline Big Data + ML + Claude Dashboards

> Predicción de demanda de viajes por zona y hora en Nueva York (NYC TLC Trip Records)
> y análisis del impacto del cargo por congestión (enero 2025).

**Estado:** 🟢 Fase 1 (ingesta + calidad + silver) · 🟢 Fase 2 (gold + EDA) · 🟡 Fase 3 (modelo predictivo)

## Hallazgos principales (oct-2024 a mar-2025)

| | |
|---|---|
| **Volumen** | ~117.700 viajes/día; mínimo de 52.492 el 25-dic |
| **Patrón horario** | Pico jueves 18 h vs. valle martes 3 h: **48×** |
| **Concentración** | 32 zonas (12%) generan el 80% de la demanda; el perímetro del cargo por congestión, el 58% |
| **Cargo por congestión** | La comparación ingenua muestra +56% de viajes en otros boroughs. **Es un artefacto de la fuente** (registros `payment_type = 0`). Corregido, el CBD (−10%) no cae más que el resto de Manhattan (−11%) |
| **Para el modelo** | 49% de las horas-zona tienen 0 viajes → pérdida para conteos (Poisson/Tweedie) |

![Variación por área](docs/img/04_variacion_por_area.png)

Análisis completo: [`notebooks/01_eda.ipynb`](notebooks/01_eda.ipynb)

## Arquitectura

```
TLC (Parquet mensual) → ingest.py → bronze (crudo) → perfilado de calidad
   → silver (limpio, dbt) → gold (agregados) → LightGBM → predicciones
   → MotherDuck → Claude Dashboards + Power BI
```

## Stack
DuckDB · dbt-duckdb · Pandera · LightGBM · MLflow · MotherDuck · Claude Dashboards · Power BI

## Cómo reproducir

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt

# 1. Ingesta (bronze)
python src/ingest/ingest.py --services yellow --start 2025-01 --end 2025-01

# 2. Perfilado de calidad (no modifica datos)
python src/quality/profile_yellow.py data/bronze/yellow/year=2025/month=01/yellow_tripdata_2025-01.parquet

# 3. Limpieza + capa gold + 29 tests de datos
cd dbt_project
dbt build --profiles-dir .
cd ..

# 4. EDA (requiere: pip install matplotlib jupyter)
jupyter notebook notebooks/01_eda.ipynb
```

## Calidad de datos
Antes de limpiar, cada mes se perfila contra 17 reglas candidatas
(ver `src/quality/profile_yellow.py`). Los reportes quedan en `reports/quality/`.
Las decisiones de limpieza (descartar / corregir / marcar) se documentan con el % de filas afectadas
en [`reports/quality/DECISIONES_LIMPIEZA.md`](reports/quality/DECISIONES_LIMPIEZA.md).

**Oct-2024 a mar-2025:** 22,3 M registros → **21,4 M viajes válidos (94–97% por mes)**, descartes con causa
auditable. Un filtro ingenuo habría eliminado el 37%. 29 tests de datos en dbt en verde, incluida la conciliación
bronze = silver + rechazados. La validación multi-mes detectó un proveedor nuevo (VendorID 7) sin hora de
llegada y un cambio estructural en la fuente desde enero 2025.

## Estructura
```
src/ingest/      ingesta incremental con log de auditoría
src/quality/     perfilado de calidad
dbt_project/     modelos silver (limpieza) y gold (dim_zone, demanda zona-hora, demanda diaria por área)
notebooks/       EDA ejecutado (01_eda.ipynb)
docs/img/        gráficos del EDA
dashboards/      SQL y capturas de Claude Dashboards
reports/quality/ reportes de calidad por mes
data/            (ignorado por git)
```

## Fuente de datos
NYC Taxi & Limousine Commission — TLC Trip Record Data.
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
