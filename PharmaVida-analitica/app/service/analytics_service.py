from app.repository import athena_repository
import requests
import os
from dotenv import load_dotenv

load_dotenv()
INGESTA_BASE_URL = os.getenv("INGESTA_BASE_URL")

def ingesta_mysql():
    response = requests.post(f"{INGESTA_BASE_URL}/mysql")
    return response.json()

def ingesta_postgresql():
    response = requests.post(f"{INGESTA_BASE_URL}/postgresql")
    return response.json()

def ingesta_mongodb():
    response = requests.post(f"{INGESTA_BASE_URL}/mongodb")
    return response.json()

def ventas_por_dia():
    query = """
        SELECT 
            date_format(date_parse(c.fecha_compra, '%Y-%m-%d %H:%i:%s'), '%Y-%m-%d') AS fecha_dia,
            SUM(cc.cantidad) AS total_unidades,
            SUM(cc.cantidad * p.precio) AS total_monto
        FROM compras c
        JOIN compra_productos cp ON c.id = cp.compra_id
        JOIN compra_cantidades cc ON c.id = cc.compra_id
        JOIN productos p ON cp.producto_id = p.id
        GROUP BY 1
        ORDER BY 1;
    """
    return athena_repository.ejecutar_en_athena(query)


def top_productos():
    query = """
        SELECT 
            p.id AS producto_id,
            p.nombre,
            SUM(cc.cantidad) AS total_unidades,
            SUM(cc.cantidad * p.precio) AS facturacion_total
        FROM compra_productos cp
        JOIN compra_cantidades cc ON cp.compra_id = cc.compra_id
        JOIN productos p ON cp.producto_id = p.id
        GROUP BY p.id, p.nombre
        ORDER BY facturacion_total DESC
        LIMIT 10;
    """
    return athena_repository.ejecutar_en_athena(query)


def top_usuarios():
    query = """
        SELECT 
            u.id AS usuario_id,
            u.nombre,
            u.apellido,
            SUM(cc.cantidad * p.precio) AS gasto_total
        FROM compras c
        JOIN usuarios u ON c.usuario_id = u.id
        JOIN compra_productos cp ON c.id = cp.compra_id
        JOIN compra_cantidades cc ON c.id = cc.compra_id
        JOIN productos p ON cp.producto_id = p.id
        GROUP BY u.id, u.nombre, u.apellido
        ORDER BY gasto_total DESC
        LIMIT 10;
    """
    return athena_repository.ejecutar_en_athena(query)


def productos_sin_venta():
    query = """
        SELECT 
            p.id AS producto_id,
            p.nombre AS nombre_producto,
            p.precio,
            p.stock,
            o.id AS oferta_id,
            o.fecha_vencimiento
        FROM productos p
        LEFT JOIN compra_productos cp 
            ON p.id = cp.producto_id
        LEFT JOIN ofertas_detalle od 
            ON p.id = od.producto_id
        LEFT JOIN ofertas o 
            ON od.oferta_id = o.id
        WHERE cp.producto_id IS NULL
          AND (o.fecha_vencimiento IS NULL OR o.fecha_vencimiento = '')
        ORDER BY p.nombre;
    """
    return athena_repository.ejecutar_en_athena(query)
