"""Reporte del modelo: reports/model/MODELO.md + gráficos en docs/img/."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from features import FEATURES  # noqa: E402

BLUE, ORANGE, INK, INK2, GRID, SURF, MUTED = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb", "#b7b6b0"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
})

LABELS = {
    "naive_estacional": "Naive estacional (semana anterior)",
    "media_4_semanas": "Media 4 semanas (misma hora)",
    "lgbm_poisson": "LightGBM Poisson",
    "lgbm_tweedie": "LightGBM Tweedie",
}
FEATURE_LABELS = {
    "location_id": "Zona", "area_code": "Área", "hour": "Hora", "dow": "Día de la semana",
    "is_weekend": "Fin de semana", "is_holiday": "Festivo", "is_xmas_period": "Periodo navideño",
    "is_post_cbd": "Tras cargo por congestión", "lag_168": "Misma hora, 1 semana antes",
    "lag_336": "Misma hora, 2 semanas antes", "lag_504": "Misma hora, 3 semanas antes",
    "lag_672": "Misma hora, 4 semanas antes", "mean_4w_same_hour": "Media misma hora 4 semanas",
    "zone_mean_prev_week": "Media de la zona, semana previa",
}


def _save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def poisson_noise_floor(con) -> float:
    """WAPE mínimo esperable si la demanda fuera Poisson con media = media de 4 semanas.
    MAD exacto de Poisson(λ): 2·e^-λ·λ^(k+1)/k!, con k = floor(λ)."""
    import math
    lam = con.execute("select pred_media_4_semanas from backtest_predictions").fetchnumpy()["pred_media_4_semanas"]
    lam = np.asarray(lam, float)
    mad = sum(2 * math.exp(-l + (math.floor(l) + 1) * math.log(l) - math.lgamma(math.floor(l) + 1))
              for l in lam if l > 0)
    return mad / lam.sum()


def write_report(*, con, summary, methods, best, best_base, gain, production, rows_out, cutoffs, gain_imp,
                 shap_imp, first_future, report_dir, img_dir):
    img_dir.mkdir(parents=True, exist_ok=True)
    floor = poisson_noise_floor(con)

    # 1) WAPE total por método
    order = sorted(methods, key=lambda m: summary[(m, "total")]["wape"], reverse=True)
    fig, ax = plt.subplots(figsize=(9, 3.2))
    vals = [100 * summary[(m, "total")]["wape"] for m in order]
    bars = ax.barh([LABELS[m] for m in order], vals, color=[BLUE if m == production else MUTED for m in order], height=0.6)
    for b, v in zip(bars, vals):
        ax.text(v + 0.4, b.get_y() + b.get_height() / 2, f"{v:.1f}%", va="center", color=INK, fontsize=9)
    ax.axvline(100 * floor, color=INK2, lw=1, ls="--")
    ax.text(100 * floor + 0.3, len(order) - 0.45, f"Suelo de ruido (Poisson): {100*floor:.1f}%", color=INK2, fontsize=8.5, va="bottom")
    ax.set_xlabel("WAPE en backtest (menor es mejor). En azul: método en producción")
    ax.set_title(f"Error de pronóstico a 7 días: {len(cutoffs)} semanas de backtest")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, max(vals) * 1.15)
    ax.set_ylim(-0.6, len(order) - 0.1)
    _save(fig, img_dir / "07_backtest_wape.png")

    # 2) Real vs. pronóstico en la zona con más viajes, última semana del backtest
    zone = con.execute("""select location_id, any_value(zone) from backtest_predictions
                          where fold = (select max(fold) from backtest_predictions)
                          group by 1 order by sum(actual) desc limit 1""").fetchone()
    d = con.execute(f"""select hour_ts, actual, pred_{best} as model, pred_media_4_semanas as naive
                        from backtest_predictions where fold = (select max(fold) from backtest_predictions)
                        and location_id = {zone[0]} order by hour_ts""").fetchnumpy()
    fig, ax = plt.subplots(figsize=(11, 3.8))
    ax.plot(d["hour_ts"], d["actual"], color=INK, lw=1.6, label="Real")
    ax.plot(d["hour_ts"], d["naive"], color=BLUE, lw=2, label=LABELS["media_4_semanas"] + " (producción)")
    ax.plot(d["hour_ts"], d["model"], color=ORANGE, lw=1.4, ls="--", label=LABELS[best])
    ax.set_title(f"{zone[1]}: viajes por hora, real vs. pronóstico (última semana del backtest)")
    ax.set_ylabel("Viajes por hora")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d-%b"))
    ax.legend(frameon=False, loc="upper left", ncols=3)
    ax.set_ylim(0, max(d["actual"].max(), d["model"].max(), d["naive"].max()) * 1.18)
    _save(fig, img_dir / "08_real_vs_pronostico.png")

    # 3) Importancia (|SHAP| medio)
    idx = np.argsort(shap_imp)
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.barh([FEATURE_LABELS[FEATURES[i]] for i in idx], shap_imp[idx], color=BLUE, height=0.6)
    ax.set_xlabel("Contribución media absoluta al pronóstico (SHAP, escala log)")
    ax.set_title(f"{LABELS[best]}: ¿qué variables usa?")
    ax.grid(axis="y", visible=False)
    _save(fig, img_dir / "09_importancia_variables.png")

    # ---------------- Markdown
    def pct(x):
        return f"{100 * x:.1f}%"

    L = ["# Modelo de demanda zona-hora — resultados\n",
         f"Pronóstico a **7 días (168 h)** de viajes de taxi amarillo por zona de recogida y hora. "
         f"Backtest de origen móvil con **{len(cutoffs)} semanas** "
         f"({cutoffs[0]:%d-%b-%Y} a {cutoffs[-1]:%d-%b-%Y}); en cada corte se entrena solo con el pasado.\n",
         "## Resultado\n",
         (f"**{LABELS[best]}** reduce el WAPE un **{pct(gain)}** frente al mejor baseline ({LABELS[best_base]}) "
          f"y es el método en producción.\n" if production == best else
          f"**El modelo de machine learning no supera al baseline.** El mejor LightGBM ({LABELS[best]}) obtiene un WAPE "
          f"{pct(summary[(best, 'total')]['wape'])} frente a {pct(summary[(best_base, 'total')]['wape'])} de "
          f"{LABELS[best_base]} (un {pct(-gain)} peor). Regla de producción: un modelo complejo solo se publica si mejora "
          f"al simple en más de un 2%. **En producción: {LABELS[production]}.**\n"),
         f"El suelo de ruido Poisson estimado es **{pct(floor)}**: hay margen de mejora, pero no con las variables "
         f"disponibles (solo historia de la propia demanda). Ver *Experimentos* más abajo.\n",
         "| Método | WAPE total | WAPE zonas densas | WAPE zonas intermitentes | MAE (viajes/h) | Sesgo | Desv. WAPE entre semanas |",
         "|---|---:|---:|---:|---:|---:|---:|"]
    for m in methods:
        s = summary[(m, "total")]
        L.append(f"| {LABELS[m]}{' ⭐ producción' if m == production else ''} | {pct(s['wape'])} | {pct(summary[(m, 'densa')]['wape'])} "
                 f"| {pct(summary[(m, 'intermitente')]['wape'])} | {s['mae']:.2f} | {s['bias']:+.1%} | {pct(s['wape_std'])} |")
    L += ["\n- **WAPE** = Σ|real − pronóstico| / Σ real. Se usa en vez de MAPE porque el 49% de las horas-zona tienen 0 viajes (MAPE sería infinito).",
          "- **Zonas densas**: < 10% de horas sin viajes (calculado solo con datos previos al backtest).",
          "- **Sesgo** > 0 = el modelo sobreestima en total.\n",
          "![Backtest](../../docs/img/07_backtest_wape.png)\n",
          "## WAPE por semana de test\n",
          "| Semana desde | " + " | ".join(LABELS[m] for m in methods) + " |",
          "|---|" + "---:|" * len(methods)]
    for i, c in enumerate(cutoffs, 1):
        r = {x["method"]: x["wape"] for x in rows_out if x["fold"] == i and x["segment"] == "total"}
        L.append(f"| {c:%d-%b-%Y} | " + " | ".join(pct(r[m]) for m in methods) + " |")
    L += ["\n![Real vs pronóstico](../../docs/img/08_real_vs_pronostico.png)\n",
          "## Experimentos realizados (backtest de 8 semanas, WAPE total)\n",
          "| Variante | WAPE | Conclusión |", "|---|---:|---|",
          "| LightGBM Tweedie, variables base | 18,7% | Referencia ML |",
          "| + mediana 4 semanas, tendencia zona y nivel ciudad | 19,0% | Empeora: descartadas |",
          "| Aprender correcciones sobre la media 4 semanas (`init_score`) | 19,4% | Empeora |",
          "| Entrenar solo con el régimen actual (desde 6-ene-2025) | 19,3% | Empeora: menos datos, sesgo +2,6% |",
          "| Todo el histórico sin variables de régimen | 18,6% | Similar |",
          "| Promedio 50/50 de LightGBM y media 4 semanas | 18,3% | Igual al baseline (18,3%) |\n",
          "**Lectura:** el baseline ya captura casi toda la señal que contiene la historia de la demanda. "
          "La distancia al suelo de ruido corresponde a factores externos que el modelo no ve "
          "(clima, eventos, tormentas). Siguiente paso: incorporar clima horario (Open-Meteo).\n",
          "## Variables\n",
          "Todas las variables de historia usan rezagos ≥ 168 h: el modelo nunca ve información que no estaría "
          "disponible al pronosticar con 7 días de antelación. No se usan `payment_type`, pasajeros ni RatecodeID "
          "porque cambiaron de composición en ene-2025 (ver `reports/quality/DECISIONES_LIMPIEZA.md`).\n",
          "| Variable | Importancia SHAP | Ganancia (%) |", "|---|---:|---:|"]
    tot_gain = gain_imp.sum()
    for i in np.argsort(-shap_imp):
        L.append(f"| {FEATURE_LABELS[FEATURES[i]]} | {shap_imp[i]:.3f} | {100 * gain_imp[i] / tot_gain:.1f}% |")
    L += ["\n![Importancia](../../docs/img/09_importancia_variables.png)\n",
          "## Pronóstico generado\n",
          f"Tabla `pred_demand_zone_hour` (y `data/predictions/pred_{first_future:%Y%m%d}.parquet`): "
          f"168 h desde {first_future:%d-%b-%Y} para cada zona. `pred_trips` = método en producción "
          f"({LABELS[production]}); también incluye la predicción de {LABELS[best]} para comparación.\n",
          "## Limitaciones\n",
          "- 6 meses de historia: el modelo no ha visto un año completo (estacionalidad anual, verano).",
          "- Sin variables externas (clima, eventos). Son las siguientes candidatas.",
          "- El backtest cubre feb-mar 2025, tras el cambio estructural de la fuente en enero."]
    (report_dir / "MODELO.md").write_text("\n".join(L), encoding="utf-8")
