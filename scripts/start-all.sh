#!/bin/bash

# ==========================================
# 🚀 Script para iniciar todos los servicios
# ==========================================

set -e

echo "🚀 Iniciando todos los servicios de PharmaVida..."
echo ""

# Verificar que docker compose está instalado
if ! command -v docker compose &> /dev/null; then
    echo "❌ Error: docker compose no está instalado"
    exit 1
fi

# Verificar archivo .env centralizado
echo "🔍 Verificando archivo .env..."

if [ ! -f ".env" ]; then
    echo "❌ Error: No existe el archivo .env en la raíz del proyecto"
    echo ""
    echo "Por favor, crea el archivo .env copiando de .env.example:"
    echo "   cp .env.example .env"
    echo ""
    echo "Luego edita .env con tus credenciales reales"
    exit 1
fi

echo "✅ Archivo .env encontrado"

# Construir y levantar servicios
echo ""
echo "🔨 Construyendo imágenes..."
docker compose build

echo ""
echo "⬆️  Levantando servicios..."
docker compose up -d

echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

echo ""
echo "✅ Servicios iniciados:"
echo ""
echo "   📊 Analytics API:    http://localhost:5000"
echo "   🎯 Orquestador API:  http://localhost:8888"
echo "   👥 Usuarios API:     http://localhost:8080"
echo "   🏪 Productos API:    http://localhost:8000"
echo "   📝 Recetas API:      http://localhost:3000"
echo ""
echo "🔍 Para ver los logs: docker compose logs -f"
echo "🛑 Para detener: ./scripts/stop-all.sh"
echo ""