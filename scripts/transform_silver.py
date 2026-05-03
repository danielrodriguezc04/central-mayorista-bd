import pandas as pd
import duckdb
from pathlib import Path

BRONZE = Path("lakehouse/bronze")
SILVER = Path("lakehouse/silver")
SILVER.mkdir(parents=True, exist_ok=True)

con = duckdb.connect()

def limpiar_productos():
    df_raw = con.execute("""
        SELECT *
        FROM read_parquet('lakehouse/bronze/postgres_productos_*.parquet')
    """).fetchdf()

    df = df_raw.copy()

    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df["nombre"] = df["nombre"].astype(str).str.strip().str.title()
    df["categoria"] = df["categoria"].astype(str).str.strip().str.title()
    df["subregion"] = df["subregion"].astype(str).str.strip().str.title()
    df["precio"] = pd.to_numeric(df["precio"], errors="coerce")
    df["stock"] = pd.to_numeric(df["stock"], errors="coerce")
    df["fecha_registro"] = pd.to_datetime(df["fecha_registro"], errors="coerce")

    nulos_antes = df.isnull().sum().sum()

    df["categoria"] = df["categoria"].fillna("Sin Categoria")
    df["subregion"] = df["subregion"].fillna("Sin Subregion")
    df = df.dropna(subset=["id", "nombre", "precio", "fecha_registro"])

    filas_antes = len(df)
    df = df.drop_duplicates(subset=["id"])

    df.to_parquet(SILVER / "productos_silver.parquet", index=False)

    print("\n=== PRODUCTOS SILVER ===")
    print(f"Filas Bronze originales : {len(df_raw)}")
    print(f"Filas Silver resultantes: {len(df)}")
    print(f"Duplicados eliminados   : {filas_antes - len(df)}")
    print(f"Nulos antes/después     : {nulos_antes} -> {df.isnull().sum().sum()}")

def limpiar_ventas():
    df_raw = con.execute("""
        SELECT *
        FROM read_parquet('lakehouse/bronze/postgres_ventas_*.parquet')
    """).fetchdf()

    df = df_raw.copy()

    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df["producto_id"] = pd.to_numeric(df["producto_id"], errors="coerce")
    df["producto"] = df["producto"].astype(str).str.strip().str.title()
    df["categoria"] = df["categoria"].astype(str).str.strip().str.title()
    df["subregion"] = df["subregion"].astype(str).str.strip().str.title()
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
    df["precio_unitario"] = pd.to_numeric(df["precio_unitario"], errors="coerce")
    df["total"] = pd.to_numeric(df["total"], errors="coerce")
    df["fecha_venta"] = pd.to_datetime(df["fecha_venta"], errors="coerce")

    nulos_antes = df.isnull().sum().sum()

    df = df.dropna(
        subset=[
            "id",
            "producto_id",
            "producto",
            "categoria",
            "subregion",
            "cantidad",
            "precio_unitario",
            "total",
            "fecha_venta",
        ]
    )

    df = df[df["cantidad"] > 0]
    df = df[df["precio_unitario"] > 0]
    df = df[df["total"] > 0]

    filas_antes = len(df)
    df = df.drop_duplicates(subset=["id"])

    df.to_parquet(SILVER / "ventas_silver.parquet", index=False)

    print("\n=== VENTAS SILVER ===")
    print(f"Filas Bronze originales : {len(df_raw)}")
    print(f"Filas Silver resultantes: {len(df)}")
    print(f"Duplicados eliminados   : {filas_antes - len(df)}")
    print(f"Nulos antes/después     : {nulos_antes} -> {df.isnull().sum().sum()}")
    print(f"Rango de fechas         : {df['fecha_venta'].min()} -> {df['fecha_venta'].max()}")
    print(f"Total ventas            : ${df['total'].sum():,.2f}")

if __name__ == "__main__":
    limpiar_productos()
    limpiar_ventas()
    print("\nZona Silver generada correctamente.")