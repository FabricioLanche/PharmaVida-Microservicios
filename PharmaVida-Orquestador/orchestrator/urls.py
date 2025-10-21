from django.urls import path
from .views import (
    RegistrarCompraOrquestadaView,
    ListarMisComprasDetalladasView,
    ValidarYActualizarRecetaView,
    HealthCheckView,
)

from .swagger_view import (
    SwaggerUIView,
    OpenAPIYAMLView
)

urlpatterns = [
    # Health check
    path('echo', HealthCheckView.as_view(), name='echo'),

    # Compras orquestadas
    path('compras', RegistrarCompraOrquestadaView.as_view(), name='comprar'),
    path('compras/me', ListarMisComprasDetalladasView.as_view(), name='mis-compras'),

    # Recetas orquestadas
    path('recetas/validar/<str:receta_id>', ValidarYActualizarRecetaView.as_view(), name='validar-receta'),

    # Documentación Swagger UI
    path('docs', SwaggerUIView.as_view(), name='swagger-ui'),
    path('openapi.yaml', OpenAPIYAMLView.as_view(), name='openapi-yaml'),
]
