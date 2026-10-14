"""
Entrenamiento y validación del modelo de demanda zona-hora (horizonte 7 días).

1. Backtest con origen móvil: 8 cortes semanales. En cada corte se entrena con TODO
   el pasado y se evalúa en los 7 días siguientes (nunca se mezcla futuro en el train).
2. Se compara LightGBM (Poisson y Tweedie) contra dos baselines:
     - naive estacional: misma hora de la semana anterior (lag_168)
     - media de 4 semanas: promedio de la misma hora en las 4 semanas previas
3. Métricas por segmento: zonas densas (<10% de horas sin viajes) vs. intermitentes.
4. Se entrena el modelo final con todos los datos y se pronostican las 168 h siguientes.

Uso (desde la raíz del proyecto, con `dbt build` ya ejecutado):
    python src/ml/train.py
    python src/ml/train.py --db data/warehouse.duckdb --folds 8
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import sys
import time
from pathlib import Path

import duckdb
import lightgbm as lgb
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import CATEGORICAL, FEATURES, HORIZON_H, build_features  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "model"
IMG_DIR = ROOT / "docs" / "img"
PRED_DIR = ROOT / "data" / "predictions"

PARAMS_BASE = dict(
    learning_rate=0.05, num_leaves=63, min_data_in_leaf=200, feature_fraction=0.9,
    bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0, verbose=-1, seed=42,
    num_threads=os.cpu_count() or 2,
)
N_TREES = 500
OBJECTIVES = {
    "lgbm_poisson": dict(objective="poisson"),
    "lgbm_tweedie": dict(objective="tweedie", tweedie_variance_power=1.2),
}


# ----------------------------------------------------------------------------- utilidades
def fetch(con, sql: str) -> dict[str, np.ndarray]:
    return con.execute(sql).fetchnumpy()


def to_matrix(d: dict[str, np.ndarray]) -> np.ndarray:
    return np.column_stack([np.asarray(d[f], dtype=np.float64) for f in FEATURES])


def wape(y, p) -> float:
    return float(np.abs(y - p).sum() / max(y.sum(), 1e-9))


def metrics(y, p) -> dict[str, float]:
    return dict(wape=wape(y, p), mae=float(np.abs(y - p).mean()),
                bias=float(p.sum() / max(y.sum(), 1e-9) - 1), n=int(len(y)), trips=float(y.sum()))


def train_lgbm(X, y, extra: dict) -> lgb.Booster:
    ds = lgb.Dataset(X, y, feature_name=FEATURES, categorical_feature=CATEGORICAL, free_raw_data=False)
    return lgb.train({**PARAMS_BASE, **extra}, ds, num_boost_round=N_TREES)


# ----------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=os.environ.get("NYC_DUCKDB_PATH", str(ROOT / "data" / "warehouse.duckdb")))
    ap.add_argument("--folds", type=int, default=8)
    ap.add_argument("--no-mlflow", action="store_true")
    args = ap.parse_args()

    con = duckdb.connect(args.db)
    t0 = time.time()
    build_features(con, add_future=True)

    last_obs = con.execute("select max(hour_ts) from ml_features where trips is not null").fetchone()[0]
    first_future = last_obs + dt.timedelta(hours=1)
    cutoffs = [first_future - dt.timedelta(hours=HORIZON_H * k) for k in range(args.folds, 0, -1)]

    # Segmentación de zonas con datos ANTERIORES al primer corte (sin mirar el periodo de test)
    con.execute(f"""
        create or replace temp table zone_segment as
        select location_id,
               case when avg((trips = 0)::int) < 0.10 then 'densa' else 'intermitente' end as segment
        from ml_features where trips is not null and hour_ts < timestamp '{cutoffs[0]}'
        group by 1""")

    # MLflow es opcional: si no está disponible, el script sigue funcionando
    mlf = None
    if not args.no_mlflow:
        try:
            os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")  # tracking local en ./mlruns
            os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")
            import mlflow
            mlflow.set_tracking_uri((ROOT / "mlruns").as_uri())
            mlflow.set_experiment("nyc_demand_zone_hour")
            mlf = mlflow
        except Exception as e:  # noqa: BLE001
            print(f"MLflow no disponible ({e}); se continúa sin tracking.")

    rows_out, bt_preds = [], []
    for i, cut in enumerate(cutoffs, 1):
        end = cut + dt.timedelta(hours=HORIZON_H)
        tr = fetch(con, f"""select f.*, s.segment from ml_features f join zone_segment s using (location_id)
                            where trips is not null and lag_672 is not null and hour_ts < timestamp '{cut}'""")
        te = fetch(con, f"""select f.*, s.segment from ml_features f join zone_segment s using (location_id)
                            where trips is not null and hour_ts >= timestamp '{cut}' and hour_ts < timestamp '{end}'""")
        Xtr, ytr = to_matrix(tr), tr["trips"].astype(float)
        Xte, yte = to_matrix(te), te["trips"].astype(float)

        preds = {
            "naive_estacional": np.nan_to_num(te["lag_168"].astype(float)),
            "media_4_semanas": np.nan_to_num(te["mean_4w_same_hour"].astype(float)),
        }
        for name, extra in OBJECTIVES.items():
            preds[name] = train_lgbm(Xtr, ytr, extra).predict(Xte)

        seg = te["segment"].astype(str)
        for name, p in preds.items():
            for s_name, mask in (("total", np.ones_like(yte, bool)), ("densa", seg == "densa"),
                                 ("intermitente", seg == "intermitente")):
                rows_out.append(dict(fold=i, cutoff=str(cut), method=name, segment=s_name,
                                     **metrics(yte[mask], p[mask])))
        bt_preds.append(dict(location_id=te["location_id"], hour_ts=te["hour_ts"], fold=np.full(len(yte), i),
                             actual=yte, **{f"pred_{k}": v for k, v in preds.items()}))
        tot = {r["method"]: r["wape"] for r in rows_out if r["fold"] == i and r["segment"] == "total"}
        print(f"Fold {i}/{len(cutoffs)} (test desde {cut:%Y-%m-%d}) WAPE: "
              + " | ".join(f"{k} {100*v:.1f}%" for k, v in tot.items()), flush=True)

    # ---------------- agregados del backtest
    def agg(method, segment):
        rs = [r for r in rows_out if r["method"] == method and r["segment"] == segment]
        y_tot = sum(r["trips"] for r in rs)
        abs_err = sum(r["wape"] * r["trips"] for r in rs)
        mae = sum(r["mae"] * r["n"] for r in rs) / sum(r["n"] for r in rs)
        bias = sum((r["bias"] + 1) * r["trips"] for r in rs) / y_tot - 1
        return dict(wape=abs_err / y_tot, mae=mae, bias=bias,
                    wape_std=float(np.std([r["wape"] for r in rs])))

    methods = ["naive_estacional", "media_4_semanas", *OBJECTIVES]
    summary = {(m, s): agg(m, s) for m in methods for s in ("total", "densa", "intermitente")}
    best = min(OBJECTIVES, key=lambda m: summary[(m, "total")]["wape"])          # mejor ML
    best_base = min(("naive_estacional", "media_4_semanas"), key=lambda m: summary[(m, "total")]["wape"])
    gain = 1 - summary[(best, "total")]["wape"] / summary[(best_base, "total")]["wape"]
    # Regla de producción: se publica el método con menor error, sea ML o baseline.
    # Un modelo complejo solo se justifica si mejora al simple de forma material (> 2%).
    production = best if gain > 0.02 else best_base

    print("\nResumen backtest (WAPE total / densas / intermitentes):")
    for m in methods:
        print(f"  {m:<18}" + "  ".join(f"{100*summary[(m, s)]['wape']:6.1f}%" for s in ("total", "densa", "intermitente")))
    print(f"\nMejor ML: {best} | mejora vs. mejor baseline ({best_base}): {100*gain:+.1f}% -> en producción: {production}")

    # ---------------- modelo final + pronóstico
    full = fetch(con, "select * from ml_features where trips is not null and lag_672 is not null")
    fut = fetch(con, "select * from ml_features where trips is null")
    final = train_lgbm(to_matrix(full), full["trips"].astype(float), OBJECTIVES[best])
    yhat_ml = final.predict(to_matrix(fut))
    yhat_base = np.nan_to_num(fut["mean_4w_same_hour" if best_base == "media_4_semanas" else "lag_168"].astype(float))
    yhat = yhat_ml if production == best else yhat_base

    # Importancia: ganancia + SHAP (contribuciones nativas de LightGBM) sobre el pronóstico
    gain_imp = final.feature_importance("gain")
    contrib = final.predict(to_matrix(fut), pred_contrib=True)[:, :-1]
    shap_imp = np.abs(contrib).mean(axis=0)

    # ---------------- persistencia
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    PRED_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORT_DIR / "backtest_metrics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader(); w.writerows(rows_out)

    con.register("pred_df", {"location_id": fut["location_id"], "hour_ts": fut["hour_ts"],
                             "pred_trips": yhat, "pred_ml": yhat_ml, "pred_baseline": yhat_base})
    con.execute(f"""create or replace table pred_demand_zone_hour as
        select p.location_id, d.zone, d.borough, d.area, p.hour_ts, cast(p.hour_ts as date) as date,
               hour(p.hour_ts) as hour,
               round(p.pred_trips, 3)    as pred_trips,      -- pronóstico oficial (método de producción)
               round(p.pred_ml, 3)       as pred_{best},
               round(p.pred_baseline, 3) as pred_{best_base},
               '{production}' as production_method, current_timestamp as created_at
        from pred_df p left join dim_zone d using (location_id)""")
    stamp = f"{first_future:%Y%m%d}"
    con.execute(f"copy pred_demand_zone_hour to '{(PRED_DIR / f'pred_{stamp}.parquet').as_posix()}' (format parquet)")

    bt = {k: np.concatenate([b[k] for b in bt_preds]) for k in bt_preds[0]}
    con.register("bt_df", bt)
    con.execute("""create or replace table backtest_predictions as
        select b.*, d.zone, d.area from bt_df b left join dim_zone d using (location_id)""")

    # ---------------- MLflow
    if mlf:
        for m in methods:
            with mlf.start_run(run_name=m):
                mlf.log_params({"method": m, "folds": len(cutoffs), "horizon_h": HORIZON_H,
                                **({**PARAMS_BASE, **OBJECTIVES[m], "n_trees": N_TREES} if m in OBJECTIVES else {})})
                for s in ("total", "densa", "intermitente"):
                    mlf.log_metrics({f"wape_{s}": summary[(m, s)]["wape"], f"mae_{s}": summary[(m, s)]["mae"],
                                     f"bias_{s}": summary[(m, s)]["bias"]})

    # ---------------- reporte + gráficos
    from report import write_report  # noqa: E402
    write_report(con=con, summary=summary, methods=methods, best=best, best_base=best_base, gain=gain,
                 production=production,
                 rows_out=rows_out, cutoffs=cutoffs, gain_imp=gain_imp, shap_imp=shap_imp,
                 first_future=first_future, report_dir=REPORT_DIR, img_dir=IMG_DIR)

    print(f"\nPronóstico: {len(yhat):,} filas ({first_future:%Y-%m-%d} +7 días) -> tabla pred_demand_zone_hour "
          f"y data/predictions/pred_{stamp}.parquet | {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
