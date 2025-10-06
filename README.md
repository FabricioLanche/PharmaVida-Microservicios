# 📦 Guía de Migración - De múltiples compose a uno centralizado

Esta guía te ayudará a migrar de tu estructura actual (con múltiples `docker-compose.yml` y `.env`) a la nueva estructura centralizada.

## 🎯 Objetivo

**Antes:**
- 5 archivos `docker-compose.yml` (uno por backend)
- 5 archivos `.env` (uno por backend)
- Gestión manual de cada servicio

**Después:**
- 1 archivo `docker-compose.yml` centralizado
- 1 archivo `.env` centralizado
- Control de todos los servicios con un solo comando

## 📋 Pasos de Migración

### 1. Preparar el nuevo repositorio

```bash
# Crear la estructura del monorepo
mkdir pharmavida-backend-monorepo
cd pharmavida-backend-monorepo
```

### 2. Copiar tus backends existentes

```bash
# Copiar cada backend (SIN sus docker-compose.yml ni .env individuales)
cp -r /ruta/a/PharmaVida-analitica .
cp -r /ruta/a/orquestador_backend .
cp -r /ruta/a/farmacy .
cp -r /ruta/a/pharmacy-products .
cp -r /ruta/a/recetas_cloud .
```

### 3. Eliminar archivos de compose individuales

```bash
# IMPORTANTE: Eliminar los docker-compose.yml de cada backend
rm PharmaVida-analitica/docker-compose.yml
rm orquestador_backend/docker-compose.yml
rm farmacy/docker-compose.yml
rm pharmacy-products/docker-compose.yml
rm recetas_cloud/docker-compose.yml

# También los .dockerignore si existen
rm */docker-compose.yml
```

### 4. Crear el archivo .env centralizado

```bash
# Copiar la plantilla
cp .env.example .env
```

Ahora migra las variables de tus antiguos archivos `.env`:

#### Mapeo de variables:

**De `PharmaVida-analitica/.env` → `.env` (raíz):**
```bash
# Copiar tal cual:
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...
AWS_REGION=...
ATHENA_OUTPUT_LOCATION=...
ATHENA_DATABASE=...
INGESTA_BASE_URL=...
```

**De `orquestador_backend/.env` → `.env` (raíz):**
```bash
# Renombrar:
SECRET_KEY → DJANGO_SECRET_KEY
DEBUG → DJANGO_DEBUG

# Las URLs de microservicios YA NO son necesarias aquí
# Se definen en el docker-compose.yml usando nombres de servicios
```

**De `farmacy/.env` → `.env` (raíz):**
```bash
# Renombrar con prefijo POSTGRES_:
DB_HOST → POSTGRES_HOST
DB_PORT → POSTGRES_PORT
DB_NAME → POSTGRES_DB_NAME
DB_USER → POSTGRES_USER
DB_PASSWORD → POSTGRES_PASSWORD

# Copiar tal cual:
ADMIN_EMAIL=...
ADMIN_PASSWORD=...
ADMIN_FIRSTNAME=...
ADMIN_LASTNAME=...
ADMIN_DNI=...
JWT_SECRET=...
JWT_EXPIRATION=...
```

**De `pharmacy-products/.env` → `.env` (raíz):**
```bash
# Copiar tal cual (ya tienen prefijo MYSQL_):
MYSQL_HOST=...
MYSQL_PORT=...
MYSQL_DATABASE=...
MYSQL_USER=...
MYSQL_PASSWORD=...

# HOST y PORT ya no son necesarios (definidos en docker-compose)
```

**De `recetas_cloud/.env` → `.env` (raíz):**
```bash
# Renombrar MONGO_PASS:
MONGO_PASS → MONGO_PASSWORD

# Copiar tal cual:
MONGO_HOST=...
MONGO_PORT=...
MONGO_DB_NAME=...
MONGO_USER=...

# AWS S3:
AWS_S3_BUCKET=...

# Las credenciales AWS ya están definidas arriba (compartidas)
# PORT ya no es necesario (definido en docker-compose)
```

### 5. Copiar los archivos del monorepo

```bash
# En la raíz del proyecto, copiar:
# - docker-compose.yml (el nuevo centralizado)
# - .gitignore
# - README.md
# - .env.example

# Crear carpeta de scripts
mkdir scripts
cd scripts

# Copiar los scripts:
# - start-all.sh
# - stop-all.sh
# - check-health.sh
# - restart-service.sh

# Dar permisos de ejecución
chmod +x *.sh
```

### 6. Limpiar archivos .env antiguos

```bash
# IMPORTANTE: Eliminar los .env de cada backend
rm PharmaVida-analitica/.env
rm orquestador_backend/.env
rm farmacy/.env
rm pharmacy-products/.env
rm recetas_cloud/.env
```

### 7. Actualizar el Orquestador

El orquestador necesita actualizar las URLs de los microservicios para usar los nombres de servicios Docker:

**En `orquestador_backend/orchestrator/services.py` o donde estén definidas las URLs:**

```python
# ❌ ANTES (usando localhost):
URL_USUARIOS = "http://localhost:8080"
URL_PRODUCTOS = "http://localhost:8000"
URL_RECETAS = "http://localhost:3000"

# ✅ DESPUÉS (usando nombres de servicios Docker):
URL_USUARIOS = "http://usuarios-api:8080"
URL_PRODUCTOS = "http://productos-api:8000"
URL_RECETAS = "http://recetas-api:3000"
```

O mejor aún, usar las variables de entorno que ya están en el `.env`:

```python
import os

URL_USUARIOS = os.getenv('URL_USUARIOS_COMPRAS', 'http://usuarios-api:8080')
URL_PRODUCTOS = os.getenv('URL_PRODUCTOS_OFERTAS', 'http://productos-api:8000')
URL_RECETAS = os.getenv('URL_RECETAS_MEDICOS', 'http://recetas-api:3000')
```

### 8. Verificar la estructura final

Tu estructura debe verse así:

```
pharmavida-backend-monorepo/
├── PharmaVida-analitica/
│   ├── app/
│   ├── Dockerfile          ✅ Mantener
│   ├── main.py
│   └── requirements.txt
│
├── orquestador_backend/
│   ├── config/
│   ├── orchestrator/
│   ├── Dockerfile          ✅ Mantener
│   └── requirements.txt
│
├── farmacy/
│   ├── src/
│   ├── Dockerfile          ✅ Mantener
│   └── pom.xml
│
├── pharmacy-products/
│   ├── app/
│   ├── Dockerfile          ✅ Mantener
│   └── requirements.txt
│
├── recetas_cloud/
│   ├── src/
│   ├── Dockerfile          ✅ Mantener
│   └── package.json
│
├── scripts/
│   ├── start-all.sh
│   ├── stop-all.sh
│   ├── check-health.sh
│   └── restart-service.sh
│
├── .env                    ⭐ NUEVO - Centralizado
├── .env.example
├── .gitignore
├── docker-compose.yml      ⭐ NUEVO - Único compose
└── README.md
```

### 9. Probar la migración

```bash
# Verificar que el .env está completo
cat .env

# Iniciar todos los servicios
./scripts/start-all.sh

# Verificar el estado
./scripts/check-health.sh

# Ver logs
docker-compose logs -f
```

## 🔍 Checklist de Migración

- [ ] ✅ Backends copiados al monorepo
- [ ] ✅ `docker-compose.yml` individuales eliminados
- [ ] ✅ `.env` individuales eliminados
- [ ] ✅ `.env` centralizado creado y configurado
- [ ] ✅ Scripts copiados y con permisos de ejecución
- [ ] ✅ URLs del orquestador actualizadas (localhost → nombres de servicios)
- [ ] ✅ `.gitignore` configurado
- [ ] ✅ Servicios iniciados correctamente
- [ ] ✅ Health checks pasando

## ⚠️ Problemas Comunes y Soluciones

### Problema 1: "Cannot connect to service"

**Causa:** Las URLs todavía usan `localhost` en lugar de nombres de servicios Docker.

**Solución:**
```bash
# Dentro de la red Docker, usar nombres de servicios:
http://usuarios-api:8080      # ✅ Correcto
http://localhost:8080          # ❌ Incorrecto dentro de Docker
```

### Problema 2: "Environment variable not found"

**Causa:** Falta una variable en el `.env` centralizado.

**Solución:**
```bash
# Verificar que todas las variables estén en .env
grep -r "os.getenv\|process.env\|System.getenv" */src */app

# Comparar con .env.example
diff .env .env.example
```

### Problema 3: "Port already in use"

**Causa:** Un servicio antiguo todavía está corriendo.

**Solución:**
```bash
# Detener todos los contenedores antiguos
docker ps -a | grep pharmavida | awk '{print $1}' | xargs docker stop
docker ps -a | grep pharmavida | awk '{print $1}' | xargs docker rm

# O usar el puerto diferente en .env:
USUARIOS_PORT=8081  # En lugar de 8080
```

### Problema 4: "Service unhealthy"

**Causa:** El servicio tarda más en iniciar de lo esperado.

**Solución:**
```bash
# Ver logs del servicio específico
docker-compose logs -f [nombre-servicio]

# Aumentar el start_period en docker-compose.yml si es necesario
```

## 🎉 Ventajas Post-Migración

Después de completar la migración, disfrutarás de:

✅ **Gestión unificada**: Un solo comando para todo  
✅ **Configuración centralizada**: Un solo archivo `.env`  
✅ **Red compartida**: Comunicación directa entre servicios  
✅ **Más fácil de mantener**: Menos archivos, menos complejidad  
✅ **Deploy más simple**: Copiar todo el monorepo y levantar  
✅ **Better DevOps**: Ideal para CI/CD pipelines

## 📚 Siguientes Pasos

1. **Configurar CI/CD**: Automatizar el deploy del monorepo
2. **Agregar monitoreo**: Prometheus + Grafana para métricas
3. **Implementar logging centralizado**: ELK Stack o similar
4. **Crear backups**: Automatizar respaldos de `.env`
5. **Documentar APIs**: Centralizar la documentación Swagger/OpenAPI

## 💡 Tips Pro

### Cambio rápido entre ambientes

```bash
# Desarrollo
cp .env.development .env
./scripts/start-all.sh

# Producción
cp .env.production .env
./scripts/start-all.sh
```

### Debugging de un servicio específico

```bash
# Detener un servicio
docker-compose stop productos-api

# Correrlo en modo interactivo
docker-compose run --rm --service-ports productos-api

# Ver logs en tiempo real
docker-compose logs -f productos-api
```

### Backup del .env

```bash
# Crear backup cifrado
tar -czf - .env | openssl enc -aes-256-cbc -e > env.backup.tar.gz.enc

# Restaurar
openssl enc -aes-256-cbc -d -in env.backup.tar.gz.enc | tar xz
```

---

**¿Necesitas ayuda?** Revisa el [README.md](./README.md) principal o abre un issue en el repositorio.