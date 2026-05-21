from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import duckdb

app = FastAPI(title="Central Mayorista Dashboard")

GOLD_PATH = "lakehouse/gold"

def query(sql: str):
    con = duckdb.connect()
    result = con.execute(sql).fetchdf()
    con.close()
    return result.to_dict(orient="records")

@app.get("/")
def home():
    return FileResponse("public/index.html")

app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/api/kpis")
def kpis():
    sql = f"""
    SELECT
        COUNT(*) AS total_ventas,
        SUM(cantidad) AS unidades_vendidas,
        SUM(total_venta) AS ingresos_totales,
        AVG(total_venta) AS ticket_promedio
    FROM read_parquet('{GOLD_PATH}/fact_ventas.parquet')
    """
    return query(sql)[0]

@app.get("/api/ventas-mes")
def ventas_mes():
    sql = f"""
    SELECT
        t.anio,
        t.mes,
        t.nombre_mes,
        COUNT(*) AS total_ventas,
        SUM(f.total_venta) AS ingresos_totales
    FROM read_parquet('{GOLD_PATH}/fact_ventas.parquet') f
    JOIN read_parquet('{GOLD_PATH}/dim_tiempo.parquet') t
      ON f.tiempo_sk = t.tiempo_sk
    GROUP BY t.anio, t.mes, t.nombre_mes
    ORDER BY t.anio, t.mes
    """
    return query(sql)

@app.get("/api/top-productos")
def top_productos():
    sql = f"""
    SELECT
        p.nombre AS producto,
        SUM(f.total_venta) AS ingresos_totales
    FROM read_parquet('{GOLD_PATH}/fact_ventas.parquet') f
    JOIN read_parquet('{GOLD_PATH}/dim_producto.parquet') p
      ON f.producto_sk = p.producto_sk
    GROUP BY p.nombre
    ORDER BY ingresos_totales DESC
    LIMIT 10
    """
    return query(sql)

@app.get("/api/categorias")
def categorias():
    sql = f"""
    SELECT
        c.nombre_categoria AS categoria,
        SUM(f.total_venta) AS ingresos_totales
    FROM read_parquet('{GOLD_PATH}/fact_ventas.parquet') f
    JOIN read_parquet('{GOLD_PATH}/dim_categoria.parquet') c
      ON f.categoria_sk = c.categoria_sk
    GROUP BY c.nombre_categoria
    ORDER BY ingresos_totales DESC
    """
    return query(sql)

@app.get("/api/subregiones")
def subregiones():
    sql = f"""
    SELECT
        s.nombre_subregion AS subregion,
        SUM(f.total_venta) AS ingresos_totales
    FROM read_parquet('{GOLD_PATH}/fact_ventas.parquet') f
    JOIN read_parquet('{GOLD_PATH}/dim_subregion.parquet') s
      ON f.subregion_sk = s.subregion_sk
    GROUP BY s.nombre_subregion
    ORDER BY ingresos_totales DESC
    """
    return query(sql)

@app.get("/api/lakehouse-status")
def lakehouse_status():
    sql = f"""
    SELECT
        (SELECT COUNT(*) FROM read_parquet('{GOLD_PATH}/fact_ventas.parquet')) AS fact_ventas,
        (SELECT COUNT(*) FROM read_parquet('{GOLD_PATH}/dim_producto.parquet')) AS dim_producto,
        (SELECT COUNT(*) FROM read_parquet('{GOLD_PATH}/dim_tiempo.parquet')) AS dim_tiempo,
        (SELECT COUNT(*) FROM read_parquet('{GOLD_PATH}/dim_categoria.parquet')) AS dim_categoria,
        (SELECT COUNT(*) FROM read_parquet('{GOLD_PATH}/dim_subregion.parquet')) AS dim_subregion
    """
    return query(sql)[0]


@app.get("/api/scd-producto")
def scd_producto():
    sql = f"""
    SELECT
        version_producto,
        activo,
        COUNT(*) AS total_registros,
        MIN(valido_desde) AS valido_desde,
        MAX(valido_hasta) AS valido_hasta
    FROM read_parquet('{GOLD_PATH}/dim_producto.parquet')
    GROUP BY version_producto, activo
    ORDER BY version_producto
    """
    return query(sql)


@app.get("/api/calidad-silver")
def calidad_silver():
    return {
        "ventas_bronze": 435080,
        "ventas_silver": 105010,
        "duplicados_eliminados": 330070,
        "nulos_antes": 0,
        "nulos_despues": 0,
        "rango_fechas": "2026-01-01 a 2026-06-30"
    }


@app.get("/api/benchmark")
def benchmark():
    return {
        "postgres_ms": 168.72,
        "duckdb_ms": 16.71,
        "factor_mejora": 10.10
    }