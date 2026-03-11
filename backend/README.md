# InnovAI Backend

Backend de la aplicación InnovAI desarrollado con FastAPI, MySQL y OAuth2.

## 🏗️ Arquitectura

- **Framework**: FastAPI (Python 3.8+)
- **Base de datos**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0
- **Autenticación**: OAuth2 con JWT
- **Migraciones**: Alembic
- **Testing**: pytest
- **Documentación**: OpenAPI/Swagger automática

## 📋 Prerrequisitos

- Python 3.8 o superior
- MySQL 8.0 o superior
- pip (gestor de paquetes de Python)

## 🚀 Instalación

### 1. Clonar y configurar el proyecto

```bash
cd backend
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configurar la base de datos

#### Opción A: Base de datos local existente
Si ya tienes MySQL ejecutándose localmente:

```bash
# Configurar la base de datos
python setup_database.py

# Inicializar con datos de ejemplo
python init_db.py
```

#### Opción B: Usar Docker
```bash
# Iniciar servicios con Docker
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 3. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar .env con tus credenciales
# Las credenciales por defecto son:
# DATABASE_USER=bmc
# DATABASE_PASSWORD=Innexia
# DATABASE_HOST=localhost
```

## 🔧 Configuración de la Base de Datos

### Credenciales por defecto:
- **Host**: localhost
- **Puerto**: 3306
- **Usuario**: bmc
- **Contraseña**: Innexia
- **Base de datos**: innovai_db

### Crear usuario manualmente en MySQL:
```sql
CREATE USER 'bmc'@'localhost' IDENTIFIED BY 'Innexia';
GRANT ALL PRIVILEGES ON *.* TO 'bmc'@'localhost';
FLUSH PRIVILEGES;
```

## 🏃‍♂️ Ejecutar

### Desarrollo
```bash
# Script de inicio automático
python start_dev.py

# O manualmente
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Producción
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 Documentación de la API

Una vez ejecutando el servidor, accede a:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app tests/
```

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── api/                 # Routers de la API
│   ├── core/               # Configuración y seguridad
│   ├── models/             # Modelos de SQLAlchemy
│   ├── schemas/            # Esquemas Pydantic
│   ├── services/           # Lógica de negocio
│   ├── config.py           # Configuración
│   ├── database.py         # Configuración de BD
│   └── main.py            # Aplicación principal
├── uploads/                # Archivos subidos
├── tests/                  # Tests
├── mysql/                  # Scripts de MySQL
├── requirements.txt        # Dependencias
├── docker-compose.yml      # Docker
├── setup_database.py       # Configuración de BD
├── init_db.py             # Datos iniciales
└── start_dev.py           # Script de desarrollo
```

## 🔐 Endpoints Principales

### Autenticación
- `POST /api/auth/register` - Registro de usuarios
- `POST /api/auth/login` - Inicio de sesión
- `POST /api/auth/refresh` - Renovar token
- `POST /api/auth/logout` - Cerrar sesión

### Usuarios
- `GET /api/users/` - Listar usuarios (admin)
- `GET /api/users/me` - Perfil del usuario actual
- `PUT /api/users/{user_id}` - Actualizar usuario

### Proyectos
- `GET /api/projects/` - Listar proyectos
- `POST /api/projects/` - Crear proyecto
- `GET /api/projects/{project_id}` - Ver proyecto
- `PUT /api/projects/{project_id}` - Actualizar proyecto
- `DELETE /api/projects/{project_id}` - Eliminar proyecto

### Actividades
- `GET /api/activities/` - Listar actividades
- `POST /api/activities/` - Crear actividad
- `PUT /api/activities/{activity_id}` - Actualizar actividad

### Documentos
- `GET /api/documents/project/{project_id}` - Documentos del proyecto
- `POST /api/documents/upload` - Subir documento
- `GET /api/documents/{document_id}/download` - Descargar documento

### Business Model Canvas
- `GET /api/bmc/project/{project_id}` - BMC del proyecto
- `PUT /api/bmc/{canvas_id}` - Actualizar BMC
- `PATCH /api/bmc/{canvas_id}/element` - Actualizar elemento específico

## 🐳 Docker

### Construir imagen
```bash
docker build -t innovai-backend .
```

### Ejecutar contenedor
```bash
docker run -p 8000:8000 innovai-backend
```

### Con Docker Compose
```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Detener servicios
docker-compose down
```

## 🔍 Troubleshooting

### Error de conexión a MySQL
1. Verificar que MySQL esté ejecutándose
2. Verificar credenciales en `.env`
3. Verificar permisos del usuario 'bmc'
4. Ejecutar `python setup_database.py`

### Error de dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Error de permisos en Windows
Ejecutar PowerShell como administrador

## 📝 Licencia

Este proyecto es parte de InnovAI y está bajo licencia privada.

## 🤝 Contribución

Para contribuir al proyecto:
1. Crear una rama para tu feature
2. Implementar cambios
3. Ejecutar tests
4. Crear pull request

## 📞 Soporte

Para soporte técnico, contacta al equipo de desarrollo de InnovAI.
