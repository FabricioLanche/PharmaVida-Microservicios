# Dockerfile para Flask Backend
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para Athena y compilación
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto de Flask
EXPOSE 5000

# Comando para ejecutar la aplicación Flask
CMD ["python", "main.py"]