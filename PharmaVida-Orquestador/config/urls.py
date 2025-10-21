"""
Configuración principal de URLs del proyecto.
"""

from django.urls import path, include

urlpatterns = [
    path('api/orchestrator/', include('orchestrator.urls')),
]