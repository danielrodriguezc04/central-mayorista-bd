CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    categoria VARCHAR(80) NOT NULL,
    subregion VARCHAR(80) NOT NULL,
    precio NUMERIC(10,2) NOT NULL,
    stock INTEGER NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ventas (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario NUMERIC(10,2) NOT NULL,
    total NUMERIC(10,2) NOT NULL,
    subregion VARCHAR(80) NOT NULL,
    fecha_venta TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_producto
        FOREIGN KEY(producto_id)
        REFERENCES productos(id)
);

INSERT INTO productos (nombre, categoria, subregion, precio, stock) VALUES
('Papa capira', 'Tubérculos', 'Norte', 2500.00, 100),
('Tomate chonto', 'Hortalizas', 'Oriente', 3200.00, 80),
('Cebolla cabezona', 'Hortalizas', 'Norte', 2800.00, 70),
('Banano criollo', 'Frutas', 'Urabá', 1800.00, 120),
('Yuca', 'Tubérculos', 'Occidente', 2100.00, 95),
('Aguacate hass', 'Frutas', 'Suroeste', 4500.00, 60),
('Zanahoria', 'Hortalizas', 'Oriente', 2600.00, 75),
('Plátano verde', 'Plátanos', 'Urabá', 2200.00, 110),
('Mango', 'Frutas', 'Magdalena Medio', 3900.00, 50),
('Maíz', 'Granos', 'Bajo Cauca', 1700.00, 140);

INSERT INTO ventas (producto_id, cantidad, precio_unitario, total, subregion, fecha_venta) VALUES
(1, 10, 2500.00, 25000.00, 'Norte', '2026-04-01 08:00:00'),
(2, 8, 3200.00, 25600.00, 'Oriente', '2026-04-01 09:00:00'),
(3, 15, 2800.00, 42000.00, 'Norte', '2026-04-01 10:00:00'),
(4, 20, 1800.00, 36000.00, 'Urabá', '2026-04-01 11:00:00'),
(5, 12, 2100.00, 25200.00, 'Occidente', '2026-04-01 12:00:00'),
(6, 7, 4500.00, 31500.00, 'Suroeste', '2026-04-01 13:00:00'),
(7, 9, 2600.00, 23400.00, 'Oriente', '2026-04-01 14:00:00'),
(8, 14, 2200.00, 30800.00, 'Urabá', '2026-04-01 15:00:00'),
(9, 6, 3900.00, 23400.00, 'Magdalena Medio', '2026-04-01 16:00:00'),
(10, 18, 1700.00, 30600.00, 'Bajo Cauca', '2026-04-01 17:00:00');