import time
import pandas as pd
import duckdb
from sqlalchemy import create_engine, text

PG_URL = "postgresql://admin:admin123@localhost:5433/central_mayorista"

pg_engine = create_engine(PG_URL)
duck = duckdb.connect()

duck.execute("""
CREATE OR REPLACE VIEW fact_ventas AS
SELECT * FROM read_parquet('lakehouse/gold/fact_ventas.parquet')
""")

duck.execute("""
CREATE OR REPLACE VIEW dim_tiempo AS
SELECT * FROM read_parquet('lakehouse/gold/dim_tiempo.parquet')
""")

QUERY_POSTGRES = text("""
    SELECT
        EXTRACT(YEAR FROM fecha_venta) AS anio,
        EXTRACT(MONTH FROM fecha_venta) AS mes,
        COUNT(*) AS total_ventas,
        SUM(cantidad) AS unidades_vendidas,
        SUM(total) AS ingresos_totales
    FROM ventas
    GROUP BY 1, 2
    ORDER BY 1, 2
""")

QUERY_DUCKDB = """
    SELECT
        t.anio,
        t.mes,
        COUNT(*) AS total_ventas,
        SUM(f.cantidad) AS unidades_vendidas,
        SUM(f.total_venta) AS ingresos_totales
    FROM fact_ventas f
    JOIN dim_tiempo t ON f.tiempo_sk = t.tiempo_sk
    GROUP BY t.anio, t.mes
    ORDER BY t.anio, t.mes
"""

inicio = time.time()
with pg_engine.connect() as conn:
    df_pg = pd.read_sql(QUERY_POSTGRES, conn)
tiempo_pg = (time.time() - inicio) * 1000

inicio = time.time()
df_duck = duck.execute(QUERY_DUCKDB).fetchdf()
tiempo_duck = (time.time() - inicio) * 1000

print("\n=== BENCHMARK POSTGRESQL VS DUCKDB ===")
print(f"PostgreSQL OLTP : {tiempo_pg:.2f} ms")
print(f"DuckDB Columnar : {tiempo_duck:.2f} ms")

if tiempo_duck > 0:
    print(f"Factor mejora   : {tiempo_pg / tiempo_duck:.2f}x")

print("\nResultado PostgreSQL:")
print(df_pg.to_string(index=False))

print("\nResultado DuckDB:")
print(df_duck.to_string(index=False))