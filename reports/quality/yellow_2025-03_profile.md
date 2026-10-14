# Perfil de calidad - Yellow Taxi 2025-03

- Archivo: `yellow_tripdata_2025-03.parquet`
- Filas: **4,145,257**
- Columnas: 22
- Filas con al menos una regla incumplida: **1,739,430 (41.96%)**

## Reglas candidatas (solo medición, no se ha borrado nada)

| Regla | Descripción | Filas | % |
|---|---|---:|---:|
| R01 | Pickup fuera del mes del archivo | 33 | 0.001% |
| R02 | Dropoff anterior o igual al pickup | 22,280 | 0.537% |
| R03 | Duración > 4 horas | 1,473 | 0.036% |
| R04 | Distancia <= 0 | 103,722 | 2.502% |
| R05 | Distancia > 100 millas | 214 | 0.005% |
| R06 | Velocidad media > 80 mph (distancia/tiempo imposible) | 1,050 | 0.025% |
| R07 | fare_amount negativo (reversos/anulaciones) | 208,724 | 5.035% |
| R08 | total_amount <= 0 | 69,287 | 1.671% |
| R09 | fare_amount > 500 USD | 46 | 0.001% |
| R10 | passenger_count nulo | 916,663 | 22.114% |
| R11 | passenger_count = 0 | 22,715 | 0.548% |
| R12 | passenger_count > 6 | 13 | 0.000% |
| R13 | RatecodeID nulo o fuera de catálogo (1-6) | 960,651 | 23.175% |
| R14 | Zona desconocida (264/265) en origen o destino | 28,415 | 0.685% |
| R15 | payment_type 6 (viaje anulado) | 0 | 0.000% |
| R16 | total_amount no cuadra con la suma de componentes (tolerancia 0.05) | 1,384,035 | 33.388% |
| R17 | Filas duplicadas exactas | 0 | 0.000% |

## Perfil por columna

| Columna | Tipo | Mín | Máx | Media | p50 | Nulos % | Distintos aprox. |
|---|---|---|---|---|---|---:|---:|
| VendorID | INTEGER | 1 | 7 | 1.82494378 | 2 | 0.00 | 4 |
| tpep_pickup_datetime | TIMESTAMP | 2007-12-05 18:45:00 | 2025-04-01 00:00:17 | 2025-03-16 | 2025-03-16 02:11:27.03688 | 0.00 | 1,462,778 |
| tpep_dropoff_datetime | TIMESTAMP | 2007-12-05 19:02:00 | 2025-04-03 14:07:50 | 2025-03-16 | 2025-03-16 06:05:35.693922 | 0.00 | 1,644,461 |
| passenger_count | BIGINT | 0 | 9 | 1.29111991 | 1 | 22.11 | 11 |
| trip_distance | DOUBLE | 0.0 | 320136.29 | 6.58409978 | 1.7943299027754147 | 0.00 | 3,237 |
| RatecodeID | BIGINT | 1 | 99 | 2.42349239 | 1 | 22.11 | 7 |
| store_and_fwd_flag | VARCHAR | N | Y |  | None | 22.11 | 2 |
| PULocationID | INTEGER | 1 | 265 | 161.765313 | 161 | 0.00 | 266 |
| DOLocationID | INTEGER | 1 | 265 | 161.228734 | 162 | 0.00 | 266 |
| payment_type | BIGINT | 0 | 4 | 0.95609512 | 1 | 0.00 | 5 |
| fare_amount | DOUBLE | -999.0 | 46263.88 | 17.8003425 | 13.489324944959593 | 0.00 | 9,542 |
| extra | DOUBLE | -9.25 | 13.5 | 1.22092410 | 0.0 | 0.00 | 76 |
| mta_tax | DOUBLE | -0.5 | 10.5 | 0.47857167 | 0.5 | 0.00 | 11 |
| tip_amount | DOUBLE | -92.09 | 290.0 | 2.85885602 | 2.1818245740741755 | 0.00 | 4,115 |
| tolls_amount | DOUBLE | -142.17 | 916.87 | 0.47497649 | 0.0 | 0.00 | 1,146 |
| improvement_surcharge | DOUBLE | -1.0 | 1.0 | 0.95710857 | 1.0 | 0.00 | 4 |
| total_amount | DOUBLE | -1000.0 | 46269.44 | 26.2658980 | 20.793916043076752 | 0.00 | 20,486 |
| congestion_surcharge | DOUBLE | -2.5 | 2.5 | 2.21939441 | 2.5 | 22.11 | 4 |
| Airport_fee | DOUBLE | -1.75 | 6.75 | 0.13512275 | 0.0 | 22.11 | 6 |
| cbd_congestion_fee | DOUBLE | -0.75 | 1.5 | 0.53642681 | 0.75 | 0.00 | 6 |
| month | VARCHAR | 03 | 03 |  | None | 0.00 | 1 |
| year | BIGINT | 2025 | 2025 | 2025.0 | 2025 | 0.00 | 1 |

## Por proveedor (VendorID)

| VendorID | Filas | % pax nulo | % fare negativo |
|---|---:|---:|---:|
| 1 | 834,394 | 15.84 | 0.0 |
| 2 | 3,289,048 | 23.84 | 6.35 |
| 6 | 334 | 100.0 | 0.0 |
| 7 | 21,481 | 0.0 | 0.0 |

## Por tipo de pago

Recordatorio: la propina solo se registra en pagos con tarjeta (payment_type=1).

| payment_type | Filas | Propina media |
|---|---:|---:|
| 0 | 916,663 | 0.37 |
| 1 | 2,704,166 | 4.26 |
| 2 | 405,847 | 0.0 |
| 3 | 26,924 | 0.02 |
| 4 | 91,657 | 0.04 |