from flask import Flask
from flask_cors import CORS
from app.controller.analytics_controller import analytics_bp
from flask import Flask
from dotenv import load_dotenv


# 👇 Carga las variables del .env
load_dotenv()

app = Flask(__name__)

# Habilitar CORS (para que el frontend pueda hacer requests)
CORS(app)

# Registrar el Blueprint del microservicio analítico
app.register_blueprint(analytics_bp, url_prefix="/api/analitica")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
