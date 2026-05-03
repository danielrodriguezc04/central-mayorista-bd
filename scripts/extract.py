import pandas as pd
from sqlalchemy import create_engine
import clickhouse_connect
from pathlib import Path
from datetime import datetime

BRONZE = Path("lakehouse/bronze")
BRONZE.mkdir(parents=True, exist_ok=True)

fecha_extraccion = datetime.now().strftime("%Y%m%d_%H%M%S")

PG_URL = "postgresql://admin:admin123@localhost:5433/central_mayorista"

pg_engine = create_engine(PG_URL)

clickhouse = clickhouse_connect.get_client(
    host="localhost",
    port=8123,
    username="admin",
    password="admin123",
)

def guardar_parquet(df: pd.DataFrame, nombre: str, fuente: str):
    df["_extraido_en"] = datetime.now()
    df["_fuente"] = fuente

    ruta = BRONZE / f"{nombre}_{fecha_extraccion}.parquet"
    df.to_parquet(ruta, index=False)

    print(f"{nombre}: {len(df)} filas guardadas en {ruta}")

def extraer_postgres():
    print("\n=== Extrayendo desde PostgreSQL ===")

    productos = pd.read_sql("""
        SELECT id, nombre, categoria, subregion, precio, stock, fecha_registro
        FROM productos
        ORDER BY id
    """, pg_engine)

    ventas = pd.read_sql("""
        SELECT
            v.id,
            v.producto_id,
            p.nombre AS producto,
            p.categoria,
            v.subregion,
            v.cantidad,
            v.precio_unitario,
            v.total,
            v.fecha_venta
        FROM ventas v
        JOIN productos p ON p.id = v.producto_id
        ORDER BY v.id
    """, pg_engine)

    guardar_parquet(productos, "postgres_productos", "postgresql")
    guardar_parquet(ventas, "postgres_ventas", "postgresql")

def extraer_clickhouse():
    print("\n=== Extrayendo desde ClickHouse ===")

    productos_result = clickhouse.query("""
        SELECT id, nombre, categoria, subregion, precio, stock, fecha_registro
        FROM central_analytics.productos_analytics
        ORDER BY id
    """)

    productos = pd.DataFrame(
        productos_result.result_rows,
        columns=productos_result.column_names
    )

    ventas_result = clickhouse.query("""
        SELECT
            id,
            producto_id,
            producto,
            categoria,
            subregion,
            cantidad,
            precio_unitario,
            total,
            fecha_venta
        FROM central_analytics.ventas_analytics
        ORDER BY id
    """)

    ventas = pd.DataFrame(
        ventas_result.result_rows,
        columns=ventas_result.column_names
    )

    guardar_parquet(productos, "clickhouse_productos", "clickhouse")
    guardar_parquet(ventas, "clickhouse_ventas", "clickhouse")

if __name__ == "__main__":
    extraer_postgres()
    extraer_clickhouse()
    print("\nZona Bronze generada correctamente.")