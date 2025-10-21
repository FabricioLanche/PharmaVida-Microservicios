# Dockerfile para Backend Django
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilación y dependencias comunes de Django
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primero para aprovechar cache
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto de Django (usaremos 8888)
EXPOSE 8888

# Comando para ejecutar Django (ajusta el nombre del proyecto si es necesario)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8888"]