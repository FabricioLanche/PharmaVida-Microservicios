"""
Vista para servir la documentación Swagger UI.
"""

from django.http import HttpResponse
from django.views import View
import os
import yaml
from django.conf import settings  # Agrega esto arriba, junto a los imports


class SwaggerUIView(View):
    """
    Sirve la interfaz de Swagger UI con la especificación OpenAPI.
    """

    def get(self, request):
        html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Orquestador - Documentación</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.10.0/swagger-ui.css">
    <style>
        body {
            margin: 0;
            padding: 0;
        }
        .topbar {
            display: none;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>

    <script src="https://unpkg.com/swagger-ui-dist@5.10.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.10.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: "/api/orchestrator/openapi.yaml",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                persistAuthorization: true
            });
            window.ui = ui;
        };
    </script>
</body>
</html>
        """
        return HttpResponse(html, content_type='text/html')

class OpenAPIYAMLView(View):
    def get(self, request):

        yaml_path = os.path.join(settings.BASE_DIR, 'openapi.yaml')

        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                yaml_content = f.read()
            return HttpResponse(yaml_content, content_type='application/x-yaml')
        except FileNotFoundError:
            return HttpResponse('openapi.yaml no encontrado', status=404)