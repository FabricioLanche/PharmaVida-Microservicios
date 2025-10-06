# Backend Orquestador - Sistema de Botica

Backend orquestador sin base de datos desarrollado en Django que coordina las llamadas entre los diferentes microservicios del sistema de botica.

## Descripción

El backend orquestador actúa como capa de integración entre los microservicios, proporcionando endpoints que combinan y validan información de múltiples fuentes antes de realizar operaciones críticas.

### Responsabilidades

- **Validación de compras**: Verifica stock y recetas médicas antes de registrar compras
- **Enriquecimiento de datos**: Combina información de productos con compras
- **Validación de recetas**: Valida médicos, pacientes y productos antes de aprobar recetas
- **Coordinación**: Orquesta llamadas entre microservicios de forma transparente

## Estructura del Proyecto

```
backend-orquestador/
├── config/                     # Configuración del proyecto Django
│   ├── __init__.py
│   ├── settings.py            # Configuración principal
│   ├── urls.py                # URLs raíz
│   ├── wsgi.py                # WSGI entry point
│   └── asgi.py                # ASGI entry point
├── orchestrator/              # App principal del orquestador
│   ├── __init__.py
│   ├── apps.py                # Configuración de la app
│   ├── views.py               # Endpoints (controladores)
│   ├── services.py            # Lógica de orquestación
│   ├── utils.py               # Utilidades y excepciones
│   └── urls.py                # URLs del orquestador
├── manage.py                  # Script de gestión Django
├── requirements.txt           # Dependencias Python
├── .env.example              # Ejemplo de variables de entorno
├── .gitignore                # Archivos ignorados por Git
├── run_server.sh             # Script para ejecutar el servidor
└── README.md                 # Esta documentación
```

## Requisitos

- Python 3.9+
- pip
- virtualenv (recomendado)

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd backend-orquestador
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# En Linux/Mac
source venv/bin/activate

# En Windows
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Editar `.env` con las URLs de tus microservicios:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

URL_USUARIOS_COMPRAS=http://localhost:8081
URL_PRODUCTOS_OFERTAS=http://localhost:8082
URL_RECETAS_MEDICOS=http://localhost:8083
```

## Ejecución

### Opción 1: Usando el script (Linux/Mac)

```bash
chmod +x run_server.sh
./run_server.sh
```

### Opción 2: Manualmente

```bash
python manage.py runserver 8888
```

El servidor estará disponible en: `http://localhost:8888`

## Endpoints Disponibles

### Health Check

```
GET /api/orchestrator/health
```

Verifica que el servicio esté operativo.

**Respuesta:**
```json
{
  "status": "healthy",
  "service": "orchestrator",
  "message": "Backend orquestador operativo"
}
```

### Registrar Compra (Orquestado)

```
POST /api/orchestrator/compras
```

Registra una compra validando stock y recetas médicas.

**Headers:**
- `Authorization: Bearer <token>`

**Body:**
```json
{
  "productos": [
    {
      "producto_id": 1,
      "cantidad": 2
    },
    {
      "producto_id": 5,
      "cantidad": 1
    }
  ],
  "datos_adicionales": {
    "metodo_pago": "tarjeta"
  }
}
```

**Flujo de orquestación:**
1. Obtiene detalles completos de cada producto
2. Valida stock disponible
3. Si algún producto requiere receta, valida recetas del usuario
4. Registra la compra en el microservicio de compras
5. Retorna la compra con detalles enriquecidos

### Listar Mis Compras (Detalladas)

```
GET /api/orchestrator/compras/me
```

Obtiene las compras del usuario autenticado con detalles de productos.

**Headers:**
- `Authorization: Bearer <token>`

**Respuesta:**
```json
{
  "compras": [
    {
      "id": 1,
      "fecha_compra": "2025-10-01",
      "usuario_id": 123,
      "productos_detalle": [
        {
          "producto_id": 1,
          "cantidad": 2,
          "nombre": "Paracetamol 500mg",
          "precio": 5.50,
          "tipo": "medicamento",
          "stock": 100
        }
      ]
    }
  ]
}
```

### Listar Todas las Compras (Admin)

```
GET /api/orchestrator/compras/all
```

Obtiene todas las compras con detalles (solo administradores).

**Headers:**
- `Authorization: Bearer <token>` (debe ser admin)

### Validar y Actualizar Estado de Receta

```
PUT /api/orchestrator/recetas/estado/{receta_id}
```

Valida una receta y actualiza su estado.

**Headers:**
- `Authorization: Bearer <token>`

**Body:**
```json
{
  "estadovalidacion": "VALIDADA"
}
```

**Flujo de orquestación:**
1. Obtiene información de la receta
2. Valida que todos los productos existan
3. Valida que el médico esté colegiado y con colegiatura válida
4. Valida que el paciente exista en el sistema
5. Actualiza el estado de la receta

**Respuesta:**
```json
{
  "mensaje": "Receta validada y actualizada exitosamente",
  "receta": { ... },
  "validaciones": {
    "productos_validados": 3,
    "medico_valido": true,
    "paciente_valido": true
  }
}
```

## Manejo de Errores

Todos los endpoints retornan errores en formato estandarizado:

```json
{
  "error": "Descripción del error",
  "details": {
    "campo_adicional": "información adicional"
  }
}
```

### Códigos de estado HTTP

- `200 OK`: Operación exitosa
- `201 Created`: Recurso creado exitosamente
- `400 Bad Request`: Error en los datos enviados
- `401 Unauthorized`: Token no proporcionado o inválido
- `403 Forbidden`: Sin permisos para la operación
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error del servidor
- `503 Service Unavailable`: Microservicio no disponible
- `504 Gateway Timeout`: Timeout al comunicarse con microservicio

## Configuración de Microservicios

El orquestador necesita que los siguientes microservicios estén disponibles:

### 1. usuarios_y_autenticacion_y_compras (Java/Spring Boot)
- Puerto por defecto: 8081
- Endpoints utilizados:
  - `POST /api/compras`
  - `GET /api/compras/me`
  - `GET /api/compras/all`
  - `GET /api/user/me`
  - `GET /api/user/all`

### 2. productos_y_ofertas (Python/FastAPI)
- Puerto por defecto: 8082
- Endpoints utilizados:
  - `GET /api/productos/{id}`
  - `GET /api/ofertas/all`

### 3. recetas_y_medicos (Node.js/Express)
- Puerto por defecto: 8083
- Endpoints utilizados:
  - `GET /api/recetas/{id}`
  - `GET /api/recetas/filter`
  - `PUT /api/recetas/estado/{id}`
  - `GET /api/medicos/filter`

## Variables de Entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `SECRET_KEY` | Clave secreta de Django | - |
| `DEBUG` | Modo debug | `True` |
| `URL_USUARIOS_COMPRAS` | URL del microservicio de usuarios | `http://localhost:8081` |
| `URL_PRODUCTOS_OFERTAS` | URL del microservicio de productos | `http://localhost:8082` |
| `URL_RECETAS_MEDICOS` | URL del microservicio de recetas | `http://localhost:8083` |
## Desarrollo

### Sin Base de Datos

Este backend NO utiliza base de datos. Toda la información se obtiene de los microservicios correspondientes.

### Logging

Los logs se configuran automáticamente y registran:
- Errores de comunicación con microservicios
- Errores de validación
- Excepciones no manejadas

### Testing

Para ejecutar tests (cuando se implementen):

```bash
python manage.py test orchestrator
```

## Producción

### Usando Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8888 --workers 4
```

### Variables de Entorno en Producción

Asegúrate de configurar:
- `SECRET_KEY` con una clave segura y aleatoria
- `DEBUG=False`
- URLs correctas de los microservicios

## Troubleshooting

### Error: "No se pudo conectar con el microservicio"

- Verifica que todos los microservicios estén ejecutándose
- Confirma las URLs en el archivo `.env`
- Revisa los logs de los microservicios

### Error: "Token de autenticación requerido"

- Asegúrate de enviar el header `Authorization: Bearer <token>`
- Verifica que el token sea válido

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request