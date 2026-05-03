import pandas as pd
from sqlalchemy import create_engine
import clickhouse_connect

PG_URL = "postgresql://admin:admin123@localhost:5433/central_mayorista"

pg = create_engine(PG_URL)

ch = clickhouse_connect.get_client(
    host="localhost",
    port=8123,
    username="admin",
    password="admin123"
)

productos = pd.read_sql("""
    SELECT id, nombre, categoria, subregion, precio, stock, fecha_registro
    FROM productos
    ORDER BY id
""", pg)

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
""", pg)

ch.command("TRUNCATE TABLE central_analytics.productos_analytics")
ch.command("TRUNCATE TABLE central_analytics.ventas_analytics")

ch.insert_df("central_analytics.productos_analytics", productos)
ch.insert_df("central_analytics.ventas_analytics", ventas)

print(f"Productos cargados en ClickHouse: {len(productos)}")
print(f"Ventas cargadas en ClickHouse: {len(ventas)}")