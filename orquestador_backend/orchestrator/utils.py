"""
Utilidades y manejadores de excepciones para el orquestador.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


class OrchestrationError(Exception):
    """Excepción personalizada para errores de orquestación."""

    def __init__(self, message, status_code=400, details=None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


def custom_exception_handler(exc, context):
    """
    Manejador personalizado de excepciones para DRF.
    """

    # Llamar al manejador por defecto primero
    response = exception_handler(exc, context)

    # Si es una OrchestrationError, personalizamos la respuesta
    if isinstance(exc, OrchestrationError):
        return Response(
            {
                'error': exc.message,
                'details': exc.details
            },
            status=exc.status_code
        )

    # Para otras excepciones, retornamos la respuesta por defecto
    if response is not None:
        response.data = {
            'error': response.data.get('detail', 'Error en la petición'),
            'details': response.data
        }

    return response