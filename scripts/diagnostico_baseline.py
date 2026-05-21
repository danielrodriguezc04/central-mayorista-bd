import duckdb
import time
from pathlib import Path
from statistics import median

DOCS = Path("docs/diagnostico_baseline")
DOCS.mkdir(parents=True, exist_ok=True)

GOLD = "lakehouse/gold"

QUERIES = {
    "q1_ventas_por_mes": """
        SELECT
            t.anio,
            t.mes,
            t.nombre_mes,
            COUNT(*) AS total_ventas,
            SUM(f.cantidad) AS unidades_vendidas,
            SUM(f.total_venta) AS ingresos_totales,
            AVG(f.total_venta) AS ticket_promedio
        FROM read_parquet('lakehouse/gold/fact_ventas.parquet') f
        JOIN read_parquet('lakehouse/gold/dim_tiempo.parquet') t
            ON f.tiempo_sk = t.tiempo_sk
        GROUP BY t.anio, t.mes, t.nombre_mes
        ORDER BY t.anio, t.mes
    """,

    "q2_top_productos": """
        SELECT
            p.nombre AS producto,
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

    "q3_ingresos_categoria": """
        SELECT
            c.nombre_categoria,
            COUNT(*) AS total_ventas,
            SUM(f.cantidad) AS unidades_vendidas,
            SUM(f.total_venta) AS ingresos_totales
        FROM read_parquet('lakehouse/gold/fact_ventas.parquet') f
        JOIN read_parquet('lakehouse/gold/dim_categoria.parquet') c
            ON f.categoria_sk = c.categoria_sk
        GROUP BY c.nombre_categoria
        ORDER BY ingresos_totales DESC
    """
}


def guardar_texto(nombre_archivo: str, contenido: str):
    ruta = DOCS / nombre_archivo
    ruta.write_text(contenido, encoding="utf-8")
    print(f"Archivo generado: {ruta}")


def medir_tiempos(con, query: str):
    # Warm-up
    for _ in range(3):
        con.execute(query).fetchall()

    tiempos = []

    for _ in range(5):
        inicio = time.perf_counter()
        con.execute(query).fetchall()
        fin = time.perf_counter()
        tiempos.append((fin - inicio) * 1000)

    tiempos_ordenados = sorted(tiempos)

    return {
        "min": tiempos_ordenados[0],
        "max": tiempos_ordenados[-1],
        "mediana": median(tiempos_ordenados),
        "tiempos": tiempos_ordenados
    }


def main():
    con = duckdb.connect()

    for nombre, query in QUERIES.items():
        print(f"\nProcesando {nombre}...")

        explain = con.execute(f"EXPLAIN ANALYZE {query}").fetchdf()

        plan_texto = explain.to_string(index=False)
        guardar_texto(f"{nombre}_plan.txt", plan_texto)

        tiempos = medir_tiempos(con, query)

        contenido_tiempos = f"""
QUERY: {nombre}

Mediciones con warm-up previo:
- Warm-up: 3 ejecuciones
- Mediciones: 5 ejecuciones

Tiempos medidos (ms):
{[round(t, 2) for t in tiempos["tiempos"]]}

Mediana baseline: {tiempos["mediana"]:.2f} ms
Mínimo: {tiempos["min"]:.2f} ms
Máximo: {tiempos["max"]:.2f} ms
"""

        guardar_texto(f"{nombre}_tiempos.txt", contenido_tiempos)

    con.close()

    print("\nDiagnóstico baseline generado correctamente.")


if __name__ == "__main__":
    main()