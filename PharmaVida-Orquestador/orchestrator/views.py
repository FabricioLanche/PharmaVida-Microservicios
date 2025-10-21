"""
Views del orquestador para coordinar llamadas entre microservicios.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import (
    registrar_compra_orquestada,
    listar_compras_usuario_detalladas,
    validar_y_actualizar_estado_receta
)
from .utils import OrchestrationError
import logging

logger = logging.getLogger(__name__)


class RegistrarCompraOrquestadaView(APIView):
    def post(self, request):
        try:
            auth_header = request.headers.get('Authorization')
            data = request.data

            productos = data.get('productos')
            cantidades = data.get('cantidades')
            if not productos or not cantidades or len(productos) != len(cantidades):
                return Response(
                    {'error': 'Se requiere arrays de productos y cantidades del mismo tamaño'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            resultado = registrar_compra_orquestada(
                productos_compra=productos,
                cantidades_compra=cantidades,
                auth_token=auth_header,
                datos_adicionales=data.get('datos_adicionales', {})
            )
            return Response(resultado, status=status.HTTP_201_CREATED)

        except OrchestrationError as e:
            logger.error(f"Error de orquestación: {str(e)}")
            return Response(
                {'error': str(e), 'details': getattr(e, 'details', None)},
                status=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            )
        except Exception as e:
            logger.exception("Error inesperado en registrar compra")
            return Response(
                {'error': 'Error interno del servidor', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ListarMisComprasDetalladasView(APIView):
    """
    GET /api/orchestrator/compras/me

    Obtiene las compras del usuario autenticado con detalles completos:
    - Información de productos
    - Ofertas aplicadas
    - Cantidades y precios
    """

    def get(self, request):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return Response(
                    {'error': 'Token de autenticación requerido'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            resultado = listar_compras_usuario_detalladas(auth_header)

            return Response(resultado, status=status.HTTP_200_OK)

        except OrchestrationError as e:
            logger.error(f"Error de orquestación: {str(e)}")
            return Response(
                {'error': str(e), 'details': e.details if hasattr(e, 'details') else None},
                status=e.status_code if hasattr(e, 'status_code') else status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error inesperado en listar compras: {str(e)}")
            return Response(
                {'error': 'Error interno del servidor', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ValidarYActualizarRecetaView(APIView):
    """
    PUT /api/orchestrator/recetas/estado/{id}

    Valida una receta antes de actualizar su estado:
    1. Obtiene información de la receta
    2. Valida que los productos existan y coincidan nombre
    3. Valida que el médico esté colegiado
    4. Valida que el paciente (DNI) coincida con el usuario autenticado
    5. Actualiza el estado de la receta
    """

    def put(self, request, receta_id):
        try:
            # Solo requiere el token en header y el id en la URL
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return Response(
                    {'error': 'Token de autenticación requerido'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # El estado se define fijo a "validada" (puedes parametrizar si quieres)
            nuevo_estado = "validada"

            resultado = validar_y_actualizar_estado_receta(
                receta_id=receta_id,
                nuevo_estado=nuevo_estado,
                auth_token=auth_header
            )

            return Response(resultado, status=status.HTTP_200_OK)

        except OrchestrationError as e:
            logger.error(f"Error de orquestación: {str(e)}")
            return Response(
                {'error': str(e), 'details': getattr(e, 'details', None)},
                status=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            )
        except Exception as e:
            logger.error(f"Error inesperado en validar receta: {str(e)}")
            return Response(
                {'error': 'Error interno del servidor', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckView(APIView):
    """
    GET /api/orchestrator/health

    Endpoint de health check para monitoreo.
    """

    def get(self, request):
        return Response({
            'status': 'healthy',
            'service': 'orchestrator',
            'message': 'Backend orquestador operativo'
        }, status=status.HTTP_200_OK)