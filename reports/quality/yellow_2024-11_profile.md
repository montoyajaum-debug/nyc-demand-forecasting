# Perfil de calidad - Yellow Taxi 2024-11

- Archivo: `yellow_tripdata_2024-11.parquet`
- Filas: **3,646,369**
- Columnas: 22
- Filas con al menos una regla incumplida: **1,239,656 (34.00%)**

## Reglas candidatas (solo medición, no se ha borrado nada)

| Regla | Descripción | Filas | % |
|---|---|---:|---:|
| R01 | Pickup fuera del mes del archivo | 50 | 0.001% |
| R02 | Dropoff anterior o igual al pickup | 1,861 | 0.051% |
| R03 | Duración > 4 horas | 1,958 | 0.054% |
| R04 | Distancia <= 0 | 68,315 | 1.874% |
| R05 | Distancia > 100 millas | 148 | 0.004% |
| R06 | Velocidad media > 80 mph (distancia/tiempo imposible) | 1,023 | 0.028% |
| R07 | fare_amount negativo (reversos/anulaciones) | 71,470 | 1.960% |
| R08 | total_amount <= 0 | 61,049 | 1.674% |
| R09 | fare_amount > 500 USD | 41 | 0.001% |
| R10 | passenger_count nulo | 373,674 | 10.248% |
| R11 | passenger_count = 0 | 28,370 | 0.778% |
| R12 | passenger_count > 6 | 21 | 0.001% |
| R13 | RatecodeID nulo o fuera de catálogo (1-6) | 416,100 | 11.411% |
| R14 | Zona desconocida (264/265) en origen o destino | 32,984 | 0.905% |
| R15 | payment_type 6 (viaje anulado) | 0 | 0.000% |
| R16 | total_amount no cuadra con la suma de componentes (tolerancia 0.05) | 1,030,072 | 28.249% |
| R17 | Filas duplicadas exactas | 0 | 0.000% |

## Perfil por columna

| Columna | Tipo | Mín | Máx | Media | p50 | Nulos % | Distintos aprox. |
|---|---|---|---|---|---|---:|---:|
| VendorID | INTEGER | 1 | 6 | 1.76808490 | 2 | 0.00 | 3 |
| tpep_pickup_datetime | TIMESTAMP | 2002-12-31 22:17:43 | 2024-12-01 22:04:33 | 2024-11-15 | 2024-11-15 20:20:55.675732 | 0.00 | 1,514,995 |
| tpep_dropoff_datetime | TIMESTAMP | 2002-12-31 22:23:55 | 2024-12-01 23:10:54 | 2024-11-15 | 2024-11-15 18:44:55.026628 | 0.00 | 2,144,058 |
| passenger_count | BIGINT | 0 | 9 | 1.32807151 | 1 | 10.25 | 11 |
| trip_distance | DOUBLE | 0.0 | 398608.62 | 5.36954060 | 1.7249932834055093 | 0.00 | 3,885 |
| RatecodeID | BIGINT | 1 | 99 | 2.35826619 | 1 | 10.25 | 7 |
| store_and_fwd_flag | VARCHAR | N | Y |  | None | 10.25 | 2 |
| PULocationID | INTEGER | 1 | 265 | 164.621977 | 162 | 0.00 | 272 |
| DOLocationID | INTEGER | 1 | 265 | 163.822862 | 162 | 0.00 | 290 |
| payment_type | BIGINT | 0 | 4 | 1.09904483 | 1 | 0.00 | 5 |
| fare_amount | DOUBLE | -1458.3 | 335544.44 | 19.1980649 | 13.925999916745543 | 0.00 | 8,961 |
| extra | DOUBLE | -7.5 | 14.25 | 1.31129500 | 0.9982142850985916 | 0.00 | 59 |
| mta_tax | DOUBLE | -0.5 | 41.3 | 0.47788650 | 0.5 | 0.00 | 11 |
| tip_amount | DOUBLE | -93.68 | 572.5 | 3.31519399 | 2.6285771812363206 | 0.00 | 3,853 |
| tolls_amount | DOUBLE | -140.63 | 140.63 | 0.53895810 | 0.0 | 0.00 | 1,000 |
| improvement_surcharge | DOUBLE | -1.0 | 1.0 | 0.95627677 | 1.0 | 0.00 | 5 |
| total_amount | DOUBLE | -1477.68 | 335550.94 | 27.6520190 | 21.094555625480787 | 0.00 | 19,321 |
| congestion_surcharge | DOUBLE | -2.5 | 2.5 | 2.23716791 | 2.5 | 10.25 | 4 |
| Airport_fee | DOUBLE | -1.75 | 1.75 | 0.13458128 | 0.0 | 10.25 | 3 |
| month | BIGINT | 11 | 11 | 11.0 | 11 | 0.00 | 1 |
| year | BIGINT | 2024 | 2024 | 2024.0 | 2024 | 0.00 | 1 |
| cbd_congestion_fee | DOUBLE | None | None |  | None | 100.00 | 0 |

## Por proveedor (VendorID)

| VendorID | Filas | % pax nulo | % fare negativo |
|---|---:|---:|---:|
| 1 | 846,540 | 8.38 | 0.0 |
| 2 | 2,799,606 | 10.81 | 2.55 |
| 6 | 223 | 100.0 | 0.0 |

## Por tipo de pago

Recordatorio: la propina solo se registra en pagos con tarjeta (payment_type=1).

| payment_type | Filas | Propina media |
|---|---:|---:|
| 0 | 373,674 | 0.73 |
| 1 | 2,718,920 | 4.34 |
| 2 | 449,826 | 0.0 |
| 3 | 26,845 | 0.03 |
| 4 | 77,104 | 0.05 |