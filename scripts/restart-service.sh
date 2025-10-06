#!/bin/bash

# ==========================================
# 🔄 Script para reiniciar un servicio específico
# ==========================================

if [ -z "$1" ]; then
    echo "❌ Error: Debes especificar un servicio"
    echo ""
    echo "Uso: ./scripts/restart-service.sh [servicio]"
    echo ""
    echo "Servicios disponibles:"
    echo "  - analytics-api"
    echo "  - orquestador-api"
    echo "  - usuarios-api"
    echo "  - productos-api"
    echo "  - recetas-api"
    echo ""
    exit 1
fi

SERVICE=$1

echo "🔄 Reiniciando servicio: $SERVICE..."
echo ""

# Verificar que el servicio existe
if ! docker compose ps --services | grep -q "^$SERVICE$"; then
    echo "❌ Error: El servicio '$SERVICE' no existe"
    exit 1
fi

# Reiniciar el servicio
docker compose restart $SERVICE

echo ""
echo "✅ Servicio $SERVICE reiniciado"
echo ""
echo "🔍 Ver logs: docker compose logs -f $SERVICE"
echo ""