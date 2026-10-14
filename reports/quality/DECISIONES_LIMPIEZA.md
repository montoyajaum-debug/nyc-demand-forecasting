# Decisiones de limpieza — Yellow Taxi

Basadas en el perfilado de enero 2025 (`yellow_2025-01_profile.md`, 3.475.226 filas).
Implementadas en `dbt_project/models/silver/`. Umbrales parametrizados en `dbt_project.yml` (vars).

## Principio
Separar **"¿es un viaje real?"** (se descarta si no) de **"¿sus importes/campos son fiables?"**
(se conserva con bandera). El modelo de demanda cuenta viajes; el análisis de tarifas filtra por banderas.
Un filtro único habría eliminado el 37% de los viajes reales.

## A. Descartadas (no son viajes) → `silver_yellow_rejected`

| Regla | Criterio | Ene-2025 | Justificación |
|---|---|---:|---|
| R07 | `fare_amount < 0` | 144.118 (4,15%) | Asientos contables. Solo VendorID 2. 59.288 son reverso exacto de un cobro positivo |
| R04 | distancia ≤ 0 y duración < 1 min | 21.798 (0,63%) | Arranques falsos / registros de tarifa fija sin recorrido |
| R02 | dropoff < pickup, o dropoff = pickup sin recorrido ni cobro | 0,02–0,05% | Tiempo imposible. *Ajustada tras validar 6 meses (ver abajo)* |
| R03 | duración > 240 min | 1.265 (0,04%) | Meter no cerrado |
| R06 | velocidad > 80 mph | 950 (0,03%) | Distancia/tiempo incoherentes |
| R01 | pickup fuera del mes del archivo | 22 (0,00%) | Reloj del dispositivo mal configurado |
| | **Total descartado (ene-2025)** | **~4,9%** | |

## B. Conservadas con bandera → `silver_yellow_trips` (3.305.033 viajes)

| Bandera | % de silver | Uso |
|---|---:|---|
| `is_payment_type_0` | 13,72% | Registros con pasajeros, RatecodeID, congestion_surcharge y airport_fee nulos a la vez. Tarifa y duración normales → **viajes válidos para demanda** (decisión aprobada) |
| `is_pax_unknown` | 14,45% | Pasajeros nulo o 0. **No se imputa** |
| `is_valid_distance` = false | 1,63% | Excluir en análisis de distancia/velocidad |
| `is_known_zone` = false | 0,78% | Zonas 264/265. Excluir del modelo por zona |
| `is_valid_fare` = false | 0,03% | Excluir en análisis de tarifas |
| `is_tip_recorded` | — | Propina solo se registra con tarjeta: análisis de propinas solo con `payment_type = 1` |
| `was_reversed` | 55.378 | Cobro con reverso posterior. Se cuenta como viaje; revisar en análisis de ingresos |

## C. Regla retirada
**R16 (total ≠ suma de componentes, 32% de filas):** las diferencias se concentran en ±2,50 y −3,25,
valores que coinciden con recargos. Indica que la composición de `total_amount` varía por tipo de registro;
la causa exacta no está confirmada. No afecta a la demanda → se documenta como limitación, no se filtra.

## Controles automáticos (dbt test)
- Conciliación: bronze = silver + rechazadas, por mes (`assert_row_reconciliation`)
- Alerta si un mes descarta > 10% (`assert_reject_rate_below_threshold`)
- Rangos, nulos, catálogos e integridad referencial con zonas (18 tests en silver, 29 en total con gold)


## Validación en 6 meses (oct-2024 a mar-2025, 22,3 M registros)

% de registros por resultado:

| Resultado | 2024-10 | 2024-11 | 2024-12 | 2025-01 | 2025-02 | 2025-03 |
|---|---:|---:|---:|---:|---:|---:|
| **Válido** | 97,25 | 97,24 | 97,02 | 95,14 | 94,26 | 94,30 |
| R07 tarifa negativa | 1,97 | 1,96 | 2,14 | 4,15 | 5,11 | 5,04 |
| R04 viaje fantasma | 0,68 | 0,67 | 0,73 | 0,63 | 0,56 | 0,58 |
| R03 duración > 4 h | 0,05 | 0,05 | 0,05 | 0,04 | 0,03 | 0,04 |
| R02 tiempo inválido | 0,03 | 0,05 | 0,03 | 0,02 | 0,02 | 0,02 |
| R06 velocidad > 80 mph | 0,03 | 0,03 | 0,03 | 0,03 | 0,02 | 0,02 |
| R01 fuera de mes | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |

### Hallazgos de la validación multi-mes
1. **Ajuste de R02 (VendorID 7).** Proveedor nuevo en 2025. En mar-2025 envía 22.199 viajes con
   dropoff = pickup pero distancia (2,9 mi) y tarifa (16 USD) normales: falta la hora de llegada, el viaje existe.
   La regla original los descartaba. Ahora se conservan con `duration_min = NULL` e `is_valid_duration = false`.
   Sin este ajuste, la demanda de marzo se habría subestimado en ~0,6%.
2. **Cambio estructural en la fuente desde ene-2025.** Los registros `payment_type = 0` pasan de ~10% a ~20%
   (VendorID 2: de 9–11% a 24–25%). Las variables pasajeros/RatecodeID no son comparables antes y después:
   **no se usan como features del modelo**.
3. **Tarifas negativas se duplican en 2025** (2% → 5%), coincidiendo con el cargo por congestión (5-ene-2025);
   en mar-2025, 46.863 de ellas revierten también `cbd_congestion_fee`. Se descartan igual (son asientos contables),
   pero el aumento se documenta para el análisis de impacto.

> Lección: validar las reglas con un solo mes no basta. Dos de los tres hallazgos solo aparecen al comparar meses.
