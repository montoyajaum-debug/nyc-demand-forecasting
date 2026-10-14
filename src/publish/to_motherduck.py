"""
Publica en MotherDuck las tablas que consumen los dashboards (Claude Dashboards / Power BI).

Principio de coste: el procesamiento pesado (22 M de registros) se queda en local con DuckDB.
A la nube solo suben tablas agregadas o pequeñas (~15 MB en total), muy por debajo de los
10 GB del plan gratuito de MotherDuck.

Requisitos:
  1. Haber ejecutado `dbt build` y `python src/ml/train.py`.
  2. Token de MotherDuck en la variable de entorno `motherduck_token` (NUNCA en el código):
       PowerShell (solo para la sesión actual):  $env:motherduck_token = "<tu token>"

Uso:
    python src/publish/to_motherduck.py --dry-run     # muestra qué subiría, sin conectarse
    python src/publish/to_motherduck.py
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
MD_DATABASE = "nyc_demand"

# Tabla local -> descripción (se guarda como COMMENT en MotherDuck para que Claude Dashboards
# entienda el significado de cada tabla al escribir SQL)
TABLES = {
    "dim_zone": "Zonas TLC con área de análisis (CBD derivado de los datos, Frontera CBD, Manhattan resto, Aeropuertos, Otros boroughs).",
    "gold_demand_daily_area": "Viajes, ingresos y cargo por congestión por día y área. is_post_cbd = desde 2025-01-05.",
    "gold_demand_zone_hour": "Viajes por zona de recogida y hora (grilla completa, horas sin viajes = 0). Oct-2024 a mar-2025.",
    "quality_yellow_summary": "Resultado de la limpieza por mes: filas válidas y descartadas por regla (R01-R07).",
    "backtest_predictions": "Backtest de 8 semanas: real vs. pronóstico por zona-hora para cada método (naive, media 4 semanas, LightGBM).",
    "pred_demand_zone_hour": "Pronóstico a 7 días por zona-hora. pred_trips = método en producción.",
}
CSV_TABLES = {
    "backtest_metrics": (ROOT / "reports" / "model" / "backtest_metrics.csv",
                         "Métricas del backtest por semana, método y segmento (WAPE, MAE, sesgo)."),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=os.environ.get("NYC_DUCKDB_PATH", str(ROOT / "data" / "warehouse.duckdb")))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    local = duckdb.connect(args.db, read_only=True)
    src = local.execute("select current_database()").fetchone()[0]  # nombre del catálogo local
    existing = {r[0] for r in local.execute("select table_name from duckdb_tables()").fetchall()}
    missing = [t for t in TABLES if t not in existing]
    if missing:
        sys.exit(f"Faltan tablas locales: {missing}. Ejecuta `dbt build` y `python src/ml/train.py` primero.")
    for name, (path, _) in CSV_TABLES.items():
        if not path.exists():
            sys.exit(f"No existe {path}. Ejecuta `python src/ml/train.py` primero.")

    print("Tablas a publicar:")
    for t in TABLES:
        n = local.execute(f"select count(*) from {t}").fetchone()[0]
        print(f"  {t:<26}{n:>12,} filas")
    if args.dry_run:
        print("\n--dry-run: no se ha conectado a MotherDuck.")
        return 0

    if not (os.environ.get("motherduck_token") or os.environ.get("MOTHERDUCK_TOKEN")):
        sys.exit("Falta la variable de entorno motherduck_token. En PowerShell: $env:motherduck_token = \"<tu token>\"")
    os.environ.setdefault("motherduck_token", os.environ.get("MOTHERDUCK_TOKEN", ""))

    local.execute("ATTACH 'md:'")  # usa el token del entorno; el token nunca se imprime
    local.execute(f"CREATE DATABASE IF NOT EXISTS {MD_DATABASE}")

    print(f"\nPublicando en MotherDuck → {MD_DATABASE}:")
    for t, comment in TABLES.items():
        local.execute(f"CREATE OR REPLACE TABLE {MD_DATABASE}.main.{t} AS SELECT * FROM {src}.main.{t}")
        local.execute(f"COMMENT ON TABLE {MD_DATABASE}.main.{t} IS '{comment}'")
        n_local = local.execute(f"select count(*) from {src}.main.{t}").fetchone()[0]
        n_md = local.execute(f"select count(*) from {MD_DATABASE}.main.{t}").fetchone()[0]
        status = "OK" if n_local == n_md else "¡DIFERENCIA!"
        print(f"  {t:<26}{n_md:>12,} filas  {status}")
        if n_local != n_md:
            return 1
    for t, (path, comment) in CSV_TABLES.items():
        local.execute(f"CREATE OR REPLACE TABLE {MD_DATABASE}.main.{t} AS SELECT * FROM read_csv_auto('{path.as_posix()}')")
        local.execute(f"COMMENT ON TABLE {MD_DATABASE}.main.{t} IS '{comment}'")
        print(f"  {t:<26}{local.execute(f'select count(*) from {MD_DATABASE}.main.{t}').fetchone()[0]:>12,} filas  OK")

    print(f"\nListo. En Claude, con el conector de MotherDuck, pide un dashboard sobre la base `{MD_DATABASE}`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
