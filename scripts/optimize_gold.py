import pandas as pd
from pathlib import Path

GOLD = Path("lakehouse/gold")
OPTIMIZED = Path("lakehouse/gold/optimized")
OPTIMIZED.mkdir(parents=True, exist_ok=True)

fact = pd.read_parquet(GOLD / "fact_ventas.parquet")
dim_tiempo = pd.read_parquet(GOLD / "dim_tiempo.parquet")
dim_producto = pd.read_parquet(GOLD / "dim_producto.parquet")
dim_categoria = pd.read_parquet(GOLD / "dim_categoria.parquet")

# Q1 optimizada: ventas por mes
ventas_mes = (
    fact.merge(dim_tiempo[["tiempo_sk", "anio", "mes", "nombre_mes"]], on="tiempo_sk", how="left")
    .groupby(["anio", "mes", "nombre_mes"], as_index=False)
    .agg(
        total_ventas=("venta_id", "count"),
        unidades_vendidas=("cantidad", "sum"),
        ingresos_totales=("total_venta", "sum"),
        ticket_promedio=("total_venta", "mean"),
    )
    .sort_values(["anio", "mes"])
)

ventas_mes.to_parquet(OPTIMIZED / "ventas_por_mes.parquet", index=False)

# Q2 optimizada: top productos
top_productos = (
    fact.merge(dim_producto[["producto_sk", "nombre", "categoria"]], on="producto_sk", how="left")
    .groupby(["nombre", "categoria"], as_index=False)
    .agg(
        unidades_vendidas=("cantidad", "sum"),
        ingresos_totales=("total_venta", "sum"),
    )
    .sort_values("ingresos_totales", ascending=False)
)

top_productos.to_parquet(OPTIMIZED / "top_productos.parquet", index=False)

# Q3 optimizada: ingresos por categoría
ingresos_categoria = (
    fact.merge(dim_categoria[["categoria_sk", "nombre_categoria"]], on="categoria_sk", how="left")
    .groupby(["nombre_categoria"], as_index=False)
    .agg(
        total_ventas=("venta_id", "count"),
        unidades_vendidas=("cantidad", "sum"),
        ingresos_totales=("total_venta", "sum"),
    )
    .sort_values("ingresos_totales", ascending=False)
)

ingresos_categoria.to_parquet(OPTIMIZED / "ingresos_categoria.parquet", index=False)

print("=== GOLD OPTIMIZADO GENERADO ===")
print(f"ventas_por_mes       : {len(ventas_mes)} filas")
print(f"top_productos        : {len(top_productos)} filas")
print(f"ingresos_categoria   : {len(ingresos_categoria)} filas")
print(f"Ruta                 : {OPTIMIZED}")