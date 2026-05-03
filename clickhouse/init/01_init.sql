CREATE DATABASE IF NOT EXISTS central_analytics;

CREATE TABLE IF NOT EXISTS central_analytics.ventas_analytics
(
    id UInt32,
    producto String,
    categoria String,
    subregion String,
    cantidad UInt32,
    precio_unitario Float64,
    total Float64,
    fecha_venta DateTime
)
ENGINE = MergeTree
ORDER BY (subregion, fecha_venta, id);

CREATE TABLE IF NOT EXISTS central_analytics.precios_historicos
(
    id UInt32,
    producto String,
    categoria String,
    subregion String,
    precio Float64,
    fecha DateTime
)
ENGINE = MergeTree
ORDER BY (producto, fecha);

INSERT INTO central_analytics.ventas_analytics VALUES
(1, 'Papa capira', 'Tubérculos', 'Norte', 10, 2500, 25000, '2026-04-01 08:00:00'),
(2, 'Tomate chonto', 'Hortalizas', 'Oriente', 8, 3200, 25600, '2026-04-01 09:00:00'),
(3, 'Cebolla cabezona', 'Hortalizas', 'Norte', 15, 2800, 42000, '2026-04-01 10:00:00'),
(4, 'Banano criollo', 'Frutas', 'Urabá', 20, 1800, 36000, '2026-04-01 11:00:00'),
(5, 'Yuca', 'Tubérculos', 'Occidente', 12, 2100, 25200, '2026-04-01 12:00:00'),
(6, 'Aguacate hass', 'Frutas', 'Suroeste', 7, 4500, 31500, '2026-04-01 13:00:00'),
(7, 'Zanahoria', 'Hortalizas', 'Oriente', 9, 2600, 23400, '2026-04-01 14:00:00'),
(8, 'Plátano verde', 'Plátanos', 'Urabá', 14, 2200, 30800, '2026-04-01 15:00:00'),
(9, 'Mango', 'Frutas', 'Magdalena Medio', 6, 3900, 23400, '2026-04-01 16:00:00'),
(10, 'Maíz', 'Granos', 'Bajo Cauca', 18, 1700, 30600, '2026-04-01 17:00:00');

INSERT INTO central_analytics.precios_historicos VALUES
(1, 'Papa capira', 'Tubérculos', 'Norte', 2400, '2026-03-28 08:00:00'),
(2, 'Papa capira', 'Tubérculos', 'Norte', 2450, '2026-03-29 08:00:00'),
(3, 'Papa capira', 'Tubérculos', 'Norte', 2500, '2026-04-01 08:00:00'),
(4, 'Tomate chonto', 'Hortalizas', 'Oriente', 3000, '2026-03-28 09:00:00'),
(5, 'Tomate chonto', 'Hortalizas', 'Oriente', 3100, '2026-03-29 09:00:00'),
(6, 'Tomate chonto', 'Hortalizas', 'Oriente', 3200, '2026-04-01 09:00:00'),
(7, 'Aguacate hass', 'Frutas', 'Suroeste', 4300, '2026-03-28 10:00:00'),
(8, 'Aguacate hass', 'Frutas', 'Suroeste', 4400, '2026-03-29 10:00:00'),
(9, 'Aguacate hass', 'Frutas', 'Suroeste', 4500, '2026-04-01 10:00:00'),
(10, 'Maíz', 'Granos', 'Bajo Cauca', 1600, '2026-03-28 11:00:00');