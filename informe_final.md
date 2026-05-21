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

# 12. Repositorio

Repositorio GitHub del proyecto:

```text
https://github.com/danielrodriguezc04/central-mayorista-bd
```
