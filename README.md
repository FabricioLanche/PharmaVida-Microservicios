# PharmaVida-Microservicios

Repositorio centralizado para orquestar los tres microservicios de PharmaVida mediante Docker Compose.

## Servicios Incluidos

- **Productos y Ofertas** (FastAPI) - Puerto 8000
- **Usuarios y Compras** (Spring Boot) - Puerto 8080
- **Recetas y Médicos** (Node.js/Express) - Puerto 3000

## Requisitos Previos

- Docker >= 20.10
- Docker Compose >= 1.29
- Git
- Bases de datos externas configuradas en los puertos especificados

## Instalación y Uso

### 1. Clonar el repositorio

\`\`\`bash
git clone <repositorio-url>
cd PharmaVida-Microservicios
\`\`\`

### 2. Configurar variables de entorno

Edita el archivo \`.env\` con tus credenciales de bases de datos y configuraciones específicas:

\`\`\`bash
nano .env
\`\`\`

### 3. Iniciar todos los servicios

\`\`\`bash
docker-compose up -d
\`\`\`

### 4. Verificar estado de los servicios

\`\`\`bash
docker-compose ps
\`\`\`

### 5. Ver logs en tiempo real

\`\`\`bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f productos-api
docker-compose logs -f usuarios-api
docker-compose logs -f recetas-api
\`\`\`

## Acceso a los Servicios

- **Productos API**: http://localhost:8000
- **Usuarios API**: http://localhost:8080
- **Recetas API**: http://localhost:3000

## Comandos Útiles

### Detener todos los servicios
\`\`\`bash
docker-compose down
\`\`\`

### Reconstruir imágenes
\`\`\`bash
docker-compose build --no-cache
\`\`\`

### Reiniciar un servicio específico
\`\`\`bash
docker-compose restart productos-api
\`\`\`

### Ver uso de recursos
\`\`\`bash
docker stats
\`\`\`

## Estructura de Directorios

\`\`\`
PharmaVida-Microservicios/
├── PharmaVida-Productos/     # Backend FastAPI
├── PharmaVida-Usuarios/      # Backend Spring Boot
├── PharmaVida-Recetas/       # Backend Node.js
├── .env                       # Variables de entorno centralizadas
├── docker-compose.yml         # Orquestación de servicios
├── .gitignore                 # Archivos ignorados por Git
└── README.md                  # Este archivo
\`\`\`

## Notas Importantes

1. **Variables de Entorno**: Todos los servicios cargan las variables desde el archivo \`.env\` central.

2. **Health Checks**: Cada servicio tiene configurado health checks automáticos.

3. **Conexiones de Base de Datos**: Los servicios se conectan a bases de datos externas usando las variables HOST, PORT, DATABASE, USER y PASSWORD definidas en el \`.env\`.

4. **AWS Credentials**: Asegúrate de que \`~/.aws\` esté configurado en tu máquina local para que el servicio de recetas pueda acceder a S3.

## Troubleshooting

### El servicio no inicia
\`\`\`bash
docker-compose logs <nombre-servicio>
\`\`\`

### No se conecta a la base de datos
Verifica que las credenciales y puertos en el archivo \`.env\` sean correctos y que las bases de datos externas estén accesibles en las IPs y puertos especificados.

### Puerto en uso localmente
Si un puerto en Docker ya está en uso, verifica qué servicio lo está ocupando:
\`\`\`bash
docker-compose ps
\`\`\`

## Contribuciones

Para contribuir, por favor:

1. Crea una rama desde \`main\`
2. Realiza tus cambios
3. Envía un pull request

## Licencia

Especifica la licencia del proyecto

## Contacto

Para preguntas o problemas, contacta al equipo de desarrollo.
\`\`\`