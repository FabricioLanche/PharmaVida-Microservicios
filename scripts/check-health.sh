#!/bin/bash

# ==========================================
# 🏥 Script para verificar el estado de todos los servicios
# ==========================================

echo "🏥 Verificando estado de los servicios..."
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_service() {
    local name=$1
    local url=$2
    local port=$3

    printf "%-25s" "$name:"

    # Verificar si el contenedor está corriendo
    if ! docker ps --format '{{.Names}}' | grep -q "$name"; then
        echo -e "${RED}❌ Contenedor no está corriendo${NC}"
        return 1
    fi

    # Verificar el endpoint
    if curl -f -s -o /dev/null "$url" 2>/dev/null; then
        echo -e "${GREEN}✅ Activo (Puerto $port)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Contenedor activo pero endpoint no responde${NC}"
        return 1
    fi
}

echo "📊 Estado de los servicios:"
echo ""

check_service "pharmavida_analytics" "http://localhost:5000/echo" "5000"
check_service "pharmavida_orquestador" "http://localhost:8888/echo" "8888"
check_service "pharmavida_usuarios" "http://localhost:8080/api/health" "8080"
check_service "pharmavida_productos" "http://localhost:8000/docs" "8000"
check_service "pharmavida_recetas" "http://localhost:3000/health" "3000"

echo ""
echo "💡 Para ver logs de un servicio: docker logs [nombre_contenedor]"
echo "💡 Para ver logs en tiempo real: docker logs -f [nombre_contenedor]"
echo ""