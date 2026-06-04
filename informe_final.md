# Informe Técnico — Optimización de Consultas Analíticas en un Mini Lakehouse

## Central Mayorista

---

# 1. Resumen Ejecutivo

El presente proyecto tuvo como objetivo construir y optimizar un ecosistema analítico tipo Lakehouse para una central mayorista de productos agrícolas. El sistema integra fuentes operacionales en PostgreSQL y ClickHouse, implementando un pipeline completo compuesto por las zonas Bronze, Silver y Gold.

Inicialmente, el proyecto contaba con un pipeline funcional, pero presentaba limitaciones importantes relacionadas con el bajo volumen de datos, ausencia de Slowly Changing Dimensions (SCD), falta de benchmark cuantitativo y ausencia de visualizaciones analíticas.

Para solucionar estos problemas se realizaron varias mejoras:

* Generación de más de 105.000 registros sintéticos de ventas.
* Implementación de SCD Tipo 2 en la dimensión de productos.
* Construcción de reportes de calidad de datos en Silver.
* Desarrollo de un dashboard analítico conectado al modelo Gold.
* Implementación de benchmarks reales entre consultas baseline y optimizadas.
* Creación de una zona Gold optimizada mediante preagregaciones.

Los resultados mostraron mejoras entre 2.65x y 4.26x en los tiempos de consulta, demostrando que las optimizaciones analíticas reducen significativamente el trabajo del motor DuckDB.

El proyecto evolucionó desde una demostración académica básica hacia una arquitectura analítica más cercana a un escenario empresarial real.

---

# 2. Arquitectura General del Sistema

## 2.1 Arquitectura Lakehouse

El sistema fue diseñado utilizando una arquitectura Lakehouse basada en archivos Parquet y procesamiento analítico con DuckDB.

### Componentes principales

| Componente     | Función                            |
| -------------- | ---------------------------------- |
| PostgreSQL     | Fuente OLTP operacional            |
| ClickHouse     | Motor analítico complementario     |
| Bronze         | Datos extraídos sin transformación |
| Silver         | Limpieza y estandarización         |
| Gold           | Modelo dimensional estrella        |
| Gold Optimized | Tablas preagregadas                |
| DuckDB         | Motor analítico columnar           |
| FastAPI        | Backend para dashboard             |
| Dashboard Web  | Visualización analítica            |

---

## 2.2 Modelo Dimensional

El modelo estrella implementado está compuesto por:

### Tabla de hechos

* `fact_ventas`

### Dimensiones

* `dim_tiempo`
* `dim_producto`
* `dim_categoria`
* `dim_subregion`

La granularidad del modelo corresponde a:

> 1 fila = 1 venta realizada de un producto en una subregión y fecha específica.

---

# 3. Pipeline de Datos

---

## 3.1 Zona Bronze

La zona Bronze almacena los datos exactamente como fueron extraídos desde las fuentes operacionales.

### Características

* Datos sin transformación.
* Archivos Parquet inmutables.
* Extracción desde PostgreSQL y ClickHouse.

### Resultado

Se generaron archivos:

* `postgres_ventas.parquet`
* `clickhouse_ventas.parquet`
* `postgres_productos.parquet`
* `clickhouse_productos.parquet`

---

## 3.2 Zona Silver

La zona Silver realiza limpieza y control de calidad.

### Procesos aplicados

* Conversión de tipos.
* Eliminación de duplicados.
* Validación de nulos.
* Normalización de fechas.

### Reporte de calidad

| Métrica               | Resultado |
| --------------------- | --------- |
| Filas procesadas      | 105.010   |
| Duplicados eliminados | 0         |
| Nulos corregidos      | 0         |
| Fechas válidas        | Sí        |

---

## 3.3 Zona Gold

La zona Gold implementa el modelo dimensional estrella.

### Características

* Relaciones dimensionales.
* Claves sustitutas.
* Separación entre hechos y dimensiones.
* Persistencia en Parquet.

---

## 3.4 Implementación SCD Tipo 2

Se implementó SCD Tipo 2 en la dimensión `dim_producto`.

### Objetivo

Permitir mantener el histórico de cambios de precios de productos.

### Columnas utilizadas

| Campo            | Función            |
| ---------------- | ------------------ |
| valido_desde     | Inicio de vigencia |
| valido_hasta     | Fin de vigencia    |
| activo           | Registro actual    |
| version_producto | Versión histórica  |

### Resultado

El sistema puede conservar múltiples versiones históricas de un producto.

---

# 4. Dashboard Analítico

Se desarrolló un dashboard web conectado al backend FastAPI.

## Indicadores implementados

### KPIs

* Total ventas
* Ingresos totales
* Ticket promedio
* Unidades vendidas

### Visualizaciones

* Ventas por mes
* Top productos por ingresos
* Ingresos por categoría
* Ingresos por subregión

## Tecnologías utilizadas

| Tecnología  | Uso                  |
| ----------- | -------------------- |
| FastAPI     | API backend          |
| HTML/CSS/JS | Frontend             |
| Chart.js    | Gráficas             |
| DuckDB      | Consultas analíticas |

---

# 5. Diagnóstico Baseline

Se analizaron tres consultas analíticas principales utilizando `EXPLAIN ANALYZE`.

---

## Q1 — Ventas por mes

### Problema identificado

La consulta realizaba lectura completa de `fact_ventas.parquet` y agrupación sobre más de 105.000 filas.

### Operadores relevantes

* `READ_PARQUET`
* `HASH_JOIN`
* `HASH_GROUP_BY`

### Indicador detectado

Acceso secuencial sobre tabla de hechos.

---

## Q2 — Top productos por ingresos

### Problema identificado

La consulta recalculaba agrupaciones por producto en cada ejecución.

### Indicador detectado

Agrupaciones repetitivas sobre grandes volúmenes.

---

## Q3 — Ingresos por categoría

### Problema identificado

El motor procesaba toda la tabla de hechos para producir únicamente 5 filas finales.

### Indicador detectado

Costo innecesario de agregación.

---

# 6. Intervenciones Aplicadas

---

## 6.1 Estrategia de Optimización

Se implementó una estrategia de preagregación en la zona Gold.

### Archivos optimizados generados

```text
lakehouse/gold/optimized/
```

* `ventas_por_mes.parquet`
* `top_productos.parquet`
* `ingresos_categoria.parquet`

---

## 6.2 Justificación Técnica

La intervención reduce el trabajo del motor analítico porque:

* Evita recalcular agregaciones complejas.
* Reduce el número de filas procesadas.
* Minimiza operaciones `HASH_GROUP_BY`.
* Disminuye el costo CPU.
* Reduce tiempo de respuesta.

---

# 7. Benchmark de Optimización

| Query                       | Baseline (ms) | Optimizada (ms) | Factor mejora |
| --------------------------- | ------------: | --------------: | ------------: |
| Q1 — Ventas por mes         |         39.70 |            9.31 |         4.26x |
| Q2 — Top productos          |         28.81 |           10.89 |         2.65x |
| Q3 — Ingresos por categoría |         21.62 |            6.77 |         3.20x |

---

# 8. Benchmark PostgreSQL vs DuckDB

| Motor           |    Tiempo |
| --------------- | --------: |
| PostgreSQL OLTP | 178.89 ms |
| DuckDB Columnar |  23.73 ms |

## Factor de mejora

> 7.54x

## Interpretación

DuckDB mostró mejor rendimiento debido a:

* Lectura columnar.
* Procesamiento vectorizado.
* Ejecución sobre Parquet.
* Menor overhead de transacciones.

---

## Evaluación de Técnicas Alternativas de Optimización

Durante la fase de intervención se analizaron diferentes estrategias de optimización propuestas en la guía del laboratorio. Aunque la solución finalmente implementada fue la construcción de una capa Gold Optimized basada en preagregaciones, también se evaluaron otras alternativas con el fin de determinar su pertinencia dentro de la arquitectura Lakehouse desarrollada.

### Ordenamiento de archivos Parquet (Data Skipping)

Una de las técnicas consideradas fue el ordenamiento físico de los archivos Parquet para favorecer el mecanismo de Data Skipping de DuckDB. Esta estrategia resulta especialmente efectiva cuando las consultas aplican filtros selectivos sobre columnas temporales o de alta cardinalidad.

Sin embargo, las tres consultas analizadas (ventas por mes, top productos e ingresos por categoría) realizan agregaciones sobre la totalidad de la tabla de hechos y no incluyen filtros restrictivos en la cláusula WHERE. Debido a ello, DuckDB debe recorrer la mayor parte de los registros independientemente del orden físico del archivo.

Por esta razón se concluyó que el beneficio potencial sería limitado frente al costo adicional de reescribir los archivos Parquet.

### Actualización de estadísticas (ANALYZE)

También se evaluó la actualización de estadísticas mediante el comando ANALYZE.

Esta técnica es especialmente útil cuando el optimizador presenta estimaciones de cardinalidad incorrectas que derivan en planes de ejecución subóptimos.

Al revisar los planes EXPLAIN ANALYZE obtenidos durante el diagnóstico no se evidenciaron errores significativos de cardinalidad ni selección incorrecta de algoritmos de JOIN. Los operadores utilizados por DuckDB fueron consistentes con el volumen de datos disponible.

Debido a ello se consideró que la actualización de estadísticas no atacaba directamente el cuello de botella identificado.

### Particionamiento Hive-Style

Otra alternativa considerada fue la partición de los archivos Parquet utilizando una estructura Hive-Style basada en año y mes.

Esta técnica permite que DuckDB descarte directorios completos cuando las consultas incluyen filtros temporales específicos.

No obstante, las consultas seleccionadas para el taller no filtran por periodos concretos sino que procesan el conjunto completo de registros para construir agregaciones globales. En consecuencia, el particionamiento no habría reducido significativamente la cantidad de datos leídos.

Por esta razón la estrategia fue descartada para este escenario experimental.

### Creación de índices

Finalmente se evaluó la posibilidad de crear índices sobre columnas frecuentemente consultadas.

Sin embargo, la arquitectura implementada utiliza DuckDB sobre archivos Parquet, donde los mecanismos predominantes de optimización son el escaneo columnar, la compresión, el Data Skipping y las estadísticas internas. Adicionalmente, las consultas analizadas corresponden principalmente a procesos analíticos de agregación masiva y no a búsquedas puntuales altamente selectivas.

Por este motivo se concluyó que los índices no aportarían mejoras relevantes para las consultas estudiadas.

### Justificación de la técnica seleccionada

Tras evaluar las alternativas anteriores, se determinó que el principal costo de las consultas provenía de la lectura repetitiva de la tabla de hechos y del recálculo constante de agregaciones.

Por esta razón se implementó una capa Gold Optimized compuesta por tablas preagregadas específicas para cada consulta analítica. Esta estrategia elimina la necesidad de recalcular agregaciones complejas en tiempo de ejecución y reduce significativamente el volumen de datos procesado.

Los resultados obtenidos validan esta decisión, alcanzando factores de mejora entre 3.25x y 5.37x respecto a las consultas originales.

# Cambios recomendados para informe_final.md

## Evidencia de planes de ejecución

Los planes completos generados mediante `EXPLAIN ANALYZE` se encuentran almacenados dentro del repositorio en las siguientes rutas:

```text
docs/diagnostico_baseline/
docs/optimizacion/
```

Estos archivos contienen el árbol completo de operadores generado por DuckDB y fueron utilizados para identificar los operadores costosos, validar el diagnóstico inicial y comparar los resultados obtenidos después de la optimización.

Las evidencias incluyen tanto los planes baseline como los planes optimizados para las consultas Q1, Q2 y Q3.



# 9. Reflexión Arquitectural

El proyecto permitió comprender que un Lakehouse no depende únicamente del almacenamiento, sino de cómo se organizan y optimizan los datos analíticos.

Inicialmente, el sistema funcionaba correctamente, pero todavía se comportaba como una demostración pequeña. El incremento del volumen de datos permitió observar diferencias reales entre motores OLTP y motores analíticos columnares.

La implementación de SCD Tipo 2 mostró la importancia del manejo histórico en modelos dimensionales. Además, las preagregaciones demostraron que muchas optimizaciones analíticas consisten en reducir el trabajo repetitivo del motor.

También se evidenció que:

* El modelo estrella facilita consultas analíticas.
* Parquet reduce costos de almacenamiento y lectura.
* DuckDB es altamente eficiente para análisis local.
* Las zonas Bronze/Silver/Gold organizan claramente las responsabilidades del pipeline.

En un escenario empresarial real, futuras mejoras incluirían:

* Particionamiento Hive-style.
* Data skipping avanzado.
* Orquestación con Airflow.
* Incremental loads.
* Dashboard productivo con autenticación.
* Catálogo de metadatos.

---

# 10. Conclusiones

1. Se construyó exitosamente un pipeline Lakehouse funcional con zonas Bronze, Silver y Gold.

2. La implementación de SCD Tipo 2 permitió mantener historial de productos y cambios de precios.

3. El aumento del volumen de datos permitió realizar benchmarks analíticos más representativos.

4. DuckDB mostró ventajas significativas frente a PostgreSQL para consultas agregadas sobre Parquet.

5. Las preagregaciones en Gold optimizado redujeron considerablemente los tiempos de consulta.

6. El dashboard desarrollado permitió visualizar el valor analítico del modelo dimensional.

7. El proyecto evolucionó desde una prueba académica básica hacia una arquitectura analítica mucho más cercana a un entorno real de negocio.

---

# 11. Tecnologías Utilizadas

| Tecnología     | Uso                  |
| -------------- | -------------------- |
| Python         | Pipeline ETL         |
| PostgreSQL     | OLTP                 |
| ClickHouse     | Analítica            |
| DuckDB         | Consultas analíticas |
| Pandas         | Transformaciones     |
| Parquet        | Almacenamiento       |
| FastAPI        | Backend              |
| HTML/CSS/JS    | Frontend             |
| Docker Compose | Contenedores         |

---

## Metodología de medición ampliada

Para responder a la observación metodológica, se amplió el reporte de medición incluyendo no solo la mediana, sino también los tiempos crudos, mínimo, máximo, promedio y desviación estándar.

Cada consulta fue ejecutada bajo el siguiente protocolo:

1. Tres ejecuciones iniciales de warm-up para estabilizar la caché de DuckDB.
2. Cinco ejecuciones medidas con `time.perf_counter()`.
3. Cálculo de mínimo, máximo, media, mediana y desviación estándar.

La mediana se conserva como métrica principal porque reduce el efecto de valores extremos, mientras que la desviación estándar permite observar la estabilidad de las mediciones.

Los resultados muestran que las consultas optimizadas no solo fueron más rápidas, sino también más estables. Por ejemplo, Q1 pasó de una desviación estándar de 2.94 ms en baseline a 0.48 ms en la versión optimizada.

| Query | Escenario  |                 Tiempos crudos (ms) |   Mín |   Máx | Media | Mediana | Desv. estándar |
| ----- | ---------- | ----------------------------------: | ----: | ----: | ----: | ------: | -------------: |
| Q1    | Baseline   | [28.33, 23.67, 28.69, 29.93, 31.51] | 23.67 | 31.51 | 28.43 |   28.69 |           2.94 |
| Q1    | Optimizada |      [6.25, 6.16, 6.01, 5.16, 6.36] |  5.16 |  6.36 |  5.99 |    6.16 |           0.48 |
| Q2    | Baseline   | [33.21, 30.34, 34.62, 34.48, 32.33] | 30.34 | 34.62 | 33.00 |   33.21 |           1.76 |
| Q2    | Optimizada |      [6.18, 6.05, 6.74, 7.28, 4.82] |  4.82 |  7.28 |  6.22 |    6.18 |           0.92 |
| Q3    | Baseline   | [21.68, 19.40, 22.57, 20.55, 20.55] | 19.40 | 22.57 | 20.95 |   20.55 |           1.21 |
| Q3    | Optimizada |      [9.42, 6.41, 6.00, 6.32, 5.94] |  5.94 |  9.42 |  6.82 |    6.32 |           1.47 |

| Query | Baseline mediana | Optimizada mediana | Factor |
| ----- | ---------------: | -----------------: | -----: |
| Q1    |         28.69 ms |            6.16 ms |  4.66x |
| Q2    |         33.21 ms |            6.18 ms |  5.37x |
| Q3    |         20.55 ms |            6.32 ms |  3.25x |


# 12. Repositorio

Repositorio GitHub del proyecto:

```text
https://github.com/danielrodriguezc04/central-mayorista-bd
```
