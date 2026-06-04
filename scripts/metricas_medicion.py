import duckdb
import time
import statistics

con = duckdb.connect()

QUERIES = {
    "Q1_BASELINE": """
        SELECT t.anio, t.mes, t.nombre_mes,
               COUNT(*) AS total_ventas,
               SUM(f.cantidad) AS unidades_vendidas,
               SUM(f.total_venta) AS ingresos_totales
        FROM read_parquet('lakehouse/gold/fact_ventas.parquet') f
        JOIN read_parquet('lakehouse/gold/dim_tiempo.parquet') t
          ON f.tiempo_sk = t.tiempo_sk
        GROUP BY t.anio, t.mes, t.nombre_mes
        ORDER BY t.anio, t.mes
    """,

    "Q1_OPTIMIZADA": """
        SELECT *
        FROM read_parquet('lakehouse/gold/optimized/ventas_por_mes.parquet')
    """,

    "Q2_BASELINE": """
        SELECT p.nombre AS producto,
               p.categoria,
               SUM(f.cantidad) AS unidades_vendidas,
               SUM(f.total_venta) AS ingresos_totales
        FROM read_parquet('lakehouse/gold/fact_ventas.parquet') f
        JOIN read_parquet('lakehouse/gold/dim_producto.parquet') p
          ON f.producto_sk = p.producto_sk
        GROUP BY p.nombre, p.categoria
        ORDER BY ingresos_totales DESC
        LIMIT 10
    """,

    "Q2_OPTIMIZADA": """
        SELECT *
        FROM read_parquet('lakehouse/gold/optimized/top_productos.parquet')
    """,

    "Q3_BASELINE": """
        SELECT c.nombre_categoria,
               COUNT(*) AS total_ventas,
               SUM(f.cantidad) AS unidades_vendidas,
               SUM(f.total_venta) AS ingresos_totales
        FROM read_parquet('lakehouse/gold/fact_ventas.parquet') f
        JOIN read_parquet('lakehouse/gold/dim_categoria.parquet') c
          ON f.categoria_sk = c.categoria_sk
        GROUP BY c.nombre_categoria
    """,

    "Q3_OPTIMIZADA": """
        SELECT *
        FROM read_parquet('lakehouse/gold/optimized/ingresos_categoria.parquet')
    """
}


def medir(query):
    for _ in range(3):
        con.execute(query).fetchall()

    tiempos = []

    for _ in range(5):
        inicio = time.perf_counter()
        con.execute(query).fetchall()
        fin = time.perf_counter()

        tiempos.append((fin - inicio) * 1000)

    return {
        "tiempos": [round(x, 2) for x in tiempos],
        "min": round(min(tiempos), 2),
        "max": round(max(tiempos), 2),
        "media": round(statistics.mean(tiempos), 2),
        "mediana": round(statistics.median(tiempos), 2),
        "std": round(statistics.stdev(tiempos), 2),
    }


print("\n===== RESULTADOS =====\n")

for nombre, query in QUERIES.items():
    r = medir(query)

    print(f"\n{nombre}")
    print("-" * 50)
    print("Tiempos :", r["tiempos"])
    print("Min     :", r["min"], "ms")
    print("Max     :", r["max"], "ms")
    print("Media   :", r["media"], "ms")
    print("Mediana :", r["mediana"], "ms")
    print("Std Dev :", r["std"], "ms")