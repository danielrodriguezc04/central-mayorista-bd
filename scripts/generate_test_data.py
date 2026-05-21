import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

PG_URL = "postgresql://admin:admin123@localhost:5433/central_mayorista"
TOTAL_VENTAS = 100_000
BATCH_SIZE = 5_000

engine = create_engine(PG_URL)

def generar_ventas():
    with engine.begin() as conn:
        productos = conn.execute(text("""
            SELECT id, precio, subregion
            FROM productos
            ORDER BY id
        """)).fetchall()

        if not productos:
            raise Exception("No existen productos en PostgreSQL.")

        print(f"Productos base encontrados: {len(productos)}")
        print(f"Generando {TOTAL_VENTAS:,} ventas sintéticas...")

        fecha_base = datetime(2026, 1, 1)
        batch = []

        for i in range(1, TOTAL_VENTAS + 1):
            producto = random.choice(productos)

            cantidad = random.randint(1, 120)
            precio_unitario = float(producto.precio)
            total = cantidad * precio_unitario

            fecha_venta = fecha_base + timedelta(
                days=random.randint(0, 180),
                hours=random.randint(5, 20),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )

            batch.append({
                "producto_id": producto.id,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario,
                "total": total,
                "subregion": producto.subregion,
                "fecha_venta": fecha_venta
            })

            if len(batch) >= BATCH_SIZE:
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
                """), batch)

                print(f"Insertadas {i:,} ventas...")
                batch = []

        if batch:
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
            """), batch)

        total_ventas = conn.execute(text("SELECT COUNT(*) FROM ventas")).scalar()

        print(f"Proceso finalizado.")
        print(f"Total actual de ventas en PostgreSQL: {total_ventas:,}")

if __name__ == "__main__":
    generar_ventas()