from flask import Blueprint, jsonify, request
from app.service import analytics_service

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/ventas", methods=["GET"])
def ventas_por_dia():
    """Endpoint para obtener el análisis de ventas por día"""
    data = analytics_service.ventas_por_dia()
    return jsonify(data)

@analytics_bp.route("/top-productos", methods=["GET"])
def top_productos():
    """Endpoint para obtener los productos más vendidos"""
    data = analytics_service.top_productos()
    return jsonify(data)

@analytics_bp.route("/top-usuarios", methods=["GET"])
def top_usuarios():
    """Endpoint para obtener los usuarios con más compras"""
    data = analytics_service.top_usuarios()
    return jsonify(data)

@analytics_bp.route("/productos-sin-venta", methods=["GET"])
def productos_sin_venta():
    """Endpoint para obtener productos sin ventas recientes"""
    data = analytics_service.productos_sin_venta()
    return jsonify(data)

@analytics_bp.route("/ingesta-mysql", methods=["POST"])
def ingesta_mysql():
    """Endpoint para ejecutar la ingesta desde MySQL"""
    data = analytics_service.ingesta_mysql()
    return jsonify(data)

@analytics_bp.route("/ingesta-postgresql", methods=["POST"])
def ingesta_postgresql():
    """Endpoint para ejecutar la ingesta desde PostgreSQL"""
    data = analytics_service.ingesta_postgresql()
    return jsonify(data)

@analytics_bp.route("/ingesta-mongodb", methods=["POST"])
def ingesta_mongodb():
    """Endpoint para ejecutar la ingesta desde MongoDB"""
    data = analytics_service.ingesta_mongodb()
    return jsonify(data)

@analytics_bp.route("/docs", methods=["GET"])
def docs_redirect():
    """Redirige a la documentación de Swagger"""
    from flask import redirect
    return redirect("/apidocs")

@analytics_bp.route("/echo", methods=["GET"])
def ping():
    """Endpoint de health check"""
    return {"message": "Conectado correctamente con Flask y Athena ✅"}