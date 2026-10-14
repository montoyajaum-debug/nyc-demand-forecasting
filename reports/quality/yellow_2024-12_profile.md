# Perfil de calidad - Yellow Taxi 2024-12

- Archivo: `yellow_tripdata_2024-12.parquet`
- Filas: **3,668,371**
- Columnas: 22
- Filas con al menos una regla incumplida: **1,192,363 (32.50%)**

## Reglas candidatas (solo medición, no se ha borrado nada)

| Regla | Descripción | Filas | % |
|---|---|---:|---:|
| R01 | Pickup fuera del mes del archivo | 34 | 0.001% |
| R02 | Dropoff anterior o igual al pickup | 1,223 | 0.033% |
| R03 | Duración > 4 horas | 2,008 | 0.055% |
| R04 | Distancia <= 0 | 75,450 | 2.057% |
| R05 | Distancia > 100 millas | 129 | 0.004% |
| R06 | Velocidad media > 80 mph (distancia/tiempo imposible) | 1,063 | 0.029% |
| R07 | fare_amount negativo (reversos/anulaciones) | 78,444 | 2.138% |
| R08 | total_amount <= 0 | 71,102 | 1.938% |
| R09 | fare_amount > 500 USD | 46 | 0.001% |
| R10 | passenger_count nulo | 326,291 | 8.895% |
| R11 | passenger_count = 0 | 30,397 | 0.829% |
| R12 | passenger_count > 6 | 18 | 0.000% |
| R13 | RatecodeID nulo o fuera de catálogo (1-6) | 368,407 | 10.043% |
| R14 | Zona desconocida (264/265) en origen o destino | 35,295 | 0.962% |
| R15 | payment_type 6 (viaje anulado) | 0 | 0.000% |
| R16 | total_amount no cuadra con la suma de componentes (tolerancia 0.05) | 981,148 | 26.746% |
| R17 | Filas duplicadas exactas | 0 | 0.000% |

## Perfil por columna

| Columna | Tipo | Mín | Máx | Media | p50 | Nulos % | Distintos aprox. |
|---|---|---|---|---|---|---:|---:|
| VendorID | INTEGER | 1 | 7 | 1.77471308 | 2 | 0.00 | 4 |
| tpep_pickup_datetime | TIMESTAMP | 2008-12-31 23:03:59 | 2025-03-23 20:42:06 | 2024-12-15 | 2024-12-14 17:05:55.665302 | 0.00 | 1,940,560 |
| tpep_dropoff_datetime | TIMESTAMP | 2009-01-01 00:30:36 | 2025-03-23 22:52:56 | 2024-12-15 | 2024-12-14 17:42:05.713601 | 0.00 | 2,128,522 |
| passenger_count | BIGINT | 0 | 9 | 1.36244225 | 1 | 8.89 | 11 |
| trip_distance | DOUBLE | 0.0 | 328827.63 | 5.08780132 | 1.6728172210550654 | 0.00 | 3,808 |
| RatecodeID | BIGINT | 1 | 99 | 2.32834492 | 1 | 8.89 | 7 |
| store_and_fwd_flag | VARCHAR | N | Y |  | None | 8.89 | 2 |
| PULocationID | INTEGER | 1 | 265 | 164.883986 | 162 | 0.00 | 266 |
| DOLocationID | INTEGER | 1 | 265 | 163.791121 | 162 | 0.00 | 290 |
| payment_type | BIGINT | 0 | 4 | 1.13346578 | 1 | 0.00 | 5 |
| fare_amount | DOUBLE | -975.0 | 3033.1 | 19.6612930 | 14.239236802988094 | 0.00 | 10,695 |
| extra | DOUBLE | -9.25 | 14.25 | 1.35590902 | 1.0 | 0.00 | 70 |
| mta_tax | DOUBLE | -0.5 | 10.5 | 0.47463173 | 0.5 | 0.00 | 9 |
| tip_amount | DOUBLE | -80.0 | 471.0 | 3.45946754 | 2.713953374141227 | 0.00 | 4,612 |
| tolls_amount | DOUBLE | -70.38 | 120.15 | 0.55699004 | 0.0 | 0.00 | 1,441 |
| improvement_surcharge | DOUBLE | -1.0 | 1.0 | 0.95157081 | 1.0 | 0.00 | 4 |
| total_amount | DOUBLE | -951.0 | 3037.1 | 28.3204142 | 21.64861961692555 | 0.00 | 18,950 |
| congestion_surcharge | DOUBLE | -2.5 | 2.5 | 2.22141667 | 2.5 | 8.89 | 5 |
| Airport_fee | DOUBLE | -1.75 | 1.75 | 0.12819097 | 0.0 | 8.89 | 3 |
| month | BIGINT | 12 | 12 | 12.0 | 12 | 0.00 | 1 |
| year | BIGINT | 2024 | 2024 | 2024.0 | 2024 | 0.00 | 1 |
| cbd_congestion_fee | DOUBLE | None | None |  | None | 100.00 | 0 |

## Por proveedor (VendorID)

| VendorID | Filas | % pax nulo | % fare negativo |
|---|---:|---:|---:|
| 1 | 829,242 | 8.17 | 0.0 |
| 2 | 2,838,485 | 9.09 | 2.76 |
| 6 | 414 | 100.0 | 0.0 |
| 7 | 230 | 0.0 | 0.0 |

## Por tipo de pago

Recordatorio: la propina solo se registra en pagos con tarjeta (payment_type=1).

| payment_type | Filas | Propina media |
|---|---:|---:|
| 0 | 326,291 | 1.27 |
| 1 | 2,733,369 | 4.49 |
| 2 | 490,651 | 0.0 |
| 3 | 28,938 | 0.05 |
| 4 | 89,122 | 0.06 |