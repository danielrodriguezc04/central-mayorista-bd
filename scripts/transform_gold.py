import pandas as pd
from pathlib import Path

SILVER = Path("lakehouse/silver")
GOLD = Path("lakehouse/gold")
GOLD.mkdir(parents=True, exist_ok=True)

# =========================
# Leer Silver
# =========================
productos = pd.read_parquet(SILVER / "productos_silver.parquet")
ventas = pd.read_parquet(SILVER / "ventas_silver.parquet")

# =========================
# DIM_TIEMPO
# =========================
fechas = pd.date_range(
    start=ventas["fecha_venta"].min().date(),
    end=ventas["fecha_venta"].max().date(),
    freq="D"
)

dim_tiempo = pd.DataFrame({
    "tiempo_sk": range(1, len(fechas) + 1),
    "fecha": fechas,
    "anio": fechas.year,
    "trimestre": fechas.quarter,
    "mes": fechas.month,
    "dia": fechas.day,
    "dia_semana": fechas.dayofweek,
    "nombre_mes": fechas.strftime("%B"),
    "fin_semana": fechas.dayofweek >= 5
})

dim_tiempo.to_parquet(GOLD / "dim_tiempo.parquet", index=False)

# =========================
# DIM_PRODUCTO
# =========================
dim_producto = productos[
    ["id", "nombre", "categoria", "precio"]
].copy()

dim_producto.insert(0, "producto_sk", range(1, len(dim_producto) + 1))
dim_producto.rename(columns={"id": "producto_id"}, inplace=True)

dim_producto.to_parquet(GOLD / "dim_producto.parquet", index=False)

# =========================
# DIM_CATEGORIA
# =========================
categorias = productos["categoria"].drop_duplicates().reset_index(drop=True)

dim_categoria = pd.DataFrame({
    "categoria_sk": range(1, len(categorias) + 1),
    "nombre_categoria": categorias
})

dim_categoria.to_parquet(GOLD / "dim_categoria.parquet", index=False)

# =========================
# DIM_SUBREGION
# =========================
subregiones = ventas["subregion"].drop_duplicates().reset_index(drop=True)

dim_subregion = pd.DataFrame({
    "subregion_sk": range(1, len(subregiones) + 1),
    "nombre_subregion": subregiones
})

dim_subregion.to_parquet(GOLD / "dim_subregion.parquet", index=False)

# =========================
# FACT_VENTAS
# =========================
fact = ventas.copy()

# fecha sola
fact["fecha"] = pd.to_datetime(fact["fecha_venta"]).dt.normalize()

# Join tiempo
fact = fact.merge(
    dim_tiempo[["tiempo_sk", "fecha"]],
    on="fecha",
    how="left"
)

# Join producto
fact = fact.merge(
    dim_producto[["producto_sk", "producto_id"]],
    left_on="producto_id",
    right_on="producto_id",
    how="left"
)

# Join categoria
fact = fact.merge(
    dim_categoria,
    left_on="categoria",
    right_on="nombre_categoria",
    how="left"
)

# Join subregion
fact = fact.merge(
    dim_subregion,
    left_on="subregion",
    right_on="nombre_subregion",
    how="left"
)

# Tabla final hechos
fact_ventas = fact[
    [
        "id",
        "tiempo_sk",
        "producto_sk",
        "categoria_sk",
        "subregion_sk",
        "cantidad",
        "precio_unitario",
        "total"
    ]
].copy()

fact_ventas.rename(columns={
    "id": "venta_id",
    "total": "total_venta"
}, inplace=True)

fact_ventas.to_parquet(GOLD / "fact_ventas.parquet", index=False)

# =========================
# Reporte
# =========================
print("=== ZONA GOLD GENERADA ===")
print(f"DIM_TIEMPO     : {len(dim_tiempo)}")
print(f"DIM_PRODUCTO   : {len(dim_producto)}")
print(f"DIM_CATEGORIA  : {len(dim_categoria)}")
print(f"DIM_SUBREGION  : {len(dim_subregion)}")
print(f"FACT_VENTAS    : {len(fact_ventas)}")