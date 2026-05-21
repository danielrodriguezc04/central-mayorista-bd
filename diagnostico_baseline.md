# Diagnóstico Baseline — Taller 4

## Objetivo

El objetivo de esta fase fue leer e interpretar los planes de ejecución de tres consultas analíticas representativas del modelo Gold construido en el Taller 3.

Según el Taller 4, esta fase busca identificar el operador costoso, medir el tiempo baseline y describir el problema usando vocabulario técnico del plan de ejecución.

## Consultas analizadas

Se seleccionaron tres consultas analíticas:

1. Q1 — Ventas por mes  
2. Q2 — Top productos por ingresos  
3. Q3 — Ingresos por categoría  

## Metodología de medición

Para cada consulta se ejecutó:

- `EXPLAIN ANALYZE`
- 3 ejecuciones de warm-up
- 5 mediciones reales
- cálculo de la mediana como tiempo baseline

## Tabla de diagnóstico baseline

| Query | Tiempo baseline mediana | Motor usado | Operador más costoso | Problema identificado | Indicador |
|---|---:|---|---|---|---|
| Q1 — Ventas por mes | 21.59 ms | DuckDB sobre Parquet | HASH_GROUP_BY | La consulta agrupa 105.010 filas por año y mes. El costo principal está en la agregación, no en el JOIN. | Indicador 1 — lectura completa de fact_ventas para agregación |
| Q2 — Top productos por ingresos | 18.13 ms | DuckDB sobre Parquet | HASH_GROUP_BY | La consulta debe agrupar todas las ventas por producto antes de aplicar el TOP 10. El operador TOP_N es eficiente, pero ocurre después de procesar toda la tabla de hechos. | Indicador 1 — lectura completa de fact_ventas para agregación |
| Q3 — Ingresos por categoría | 13.52 ms | DuckDB sobre Parquet | HASH_GROUP_BY | La consulta agrupa las ventas por categoría. Aunque la dimensión es pequeña, la tabla de hechos completa debe leerse para calcular los ingresos. | Indicador 1 — lectura completa de fact_ventas para agregación |

## Lectura técnica del plan

En las tres consultas, DuckDB utiliza `READ_PARQUET` para leer los archivos de la zona Gold. Posteriormente realiza `HASH_JOIN` con las dimensiones correspondientes y luego aplica `HASH_GROUP_BY` para calcular las métricas agregadas.

El problema principal no está en los JOIN, ya que las dimensiones son pequeñas y el motor utiliza `HASH_JOIN`, que es adecuado para este caso. El mayor costo se concentra en el agrupamiento de la tabla de hechos.

## Conclusión del diagnóstico

El diagnóstico muestra que las consultas son correctas y el motor utiliza operadores adecuados. Sin embargo, todas las consultas deben leer y agrupar la tabla `fact_ventas`, que contiene más de 100.000 registros.

Por lo tanto, la intervención recomendada es crear agregaciones precomputadas en la zona Gold, reduciendo la necesidad de calcular los mismos agrupamientos en cada ejecución.