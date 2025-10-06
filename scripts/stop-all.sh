#!/bin/bash

# ==========================================
# 🛑 Script para detener todos los servicios
# ==========================================

set -e

echo "🛑 Deteniendo todos los servicios de PharmaVida..."
echo ""

docker compose down

echo ""
echo "✅ Todos los servicios han sido detenidos"
echo ""
echo "💡 Para iniciar nuevamente: ./scripts/start-all.sh"
echo "🗑️  Para limpiar completamente (incluye volúmenes): docker-compose down -v"
echo ""