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
# DIM_PRODUCTO con SCD Tipo 2
# =========================
dim_producto_base = productos[
    ["id", "nombre", "categoria", "precio"]
].copy()

dim_producto_base.rename(columns={"id": "producto_id"}, inplace=True)

# Versión actual del producto
dim_producto_actual = dim_producto_base.copy()
dim_producto_actual["version_producto"] = 2
dim_producto_actual["valido_desde"] = pd.Timestamp("2026-04-01")
dim_producto_actual["valido_hasta"] = pd.Timestamp("9999-12-31")
dim_producto_actual["activo"] = True

# Versión histórica simulada
dim_producto_historico = dim_producto_base.copy()
dim_producto_historico["precio"] = (dim_producto_historico["precio"] * 0.90).round(2)
dim_producto_historico["version_producto"] = 1
dim_producto_historico["valido_desde"] = pd.Timestamp("2026-01-01")
dim_producto_historico["valido_hasta"] = pd.Timestamp("2026-03-31 23:59:59")
dim_producto_historico["activo"] = False

dim_producto = pd.concat(
    [dim_producto_historico, dim_producto_actual],
    ignore_index=True
)

dim_producto.insert(0, "producto_sk", range(1, len(dim_producto) + 1))

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

fact["fecha_venta"] = pd.to_datetime(fact["fecha_venta"])
fact["fecha"] = fact["fecha_venta"].dt.normalize()

# Join tiempo
fact = fact.merge(
    dim_tiempo[["tiempo_sk", "fecha"]],
    on="fecha",
    how="left"
)

# Join producto con SCD Tipo 2
fact = fact.merge(
    dim_producto[
        [
            "producto_sk",
            "producto_id",
            "valido_desde",
            "valido_hasta",
            "version_producto"
        ]
    ],
    on="producto_id",
    how="left"
)

fact = fact[
    (fact["fecha_venta"] >= fact["valido_desde"]) &
    (fact["fecha_venta"] <= fact["valido_hasta"])
].copy()

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
        "total",
        "version_producto"
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