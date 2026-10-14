"""
Perfilado de calidad de datos - Yellow Taxi (capa bronze).

NO modifica ni borra datos: solo mide. Con este reporte se deciden las reglas de
limpieza de la capa silver (qué se descarta, qué se corrige, qué solo se marca).

Uso:
    python src/quality/profile_yellow.py data/bronze/yellow/year=2025/month=01/yellow_tripdata_2025-01.parquet

Salidas:
    reports/quality/yellow_<YYYY-MM>_profile.md    (reporte legible, va al repo)
    reports/quality/yellow_<YYYY-MM>_rules.csv     (conteos por regla, para dashboards)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "quality"

# Reglas candidatas: (id, descripción, condición SQL que marca la fila como sospechosa)
# {y}/{m} = año/mes del archivo; {m_start}/{m_end} = límites del mes.
RULES = [
    ("R01", "Pickup fuera del mes del archivo",
     "tpep_pickup_datetime < TIMESTAMP '{m_start}' OR tpep_pickup_datetime >= TIMESTAMP '{m_end}'"),
    ("R02", "Dropoff anterior o igual al pickup",
     "tpep_dropoff_datetime <= tpep_pickup_datetime"),
    ("R03", "Duración > 4 horas",
     "date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime) > 4*3600"),
    ("R04", "Distancia <= 0",
     "trip_distance <= 0"),
    ("R05", "Distancia > 100 millas",
     "trip_distance > 100"),
    ("R06", "Velocidad media > 80 mph (distancia/tiempo imposible)",
     "date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime) > 0 AND "
     "trip_distance / (date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime)/3600.0) > 80"),
    ("R07", "fare_amount negativo (reversos/anulaciones)",
     "fare_amount < 0"),
    ("R08", "total_amount <= 0",
     "total_amount <= 0"),
    ("R09", "fare_amount > 500 USD",
     "fare_amount > 500"),
    ("R10", "passenger_count nulo",
     "passenger_count IS NULL"),
    ("R11", "passenger_count = 0",
     "passenger_count = 0"),
    ("R12", "passenger_count > 6",
     "passenger_count > 6"),
    ("R13", "RatecodeID nulo o fuera de catálogo (1-6)",
     "RatecodeID IS NULL OR RatecodeID NOT IN (1,2,3,4,5,6)"),
    ("R14", "Zona desconocida (264/265) en origen o destino",
     "PULocationID IN (264,265) OR DOLocationID IN (264,265)"),
    ("R15", "payment_type 6 (viaje anulado)",
     "payment_type = 6"),
    ("R16", "total_amount no cuadra con la suma de componentes (tolerancia 0.05)",
     "abs(total_amount - (fare_amount + extra + mta_tax + tip_amount + tolls_amount + "
     "improvement_surcharge + coalesce(congestion_surcharge,0) + coalesce(airport_fee,0) "
     "+ coalesce(cbd_congestion_fee,0))) > 0.05"),
]


def main(path: str) -> None:
    src = Path(path)
    mt = re.search(r"(\d{4})-(\d{2})", src.name)
    if not mt:
        sys.exit("El nombre del archivo debe contener YYYY-MM")
    y, m = int(mt.group(1)), int(mt.group(2))
    m_start = f"{y}-{m:02d}-01"
    m_end = f"{y + (m == 12)}-{(m % 12) + 1:02d}-01"
    tag = f"{y}-{m:02d}"

    con = duckdb.connect()
    con.execute(f"CREATE VIEW t AS SELECT * FROM read_parquet('{src.as_posix()}')")
    cols = {r[0].lower() for r in con.execute("DESCRIBE t").fetchall()}
    # Columnas que no existen en todos los años -> se crean como NULL para que las reglas no fallen
    extra_cols = [c for c in ("airport_fee", "cbd_congestion_fee", "congestion_surcharge") if c not in cols]
    if extra_cols:
        con.execute("CREATE OR REPLACE VIEW t AS SELECT *, "
                    + ", ".join(f"NULL::DOUBLE AS {c}" for c in extra_cols)
                    + f" FROM read_parquet('{src.as_posix()}')")

    n = con.execute("SELECT count(*) FROM t").fetchone()[0]
    dup = con.execute("SELECT count(*) - (SELECT count(*) FROM (SELECT DISTINCT * FROM t)) FROM t").fetchone()[0]
    schema = con.execute("DESCRIBE t").fetchall()
    cur = con.execute("SUMMARIZE t")
    names = [d[0] for d in cur.description]
    summ = [dict(zip(names, row)) for row in cur.fetchall()]  # sin pandas: solo duckdb

    rule_rows = []
    any_flag = []
    for rid, desc, cond in RULES:
        c = cond.format(m_start=m_start, m_end=m_end)
        k = con.execute(f"SELECT count(*) FROM t WHERE coalesce(({c}), false)").fetchone()[0]
        rule_rows.append((rid, desc, k, 100 * k / n if n else 0))
        any_flag.append(f"coalesce(({c}), false)")
    rule_rows.append(("R17", "Filas duplicadas exactas", dup, 100 * dup / n if n else 0))
    flagged = con.execute(f"SELECT count(*) FROM t WHERE {' OR '.join(any_flag)}").fetchone()[0]

    # Contexto adicional para decidir
    by_vendor = con.execute(
        "SELECT VendorID, count(*) AS filas, "
        "round(100*avg((passenger_count IS NULL)::INT),2) AS pct_pax_nulo, "
        "round(100*avg((fare_amount<0)::INT),2) AS pct_fare_neg "
        "FROM t GROUP BY 1 ORDER BY 1").fetchall()
    by_payment = con.execute(
        "SELECT payment_type, count(*) AS filas, round(avg(tip_amount),2) AS propina_media "
        "FROM t GROUP BY 1 ORDER BY 1").fetchall()

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / f"yellow_{tag}_rules.csv", "w", encoding="utf-8") as f:
        f.write("mes,regla,descripcion,filas,pct\n")
        for rid, desc, k, pct in rule_rows:
            f.write(f'{tag},{rid},"{desc}",{k},{pct:.4f}\n')

    L = [f"# Perfil de calidad - Yellow Taxi {tag}\n",
         f"- Archivo: `{src.name}`",
         f"- Filas: **{n:,}**",
         f"- Columnas: {len(schema)}",
         f"- Filas con al menos una regla incumplida: **{flagged:,} ({100*flagged/n:.2f}%)**\n",
         "## Reglas candidatas (solo medición, no se ha borrado nada)\n",
         "| Regla | Descripción | Filas | % |", "|---|---|---:|---:|"]
    L += [f"| {r} | {d} | {k:,} | {p:.3f}% |" for r, d, k, p in rule_rows]
    L += ["\n## Perfil por columna\n",
          "| Columna | Tipo | Mín | Máx | Media | p50 | Nulos % | Distintos aprox. |",
          "|---|---|---|---|---|---|---:|---:|"]
    for r in summ:
        mean = "" if r["avg"] is None else str(r["avg"])[:10]
        L.append(f"| {r['column_name']} | {r['column_type']} | {str(r['min'])[:19]} | {str(r['max'])[:19]} "
                 f"| {mean} | {r['q50']} | {r['null_percentage']} | {r['approx_unique']:,} |")
    L += ["\n## Por proveedor (VendorID)\n", "| VendorID | Filas | % pax nulo | % fare negativo |",
          "|---|---:|---:|---:|"]
    L += [f"| {v} | {f:,} | {a} | {b} |" for v, f, a, b in by_vendor]
    L += ["\n## Por tipo de pago\n",
          "Recordatorio: la propina solo se registra en pagos con tarjeta (payment_type=1).\n",
          "| payment_type | Filas | Propina media |", "|---|---:|---:|"]
    L += [f"| {p} | {f:,} | {t} |" for p, f, t in by_payment]
    (OUT / f"yellow_{tag}_profile.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:8 + len(rule_rows)]))
    print(f"\nReporte: reports/quality/yellow_{tag}_profile.md")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
