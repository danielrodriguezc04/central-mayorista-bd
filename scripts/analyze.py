import duckdb
import time

con = duckdb.connect()

con.execute("""
CREATE OR REPLACE VIEW fact_ventas AS
SELECT * FROM read_parquet('lakehouse/gold/fact_ventas.parquet')
""")

con.execute("""
CREATE OR REPLACE VIEW dim_tiempo AS
SELECT * FROM read_parquet('lakehouse/gold/dim_tiempo.parquet')
""")

con.execute("""
CREATE OR REPLACE VIEW dim_producto AS
SELECT * FROM read_parquet('lakehouse/gold/dim_producto.parquet')
""")

con.execute("""
CREATE OR REPLACE VIEW dim_categoria AS
SELECT * FROM read_parquet('lakehouse/gold/dim_categoria.parquet')
""")

con.execute("""
CREATE OR REPLACE VIEW dim_subregion AS
SELECT * FROM read_parquet('lakehouse/gold/dim_subregion.parquet')
""")

queries = {
    "1. Ventas por mes": """
        SELECT
            t.anio,
            t.mes,
            t.nombre_mes,
            COUNT(*) AS total_ventas,
            SUM(f.cantidad) AS unidades_vendidas,
            SUM(f.total_venta) AS ingresos_totales,
            AVG(f.total_venta) AS ticket_promedio
        FROM fact_ventas f
        JOIN dim_tiempo t ON f.tiempo_sk = t.tiempo_sk
        GROUP BY t.anio, t.mes, t.nombre_mes
        ORDER BY t.anio, t.mes
    """,

    "2. Top productos por ingresos": """
        SELECT
            p.nombre AS producto,
            p.categoria,
            SUM(f.cantidad) AS unidades_vendidas,
            SUM(f.total_venta) AS ingresos_totales
        FROM fact_ventas f
        JOIN dim_producto p ON f.producto_sk = p.producto_sk
        GROUP BY p.nombre, p.categoria
        ORDER BY ingresos_totales DESC
        LIMIT 10
    """,

    "3. Ingresos por categoría": """
        SELECT
            c.nombre_categoria,
            COUNT(*) AS total_ventas,
            SUM(f.cantidad) AS unidades_vendidas,
            SUM(f.total_venta) AS ingresos_totales
        FROM fact_ventas f
        JOIN dim_categoria c ON f.categoria_sk = c.categoria_sk
        GROUP BY c.nombre_categoria
        ORDER BY ingresos_totales DESC
    """,

    "4. Ventas por subregión": """
        SELECT
            s.nombre_subregion,
            COUNT(*) AS total_ventas,
            SUM(f.cantidad) AS unidades_vendidas,
            SUM(f.total_venta) AS ingresos_totales
        FROM fact_ventas f
        JOIN dim_subregion s ON f.subregion_sk = s.subregion_sk
        GROUP BY s.nombre_subregion
        ORDER BY ingresos_totales DESC
    """,

    "5. Ticket promedio por categoría": """
        SELECT
            c.nombre_categoria,
            AVG(f.total_venta) AS ticket_promedio,
            MIN(f.total_venta) AS venta_minima,
            MAX(f.total_venta) AS venta_maxima
        FROM fact_ventas f
        JOIN dim_categoria c ON f.categoria_sk = c.categoria_sk
        GROUP BY c.nombre_categoria
        ORDER BY ticket_promedio DESC
    """
}

for nombre, query in queries.items():
    inicio = time.time()
    resultado = con.execute(query).fetchdf()
    tiempo_ms = (time.time() - inicio) * 1000

    print(f"\n=== {nombre} ===")
    print(f"Tiempo DuckDB: {tiempo_ms:.2f} ms")
    print(resultado.to_string(index=False))