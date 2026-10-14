# Perfil de calidad - Yellow Taxi 2025-02

- Archivo: `yellow_tripdata_2025-02.parquet`
- Filas: **3,577,543**
- Columnas: 22
- Filas con al menos una regla incumplida: **1,536,237 (42.94%)**

## Reglas candidatas (solo medición, no se ha borrado nada)

| Regla | Descripción | Filas | % |
|---|---|---:|---:|
| R01 | Pickup fuera del mes del archivo | 31 | 0.001% |
| R02 | Dropoff anterior o igual al pickup | 5,164 | 0.144% |
| R03 | Duración > 4 horas | 1,211 | 0.034% |
| R04 | Distancia <= 0 | 99,771 | 2.789% |
| R05 | Distancia > 100 millas | 172 | 0.005% |
| R06 | Velocidad media > 80 mph (distancia/tiempo imposible) | 841 | 0.024% |
| R07 | fare_amount negativo (reversos/anulaciones) | 182,655 | 5.106% |
| R08 | total_amount <= 0 | 55,621 | 1.555% |
| R09 | fare_amount > 500 USD | 45 | 0.001% |
| R10 | passenger_count nulo | 806,937 | 22.556% |
| R11 | passenger_count = 0 | 21,751 | 0.608% |
| R12 | passenger_count > 6 | 16 | 0.000% |
| R13 | RatecodeID nulo o fuera de catálogo (1-6) | 846,069 | 23.649% |
| R14 | Zona desconocida (264/265) en origen o destino | 25,008 | 0.699% |
| R15 | payment_type 6 (viaje anulado) | 0 | 0.000% |
| R16 | total_amount no cuadra con la suma de componentes (tolerancia 0.05) | 1,278,590 | 35.739% |
| R17 | Filas duplicadas exactas | 0 | 0.000% |

## Perfil por columna

| Columna | Tipo | Mín | Máx | Media | p50 | Nulos % | Distintos aprox. |
|---|---|---|---|---|---|---:|---:|
| VendorID | INTEGER | 1 | 7 | 1.79551049 | 2 | 0.00 | 4 |
| tpep_pickup_datetime | TIMESTAMP | 2025-01-31 22:22:53 | 2025-03-01 00:06:32 | 2025-02-15 | 2025-02-14 22:58:00.287731 | 0.00 | 1,495,253 |
| tpep_dropoff_datetime | TIMESTAMP | 2025-01-31 22:30:00 | 2025-03-01 23:13:42 | 2025-02-15 | 2025-02-14 23:48:17.697615 | 0.00 | 1,260,697 |
| passenger_count | BIGINT | 0 | 9 | 1.27602769 | 1 | 22.56 | 11 |
| trip_distance | DOUBLE | 0.0 | 228782.51 | 6.02535659 | 1.7086879589408837 | 0.00 | 3,440 |
| RatecodeID | BIGINT | 1 | 99 | 2.45888552 | 1 | 22.56 | 7 |
| store_and_fwd_flag | VARCHAR | N | Y |  | None | 22.56 | 2 |
| PULocationID | INTEGER | 1 | 265 | 163.284595 | 161 | 0.00 | 266 |
| DOLocationID | INTEGER | 1 | 265 | 162.481337 | 162 | 0.00 | 290 |
| payment_type | BIGINT | 0 | 4 | 0.94285044 | 1 | 0.00 | 5 |
| fare_amount | DOUBLE | -1807.6 | 132531.36 | 16.7490055 | 12.805017762156583 | 0.00 | 8,145 |
| extra | DOUBLE | -7.5 | 22.55 | 1.23810846 | 0.0 | 0.00 | 74 |
| mta_tax | DOUBLE | -0.5 | 10.5 | 0.48051583 | 0.5 | 0.00 | 10 |
| tip_amount | DOUBLE | -220.0 | 440.0 | 2.73006356 | 2.1246738476893166 | 0.00 | 3,136 |
| tolls_amount | DOUBLE | -113.93 | 115.87 | 0.40529436 | 0.0 | 0.00 | 1,112 |
| improvement_surcharge | DOUBLE | -1.0 | 1.0 | 0.95916183 | 1.0 | 0.00 | 4 |
| total_amount | DOUBLE | -1832.85 | 132555.41 | 25.0305500 | 20.181123504057844 | 0.00 | 15,725 |
| congestion_surcharge | DOUBLE | -2.5 | 2.5 | 2.23168866 | 2.5 | 22.56 | 3 |
| Airport_fee | DOUBLE | -1.75 | 6.75 | 0.12163106 | 0.0 | 22.56 | 5 |
| cbd_congestion_fee | DOUBLE | -0.75 | 1.25 | 0.53731772 | 0.75 | 0.00 | 4 |
| month | VARCHAR | 02 | 02 |  | None | 0.00 | 1 |
| year | BIGINT | 2025 | 2025 | 2025.0 | 2025 | 0.00 | 1 |

## Por proveedor (VendorID)

| VendorID | Filas | % pax nulo | % fare negativo |
|---|---:|---:|---:|
| 1 | 754,990 | 14.78 | 0.0 |
| 2 | 2,817,803 | 24.67 | 6.48 |
| 6 | 330 | 100.0 | 0.0 |
| 7 | 4,420 | 0.0 | 0.0 |

## Por tipo de pago

Recordatorio: la propina solo se registra en pagos con tarjeta (payment_type=1).

| payment_type | Filas | Propina media |
|---|---:|---:|
| 0 | 806,937 | 0.32 |
| 1 | 2,336,175 | 4.07 |
| 2 | 339,481 | 0.0 |
| 3 | 21,849 | 0.03 |
| 4 | 73,101 | 0.05 |