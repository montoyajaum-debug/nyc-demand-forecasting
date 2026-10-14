# Perfil de calidad - Yellow Taxi 2025-01

- Archivo: `yellow_tripdata_2025-01.parquet`
- Filas: **3,475,226**
- Columnas: 22
- Filas con al menos una regla incumplida: **1,293,547 (37.22%)**

## Reglas candidatas (solo medición, no se ha borrado nada)

| Regla | Descripción | Filas | % |
|---|---|---:|---:|
| R01 | Pickup fuera del mes del archivo | 22 | 0.001% |
| R02 | Dropoff anterior o igual al pickup | 2,051 | 0.059% |
| R03 | Duración > 4 horas | 1,278 | 0.037% |
| R04 | Distancia <= 0 | 90,893 | 2.615% |
| R05 | Distancia > 100 millas | 162 | 0.005% |
| R06 | Velocidad media > 80 mph (distancia/tiempo imposible) | 982 | 0.028% |
| R07 | fare_amount negativo (reversos/anulaciones) | 144,118 | 4.147% |
| R08 | total_amount <= 0 | 63,596 | 1.830% |
| R09 | fare_amount > 500 USD | 55 | 0.002% |
| R10 | passenger_count nulo | 540,149 | 15.543% |
| R11 | passenger_count = 0 | 24,656 | 0.709% |
| R12 | passenger_count > 6 | 18 | 0.001% |
| R13 | RatecodeID nulo o fuera de catálogo (1-6) | 582,112 | 16.750% |
| R14 | Zona desconocida (264/265) en origen o destino | 28,357 | 0.816% |
| R15 | payment_type 6 (viaje anulado) | 0 | 0.000% |
| R16 | total_amount no cuadra con la suma de componentes (tolerancia 0.05) | 1,111,802 | 31.992% |
| R17 | Filas duplicadas exactas | 0 | 0.000% |

## Perfil por columna

| Columna | Tipo | Mín | Máx | Media | p50 | Nulos % | Distintos aprox. |
|---|---|---|---|---|---|---:|---:|
| VendorID | INTEGER | 1 | 7 | 1.78542834 | 2 | 0.00 | 4 |
| tpep_pickup_datetime | TIMESTAMP | 2024-12-31 20:47:55 | 2025-02-01 00:00:44 | 2025-01-17 | 2025-01-17 14:20:33.973906 | 0.00 | 1,967,401 |
| tpep_dropoff_datetime | TIMESTAMP | 2024-12-18 07:52:40 | 2025-02-01 23:44:11 | 2025-01-17 | 2025-01-17 14:47:54.805577 | 0.00 | 1,773,673 |
| passenger_count | BIGINT | 0 | 9 | 1.29785896 | 1 | 15.54 | 11 |
| trip_distance | DOUBLE | 0.0 | 276423.57 | 5.85512617 | 1.6685213697131884 | 0.00 | 3,330 |
| RatecodeID | BIGINT | 1 | 99 | 2.48253452 | 1 | 15.54 | 7 |
| store_and_fwd_flag | VARCHAR | N | Y |  | None | 15.54 | 2 |
| PULocationID | INTEGER | 1 | 265 | 165.191575 | 162 | 0.00 | 266 |
| DOLocationID | INTEGER | 1 | 265 | 164.125176 | 162 | 0.00 | 290 |
| payment_type | BIGINT | 0 | 5 | 1.03662294 | 1 | 0.00 | 6 |
| fare_amount | DOUBLE | -900.0 | 863372.12 | 17.0818027 | 12.279666225608656 | 0.00 | 10,304 |
| extra | DOUBLE | -7.5 | 15.0 | 1.31773669 | 0.007020615014050861 | 0.00 | 73 |
| mta_tax | DOUBLE | -0.5 | 10.5 | 0.47809905 | 0.5 | 0.00 | 10 |
| tip_amount | DOUBLE | -86.0 | 400.0 | 2.95981278 | 2.4394332914382186 | 0.00 | 3,209 |
| tolls_amount | DOUBLE | -126.94 | 170.94 | 0.44930810 | 0.0 | 0.00 | 1,127 |
| improvement_surcharge | DOUBLE | -1.0 | 1.0 | 0.95479456 | 1.0 | 0.00 | 4 |
| total_amount | DOUBLE | -901.0 | 863380.37 | 25.6112916 | 19.998008889970215 | 0.00 | 20,482 |
| congestion_surcharge | DOUBLE | -2.5 | 2.5 | 2.22523719 | 2.5 | 15.54 | 3 |
| Airport_fee | DOUBLE | -1.75 | 6.75 | 0.12391105 | 0.0 | 15.54 | 7 |
| cbd_congestion_fee | DOUBLE | -0.75 | 0.75 | 0.48340928 | 0.75 | 0.00 | 3 |
| month | VARCHAR | 01 | 01 |  | None | 0.00 | 1 |
| year | BIGINT | 2025 | 2025 | 2025.0 | 2025 | 0.00 | 1 |

## Por proveedor (VendorID)

| VendorID | Filas | % pax nulo | % fare negativo |
|---|---:|---:|---:|
| 1 | 753,671 | 11.7 | 0.0 |
| 2 | 2,719,860 | 16.6 | 5.3 |
| 6 | 489 | 100.0 | 0.0 |
| 7 | 1,206 | 0.0 | 0.0 |

## Por tipo de pago

Recordatorio: la propina solo se registra en pagos con tarjeta (payment_type=1).

| payment_type | Filas | Propina media |
|---|---:|---:|
| 0 | 540,149 | 0.45 |
| 1 | 2,444,393 | 4.11 |
| 2 | 390,429 | 0.0 |
| 3 | 23,773 | 0.02 |
| 4 | 76,481 | 0.04 |
| 5 | 1 | 0.0 |