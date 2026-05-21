# Intervención — Optimización de Consultas

## Objetivo

Aplicar una intervención técnica sobre las consultas diagnosticadas en el baseline del Taller 4, medir el antes y el después, y justificar el cambio con base en el plan de ejecución.

## Problema general identificado

En las tres consultas analizadas, el plan de ejecución mostró lectura completa de `fact_ventas.parquet` y uso del operador `HASH_GROUP_BY`.

Aunque DuckDB ejecutaba correctamente los `HASH_JOIN`, las consultas debían agrupar más de 100.000 registros cada vez para producir resultados pequeños.

Por esta razón, el cuello de botella principal fue el cálculo repetitivo de agregaciones sobre la tabla de hechos.

---

## Intervención aplicada

Se aplicó una estrategia de **preagregación en la zona Gold**.

Se generaron archivos Parquet optimizados:

```text
lakehouse/gold/optimized/ventas_por_mes.parquet
lakehouse/gold/optimized/top_productos.parquet
lakehouse/gold/optimized/ingresos_categoria.parquet

Excelente. Con esos números ya podemos documentar la intervención de forma completa.

Pega esto en:

```bash
docs/intervencion_optimizacion.md
```

````md
# Intervención — Optimización de Consultas

## Objetivo

Aplicar una intervención técnica sobre las consultas diagnosticadas en el baseline del Taller 4, medir el antes y el después, y justificar el cambio con base en el plan de ejecución.

## Problema general identificado

En las tres consultas analizadas, el plan de ejecución mostró lectura completa de `fact_ventas.parquet` y uso del operador `HASH_GROUP_BY`.

Aunque DuckDB ejecutaba correctamente los `HASH_JOIN`, las consultas debían agrupar más de 100.000 registros cada vez para producir resultados pequeños.

Por esta razón, el cuello de botella principal fue el cálculo repetitivo de agregaciones sobre la tabla de hechos.

---

## Intervención aplicada

Se aplicó una estrategia de **preagregación en la zona Gold**.

Se generaron archivos Parquet optimizados:

```text
lakehouse/gold/optimized/ventas_por_mes.parquet
lakehouse/gold/optimized/top_productos.parquet
lakehouse/gold/optimized/ingresos_categoria.parquet
````

Estos archivos reducen la cantidad de filas procesadas en tiempo de consulta.

---

## Tabla de intervención

| Campo                 | Q1 — Ventas por mes                                                                                                      |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Query afectada        | Q1 — Ventas por mes                                                                                                      |
| Problema identificado | La consulta leía `fact_ventas.parquet` completo y aplicaba `HASH_GROUP_BY` para agrupar 105.010 registros por año y mes. |
| Intervención aplicada | Crear `ventas_por_mes.parquet` como tabla preagregada en Gold optimizado.                                                |
| Plan ANTES            | `READ_PARQUET fact_ventas` → `HASH_JOIN dim_tiempo` → `HASH_GROUP_BY` → `ORDER_BY`.                                      |
| Plan DESPUÉS          | `READ_PARQUET ventas_por_mes.parquet` → `ORDER_BY`.                                                                      |
| Tiempo antes          | 39.70 ms                                                                                                                 |
| Tiempo después        | 9.31 ms                                                                                                                  |
| Factor de mejora      | 4.26x                                                                                                                    |
| Justificación técnica | La consulta dejó de agrupar la tabla de hechos completa y pasó a leer solo 6 filas preagregadas por mes.                 |

---

| Campo                 | Q2 — Top productos                                                                                                                         |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Query afectada        | Q2 — Top productos por ingresos                                                                                                            |
| Problema identificado | La consulta debía leer `fact_ventas.parquet`, unir con `dim_producto` y agrupar todas las ventas por producto antes de calcular el TOP 10. |
| Intervención aplicada | Crear `top_productos.parquet` como resumen preagregado por producto y categoría.                                                           |
| Plan ANTES            | `READ_PARQUET fact_ventas` → `HASH_JOIN dim_producto` → `HASH_GROUP_BY` → `TOP_N`.                                                         |
| Plan DESPUÉS          | `READ_PARQUET top_productos.parquet` → `TOP_N`.                                                                                            |
| Tiempo antes          | 28.81 ms                                                                                                                                   |
| Tiempo después        | 10.89 ms                                                                                                                                   |
| Factor de mejora      | 2.65x                                                                                                                                      |
| Justificación técnica | La consulta dejó de recalcular unidades e ingresos por producto sobre toda la tabla de hechos y leyó directamente el resumen ya preparado. |

---

| Campo                 | Q3 — Ingresos por categoría                                                                                                   |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Query afectada        | Q3 — Ingresos por categoría                                                                                                   |
| Problema identificado | La consulta leía todas las ventas, hacía join con `dim_categoria` y agrupaba por categoría para obtener solo 5 filas finales. |
| Intervención aplicada | Crear `ingresos_categoria.parquet` como resumen preagregado por categoría.                                                    |
| Plan ANTES            | `READ_PARQUET fact_ventas` → `HASH_JOIN dim_categoria` → `HASH_GROUP_BY` → `ORDER_BY`.                                        |
| Plan DESPUÉS          | `READ_PARQUET ingresos_categoria.parquet` → `ORDER_BY`.                                                                       |
| Tiempo antes          | 21.62 ms                                                                                                                      |
| Tiempo después        | 6.77 ms                                                                                                                       |
| Factor de mejora      | 3.20x                                                                                                                         |
| Justificación técnica | La consulta pasó de procesar 105.010 registros a leer 5 filas ya agregadas por categoría.                                     |

---

## Benchmark consolidado

| Query                       | Baseline (ms) | Optimizada (ms) | Factor mejora |
| --------------------------- | ------------: | --------------: | ------------: |
| Q1 — Ventas por mes         |         39.70 |            9.31 |         4.26x |
| Q2 — Top productos          |         28.81 |           10.89 |         2.65x |
| Q3 — Ingresos por categoría |         21.62 |            6.77 |         3.20x |

---

## Conclusión

La intervención fue efectiva porque redujo el trabajo repetitivo del motor analítico.

En lugar de ejecutar agrupaciones sobre toda la tabla de hechos en cada consulta, DuckDB lee archivos Parquet preagregados en la zona Gold optimizada.

Esto demuestra que una técnica simple de preagregación puede mejorar significativamente el rendimiento de consultas analíticas frecuentes.

```
```
