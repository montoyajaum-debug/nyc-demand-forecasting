"""
Ingesta incremental de NYC TLC Trip Records (capa bronze).

- Descarga solo los meses que faltan (idempotente).
- Escribe a archivo temporal y renombra al final: un corte de red no deja archivos corruptos.
- Registra cada ejecución en data/bronze/_ingest_log.csv (auditoría).
- Solo usa la librería estándar de Python: no requiere instalar nada.

Uso (desde la raíz del proyecto):
    python src/ingest/ingest.py --services yellow --start 2025-01 --end 2025-01
    python src/ingest/ingest.py --services yellow fhvhv --start 2024-01 --end 2025-12
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
ZONES_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
VALID_SERVICES = {"yellow", "green", "fhv", "fhvhv"}

ROOT = Path(__file__).resolve().parents[2]
BRONZE = ROOT / "data" / "bronze"
REFERENCE = ROOT / "data" / "reference"
LOG_FILE = BRONZE / "_ingest_log.csv"


def month_range(start: str, end: str) -> list[tuple[int, int]]:
    y, m = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))
    out = []
    while (y, m) <= (ey, em):
        out.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def download(url: str, dest: Path, retries: int = 3) -> int:
    """Descarga con reintentos. Devuelve bytes escritos."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "nyc-demand-forecasting/1.0"})
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp, open(tmp, "wb") as f:
                size = 0
                while chunk := resp.read(1 << 20):
                    f.write(chunk)
                    size += len(chunk)
            tmp.replace(dest)
            return size
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):  # mes aún no publicado
                tmp.unlink(missing_ok=True)
                raise
            err = e
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            err = e
        tmp.unlink(missing_ok=True)
        wait = 5 * attempt
        print(f"   intento {attempt} falló ({err}); reintento en {wait}s")
        time.sleep(wait)
    raise RuntimeError(f"No se pudo descargar {url}")


def log(row: dict) -> None:
    new = not LOG_FILE.exists()
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["run_ts", "service", "year", "month", "status", "bytes", "file"])
        if new:
            w.writeheader()
        w.writerow(row)


def main() -> int:
    p = argparse.ArgumentParser(description="Ingesta incremental NYC TLC -> data/bronze")
    p.add_argument("--services", nargs="+", default=["yellow"], choices=sorted(VALID_SERVICES))
    p.add_argument("--start", required=True, help="YYYY-MM")
    p.add_argument("--end", required=True, help="YYYY-MM")
    p.add_argument("--force", action="store_true", help="Re-descargar aunque exista")
    args = p.parse_args()

    run_ts = dt.datetime.now().isoformat(timespec="seconds")

    zones = REFERENCE / "taxi_zone_lookup.csv"
    if not zones.exists():
        print("-> taxi_zone_lookup.csv")
        download(ZONES_URL, zones)

    errors = 0
    for service in args.services:
        for y, m in month_range(args.start, args.end):
            fname = f"{service}_tripdata_{y}-{m:02d}.parquet"
            dest = BRONZE / service / f"year={y}" / f"month={m:02d}" / fname
            if dest.exists() and dest.stat().st_size > 0 and not args.force:
                print(f"   ya existe, se omite: {fname}")
                log(dict(run_ts=run_ts, service=service, year=y, month=m, status="skipped",
                         bytes=dest.stat().st_size, file=str(dest.relative_to(ROOT))))
                continue
            print(f"-> {fname}")
            try:
                size = download(f"{BASE_URL}/{fname}", dest)
                status = "downloaded"
                print(f"   OK {size / 1e6:,.1f} MB")
            except urllib.error.HTTPError as e:
                size, status = 0, f"not_available_{e.code}"
                print(f"   no publicado aún ({e.code})")
            except Exception as e:  # noqa: BLE001
                size, status = 0, f"error: {e}"
                errors += 1
                print(f"   ERROR {e}")
            log(dict(run_ts=run_ts, service=service, year=y, month=m, status=status,
                     bytes=size, file=str(dest.relative_to(ROOT))))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
