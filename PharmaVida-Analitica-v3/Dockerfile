# Dockerfile para Flask Backend
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para Athena y compilación
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python y asegurarse de incluir flasgger
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir flasgger

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto de Flask
EXPOSE 5000

# Comando para ejecutar la aplicación Flask (ajustado)
CMD ["python", "app/main.py"]
