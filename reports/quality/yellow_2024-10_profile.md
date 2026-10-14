# Perfil de calidad - Yellow Taxi 2024-10

- Archivo: `yellow_tripdata_2024-10.parquet`
- Filas: **3,833,771**
- Columnas: 22
- Filas con al menos una regla incumplida: **1,311,735 (34.22%)**

## Reglas candidatas (solo medición, no se ha borrado nada)

| Regla | Descripción | Filas | % |
|---|---|---:|---:|
| R01 | Pickup fuera del mes del archivo | 40 | 0.001% |
| R02 | Dropoff anterior o igual al pickup | 1,002 | 0.026% |
| R03 | Duración > 4 horas | 1,876 | 0.049% |
| R04 | Distancia <= 0 | 81,639 | 2.129% |
| R05 | Distancia > 100 millas | 129 | 0.003% |
| R06 | Velocidad media > 80 mph (distancia/tiempo imposible) | 1,107 | 0.029% |
| R07 | fare_amount negativo (reversos/anulaciones) | 75,377 | 1.966% |
| R08 | total_amount <= 0 | 61,858 | 1.614% |
| R09 | fare_amount > 500 USD | 36 | 0.001% |
| R10 | passenger_count nulo | 393,895 | 10.274% |
| R11 | passenger_count = 0 | 35,770 | 0.933% |
| R12 | passenger_count > 6 | 22 | 0.001% |
| R13 | RatecodeID nulo o fuera de catálogo (1-6) | 437,576 | 11.414% |
| R14 | Zona desconocida (264/265) en origen o destino | 42,609 | 1.111% |
| R15 | payment_type 6 (viaje anulado) | 0 | 0.000% |
| R16 | total_amount no cuadra con la suma de componentes (tolerancia 0.05) | 1,103,039 | 28.772% |
| R17 | Filas duplicadas exactas | 2 | 0.000% |

## Perfil por columna

| Columna | Tipo | Mín | Máx | Media | p50 | Nulos % | Distintos aprox. |
|---|---|---|---|---|---|---:|---:|
| VendorID | INTEGER | 1 | 6 | 1.76715823 | 2 | 0.00 | 3 |
| tpep_pickup_datetime | TIMESTAMP | 2009-01-01 00:35:59 | 2024-11-14 18:30:00 | 2024-10-16 | 2024-10-17 03:47:30.797608 | 0.00 | 1,646,536 |
| tpep_dropoff_datetime | TIMESTAMP | 2009-01-01 01:29:28 | 2024-11-14 18:41:41 | 2024-10-16 | 2024-10-17 01:58:38.370722 | 0.00 | 1,673,214 |
| passenger_count | BIGINT | 0 | 9 | 1.30844978 | 1 | 10.27 | 11 |
| trip_distance | DOUBLE | 0.0 | 366343.04 | 5.12356828 | 1.7711624671635504 | 0.00 | 3,580 |
| RatecodeID | BIGINT | 1 | 99 | 2.33938578 | 1 | 10.27 | 7 |
| store_and_fwd_flag | VARCHAR | N | Y |  | None | 10.27 | 2 |
| PULocationID | INTEGER | 1 | 265 | 164.487977 | 161 | 0.00 | 290 |
| DOLocationID | INTEGER | 1 | 265 | 163.974879 | 162 | 0.00 | 272 |
| payment_type | BIGINT | 0 | 4 | 1.09943499 | 1 | 0.00 | 5 |
| fare_amount | DOUBLE | -920.0 | 1680.2 | 19.7207139 | 14.236407077837024 | 0.00 | 8,804 |
| extra | DOUBLE | -7.5 | 16.0 | 1.40085151 | 1.0 | 0.00 | 68 |
| mta_tax | DOUBLE | -0.5 | 10.5 | 0.47816695 | 0.5 | 0.00 | 11 |
| tip_amount | DOUBLE | -67.45 | 500.0 | 3.42482251 | 2.690039090245082 | 0.00 | 3,783 |
| tolls_amount | DOUBLE | -76.38 | 150.0 | 0.58459950 | 0.0 | 0.00 | 1,216 |
| improvement_surcharge | DOUBLE | -1.0 | 2.0 | 0.95752140 | 1.0 | 0.00 | 5 |
| total_amount | DOUBLE | -901.0 | 1690.89 | 28.4296287 | 21.52999844595903 | 0.00 | 17,716 |
| congestion_surcharge | DOUBLE | -2.5 | 2.5 | 2.23065228 | 2.5 | 10.27 | 6 |
| Airport_fee | DOUBLE | -1.75 | 1.75 | 0.15037271 | 0.0 | 10.27 | 4 |
| month | BIGINT | 10 | 10 | 10.0 | 10 | 0.00 | 1 |
| year | BIGINT | 2024 | 2024 | 2024.0 | 2024 | 0.00 | 1 |
| cbd_congestion_fee | DOUBLE | None | None |  | None | 100.00 | 0 |

## Por proveedor (VendorID)

| VendorID | Filas | % pax nulo | % fare negativo |
|---|---:|---:|---:|
| 1 | 892,962 | 7.94 | 0.0 |
| 2 | 2,940,734 | 10.98 | 2.56 |
| 6 | 75 | 100.0 | 0.0 |

## Por tipo de pago

Recordatorio: la propina solo se registra en pagos con tarjeta (payment_type=1).

| payment_type | Filas | Propina media |
|---|---:|---:|
| 0 | 393,895 | 0.68 |
| 1 | 2,854,092 | 4.5 |
| 2 | 477,350 | 0.0 |
| 3 | 27,546 | 0.02 |
| 4 | 80,888 | 0.05 |