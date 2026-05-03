import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

PG_URL = "postgresql://admin:admin123@localhost:5433/central_mayorista"

engine = create_engine(PG_URL)

TOTAL_VENTAS = 5000

with engine.begin() as conn:
    productos = conn.execute(text("""
        SELECT id, precio, subregion
        FROM productos
        ORDER BY id
    """)).fetchall()

    if not productos:
        raise Exception("No existen productos en PostgreSQL.")

    for _ in range(TOTAL_VENTAS):
        producto = random.choice(productos)

        producto_id = producto.id
        precio_unitario = float(producto.precio)
        subregion = producto.subregion

        cantidad = random.randint(1, 80)
        total = cantidad * precio_unitario

        fecha_base = datetime(2026, 1, 1)
        fecha_venta = fecha_base + timedelta(
            days=random.randint(0, 120),
            hours=random.randint(6, 18),
            minutes=random.randint(0, 59)
        )

        conn.execute(text("""
            INSERT INTO ventas (
                producto_id,
                cantidad,
                precio_unitario,
                total,
                subregion,
                fecha_venta
            )
            VALUES (
                :producto_id,
                :cantidad,
                :precio_unitario,
                :total,
                :subregion,
                :fecha_venta
            )
        """), {
            "producto_id": producto_id,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "total": total,
            "subregion": subregion,
            "fecha_venta": fecha_venta
        })

print(f"Datos sintéticos generados correctamente: {TOTAL_VENTAS} ventas nuevas.")