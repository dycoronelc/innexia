# 🚀 Innexia - Business Model Canvas

Una aplicación completa de **Business Model Canvas** con funcionalidades PWA, backend robusto y frontend moderno.

## ✨ Características Principales

### 🎨 Frontend (React + TypeScript + Material-UI)
- **PWA Completa**: Instalable, offline, sincronización automática
- **Business Model Canvas**: Editor visual intuitivo con 9 bloques
- **Gestión de Proyectos**: CRUD completo con interfaz moderna
- **Gantt Chart**: Visualización de actividades con barras de tiempo
- **Gestión de Documentos**: Subida y organización de archivos
- **Dashboard**: Métricas y resumen del proyecto
- **Responsive**: Optimizado para móvil y escritorio

### 🔧 Backend (FastAPI + SQLAlchemy + MySQL)
- **API REST**: Endpoints completos para todas las funcionalidades
- **Autenticación**: OAuth2 con JWT tokens
- **Base de Datos**: MySQL con migraciones Alembic
- **Documentación**: Swagger/OpenAPI automática
- **CORS**: Configurado para desarrollo y producción
- **Uploads**: Manejo seguro de archivos

### 📱 PWA (Progressive Web App)
- **Instalación**: Como aplicación nativa
- **Offline**: Funcionalidad completa sin conexión
- **Sincronización**: Automática al volver online
- **Cache**: Estrategias inteligentes de almacenamiento
- **Notificaciones**: Push y del sistema

## 🛠️ Requisitos Previos

- **Python 3.8+**
- **Node.js 18+**
- **MySQL 8.0+**
- **Git**

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone <tu-repositorio>
cd innovai
```

### 2. Configurar Base de Datos MySQL

```bash
# Conectar a MySQL como root
mysql -u root -p

# Crear usuario y base de datos
CREATE USER 'bmc'@'localhost' IDENTIFIED BY 'Innexia';
GRANT ALL PRIVILEGES ON *.* TO 'bmc'@'localhost';
FLUSH PRIVILEGES;
CREATE DATABASE innovai_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 3. Configurar Backend

```bash
cd backend

# Copiar archivo de configuración
cp env.example .env

# Editar .env con tus credenciales (opcional, ya están configuradas)
# DB_USER=bmc
# DB_PASSWORD=Innexia
# DB_NAME=innovai_db

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
python setup_database.py

# Inicializar con datos de ejemplo
python init_db.py

# Iniciar servidor de desarrollo
python start_dev.py
```

**Credenciales por defecto:**
- **Admin**: `admin` / `admin123`
- **Usuario**: `usuario1` / `usuario123`

### 4. Configurar Frontend

```bash
# En otra terminal, desde el directorio raíz
cd frontend  # o desde la raíz si no hay subdirectorio

# Instalar dependencias
npm install

# Crear archivo de configuración
cp env.example .env.local

# Editar .env.local (opcional, ya está configurado)
# VITE_API_URL=http://localhost:8000

# Iniciar servidor de desarrollo
npm run dev
```

### 5. Verificar Instalación

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🧪 Testing

### Probar Backend

```bash
cd backend

# Ejecutar pruebas de la API
python test_api.py

# Ejecutar tests unitarios
pytest
```

### Probar Frontend

```bash
# Ejecutar tests
npm test

# Ejecutar linting
npm run lint

# Build de producción
npm run build
```

## 📱 Funcionalidades PWA

### Instalación
1. Abre la aplicación en Chrome/Edge
2. Aparecerá un banner de instalación
3. Haz clic en "Instalar"
4. La app se instalará como aplicación nativa

### Modo Offline
- **Funcionalidad completa** sin conexión
- **Cambios guardados** localmente
- **Sincronización automática** al volver online
- **Indicadores visuales** del estado offline

### Sincronización
- **Automática**: Al volver a estar online
- **Manual**: Botón de sincronización
- **Cola de cambios**: Con reintentos automáticos

## 🔧 Scripts Útiles

### Backend

```bash
# Configurar base de datos
python setup_database.py

# Inicializar con datos de ejemplo
python init_db.py

# Iniciar servidor de desarrollo
python start_dev.py

# Probar API
python test_api.py

# Ejecutar migraciones
alembic upgrade head
```

### Frontend

```bash
# Desarrollo
npm run dev

# Build de producción
npm run build

# Build PWA optimizada
npm run build:pwa

# Vista previa de producción
npm run preview

# Auditoría PWA
npm run pwa:audit
```

## 🗄️ Estructura de la Base de Datos

### Tablas Principales
- **users**: Usuarios del sistema
- **projects**: Proyectos
- **project_activities**: Actividades de proyectos
- **project_documents**: Documentos de proyectos
- **business_model_canvas**: Canvas de modelos de negocio
- **project_tags**: Etiquetas de proyectos

### Relaciones
- Un usuario puede tener múltiples proyectos
- Un proyecto puede tener múltiples actividades
- Un proyecto puede tener múltiples documentos
- Un proyecto tiene un Business Model Canvas
- Un proyecto puede tener múltiples etiquetas

## 🌐 API Endpoints

### Autenticación
- `POST /api/auth/register` - Registro de usuario
- `POST /api/auth/login` - Login de usuario
- `POST /api/auth/verify` - Verificar token

### Usuarios
- `GET /api/users/` - Listar usuarios
- `GET /api/users/{id}` - Obtener usuario
- `PUT /api/users/{id}` - Actualizar usuario
- `DELETE /api/users/{id}` - Eliminar usuario

### Proyectos
- `GET /api/projects/` - Listar proyectos
- `POST /api/projects/` - Crear proyecto
- `GET /api/projects/{id}` - Obtener proyecto
- `PUT /api/projects/{id}` - Actualizar proyecto
- `DELETE /api/projects/{id}` - Eliminar proyecto

### Actividades
- `GET /api/activities/` - Listar actividades
- `POST /api/activities/` - Crear actividad
- `GET /api/activities/project/{project_id}` - Actividades por proyecto
- `PUT /api/activities/{id}` - Actualizar actividad
- `DELETE /api/activities/{id}` - Eliminar actividad

### Business Model Canvas
- `GET /api/bmc/project/{project_id}` - Obtener BMC por proyecto
- `POST /api/bmc/` - Crear BMC
- `PUT /api/bmc/{id}` - Actualizar BMC
- `DELETE /api/bmc/{id}` - Eliminar BMC

### Documentos
- `GET /api/documents/project/{project_id}` - Documentos por proyecto
- `POST /api/documents/upload` - Subir documento
- `DELETE /api/documents/{id}` - Eliminar documento

## 🚀 Despliegue

### Backend (Producción)

```bash
# Instalar dependencias de producción
pip install -r requirements.txt

# Configurar variables de entorno
cp env.example .env
# Editar .env con credenciales de producción

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend (Producción)

```bash
# Build de producción
npm run build:pwa

# Los archivos estarán en dist/
# Servir desde cualquier servidor web estático
```

### Docker (Opcional)

```bash
# Construir imagen
docker build -t innexia-bmc .

# Ejecutar contenedor
docker run -p 8000:8000 innexia-bmc
```

## 🔍 Troubleshooting

### Problemas Comunes

#### Backend no inicia
```bash
# Verificar MySQL
sudo systemctl status mysql

# Verificar credenciales
mysql -u bmc -p

# Verificar puerto
netstat -tlnp | grep 8000
```

#### Frontend no conecta con Backend
```bash
# Verificar URL de la API
echo $VITE_API_URL

# Verificar CORS en backend
# Verificar que el backend esté ejecutándose
```

#### PWA no funciona
```bash
# Verificar Service Worker
# Chrome DevTools > Application > Service Workers

# Verificar Manifest
# Chrome DevTools > Application > Manifest

# Verificar HTTPS en producción
```

## 📚 Documentación Adicional

- **PWA**: [PWA_README.md](./PWA_README.md)
- **API**: http://localhost:8000/docs
- **Backend**: [backend/README.md](./backend/README.md)

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Equipo

- **Desarrollador Principal**: [Tu Nombre]
- **Proyecto**: Innexia Business Model Canvas

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa la documentación
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

---

**¡Disfruta usando Innexia Business Model Canvas! 🎉**
