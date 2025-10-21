from flask import Flask
from flask_cors import CORS
from app.controller.analytics_controller import analytics_bp
from dotenv import load_dotenv
from flasgger import Swagger
import os

# Carga las variables del .env
load_dotenv()

app = Flask(__name__)

# Habilitar CORS (para que el frontend pueda hacer requests)
CORS(app)

# Configurar Swagger UI para usar el archivo YAML
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

# Ruta relativa desde donde está main.py (/app/app/main.py)
swagger_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "swagger.yml")

# Verificar que el archivo existe antes de inicializar Swagger
if not os.path.exists(swagger_file_path):
    print(f"⚠️ ADVERTENCIA: No se encontró swagger.yml en {swagger_file_path}")
    swagger_file_path = None

if swagger_file_path:
    Swagger(app, config=swagger_config, template_file=swagger_file_path)
else:
    Swagger(app, config=swagger_config)

# Registrar el Blueprint del microservicio analítico
app.register_blueprint(analytics_bp, url_prefix="/api/analitica")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)