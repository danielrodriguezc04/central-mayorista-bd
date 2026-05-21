import duckdb
import time
from pathlib import Path
from statistics import median

DOCS = Path("docs/optimizacion")
DOCS.mkdir(parents=True, exist_ok=True)

con = duckdb.connect()

QUERIES = {
    "q1_ventas_por_mes": {
        "baseline": """
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
        "optimizada": """
            SELECT *
            FROM read_parquet('lakehouse/gold/optimized/ventas_por_mes.parquet')
            ORDER BY anio, mes
        """
    },

    "q2_top_productos": {
        "baseline": """
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
        "optimizada": """
            SELECT
                nombre AS producto,
                categoria,
                unidades_vendidas,
                ingresos_totales
            FROM read_parquet('lakehouse/gold/optimized/top_productos.parquet')
            ORDER BY ingresos_totales DESC
            LIMIT 10
        """
    },

    "q3_ingresos_categoria": {
        "baseline": """
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
        """,
        "optimizada": """
            SELECT *
            FROM read_parquet('lakehouse/gold/optimized/ingresos_categoria.parquet')
            ORDER BY ingresos_totales DESC
        """
    }
}


def medir(query):
    for _ in range(3):
        con.execute(query).fetchall()

    tiempos = []
    for _ in range(5):
        inicio = time.perf_counter()
        con.execute(query).fetchall()
        tiempos.append((time.perf_counter() - inicio) * 1000)

    tiempos = sorted(tiempos)

    return {
        "mediana": median(tiempos),
        "min": tiempos[0],
        "max": tiempos[-1],
        "tiempos": tiempos
    }


def explain(nombre, tipo, query):
    plan = con.execute(f"EXPLAIN ANALYZE {query}").fetchdf().to_string(index=False)
    ruta = DOCS / f"{nombre}_{tipo}_plan.txt"
    ruta.write_text(plan, encoding="utf-8")


def main():
    resultados = []

    for nombre, queries in QUERIES.items():
        print(f"\nProcesando {nombre}")

        baseline = medir(queries["baseline"])
        optimizada = medir(queries["optimizada"])

        explain(nombre, "baseline", queries["baseline"])
        explain(nombre, "optimizada", queries["optimizada"])

        factor = baseline["mediana"] / optimizada["mediana"]

        resultados.append({
            "query": nombre,
            "baseline_ms": baseline["mediana"],
            "optimizada_ms": optimizada["mediana"],
            "factor": factor
        })

        print(f"Baseline   : {baseline['mediana']:.2f} ms")
        print(f"Optimizada : {optimizada['mediana']:.2f} ms")
        print(f"Mejora     : {factor:.2f}x")

    lineas = [
        "# Benchmark de Optimización — Taller 4",
        "",
        "| Query | Baseline (ms) | Optimizada (ms) | Factor mejora |",
        "|---|---:|---:|---:|"
    ]

    for r in resultados:
        lineas.append(
            f"| {r['query']} | {r['baseline_ms']:.2f} | {r['optimizada_ms']:.2f} | {r['factor']:.2f}x |"
        )

    salida = "\n".join(lineas)
    (DOCS / "benchmark_optimizacion.md").write_text(salida, encoding="utf-8")

    print("\nArchivo generado:")
    print(DOCS / "benchmark_optimizacion.md")


if __name__ == "__main__":
    main()