# 📚 Documentación de la API - InnovAI Backend

## 🌟 **Descripción General**

La API de InnovAI es un sistema completo de gestión de proyectos que incluye autenticación OAuth2, gestión de usuarios, proyectos, actividades, documentos y Business Model Canvas.

**Base URL**: `http://localhost:8000`  
**Versión**: 1.0.0  
**Formato de Respuesta**: JSON  

## 🔐 **Autenticación**

La API utiliza **OAuth2 con JWT tokens** para la autenticación. Todos los endpoints protegidos requieren un token de acceso válido en el header `Authorization`.

```
Authorization: Bearer <access_token>
```

### Tipos de Usuario
- **admin**: Acceso completo a todas las funcionalidades
- **user**: Acceso limitado a sus propios recursos y proyectos

---

## 📋 **Endpoints de Autenticación**

### **POST** `/api/auth/register`
Registrar un nuevo usuario.

**Body:**
```json
{
  "username": "nuevo_usuario",
  "email": "usuario@ejemplo.com",
  "full_name": "Nombre Completo",
  "password": "contraseña123",
  "role": "user"
}
```

**Respuesta (201):**
```json
{
  "id": 1,
  "username": "nuevo_usuario",
  "email": "usuario@ejemplo.com",
  "full_name": "Nombre Completo",
  "role": "user",
  "active": true,
  "created_at": "2024-12-01T00:00:00Z"
}
```

### **POST** `/api/auth/login`
Iniciar sesión de usuario.

**Body (form-data):**
```
username: usuario
password: contraseña
```

**Respuesta (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### **POST** `/api/auth/refresh`
Renovar token de acceso usando refresh token.

**Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### **POST** `/api/auth/logout`
Cerrar sesión de usuario.

**Headers:** `Authorization: Bearer <token>`

### **GET** `/api/auth/me`
Obtener información del usuario actual.

**Headers:** `Authorization: Bearer <token>`

### **POST** `/api/auth/change-password`
Cambiar contraseña del usuario actual.

**Headers:** `Authorization: Bearer <token>`  
**Body:**
```json
{
  "current_password": "contraseña_actual",
  "new_password": "nueva_contraseña"
}
```

---

## 👥 **Endpoints de Usuarios**

### **GET** `/api/users/`
Obtener lista de usuarios (solo administradores).

**Headers:** `Authorization: Bearer <admin_token>`  
**Query Parameters:**
- `skip`: Número de registros a omitir (default: 0)
- `limit`: Número máximo de registros (default: 100, max: 1000)
- `search`: Buscar por nombre o email
- `role`: Filtrar por rol
- `active`: Filtrar por estado activo

### **GET** `/api/users/{user_id}`
Obtener usuario por ID.

**Headers:** `Authorization: Bearer <token>`  
**Permisos:** Solo puede ver su propio perfil o ser admin

### **POST** `/api/users/`
Crear nuevo usuario (solo administradores).

**Headers:** `Authorization: Bearer <admin_token>`  
**Body:** Mismo formato que `/api/auth/register`

### **PUT** `/api/users/{user_id}`
Actualizar usuario.

**Headers:** `Authorization: Bearer <token>`  
**Permisos:** Solo puede actualizar su propio perfil o ser admin

### **DELETE** `/api/users/{user_id}`
Eliminar usuario (solo administradores).

**Headers:** `Authorization: Bearer <admin_token>`  
**Nota:** Marca como inactivo en lugar de eliminar físicamente

### **PATCH** `/api/users/{user_id}/activate`
Activar usuario (solo administradores).

### **PATCH** `/api/users/{user_id}/deactivate`
Desactivar usuario (solo administradores).

### **GET** `/api/users/stats/summary`
Obtener estadísticas de usuarios (solo administradores).

---

## 📁 **Endpoints de Proyectos**

### **GET** `/api/projects/`
Obtener lista de proyectos.

**Headers:** `Authorization: Bearer <token>`  
**Query Parameters:**
- `skip`: Número de registros a omitir
- `limit`: Número máximo de registros
- `search`: Buscar por nombre o descripción
- `category`: Filtrar por categoría
- `location`: Filtrar por ubicación
- `status`: Filtrar por estado
- `owner_id`: Filtrar por propietario
- `tags`: Filtrar por etiquetas (separadas por coma)

### **GET** `/api/projects/{project_id}`
Obtener proyecto por ID.

### **POST** `/api/projects/`
Crear nuevo proyecto.

**Body:**
```json
{
  "name": "Nombre del Proyecto",
  "description": "Descripción del proyecto",
  "category": "Tecnología",
  "location": "Bogotá, Colombia",
  "status": "active",
  "tags": ["tag1", "tag2", "tag3"]
}
```

### **PUT** `/api/projects/{project_id}`
Actualizar proyecto.

**Permisos:** Solo el propietario o admin

### **DELETE** `/api/projects/{project_id}`
Eliminar proyecto.

**Permisos:** Solo el propietario o admin

### **GET** `/api/projects/categories`
Obtener categorías únicas de proyectos.

### **GET** `/api/projects/locations`
Obtener ubicaciones únicas de proyectos.

### **GET** `/api/projects/tags`
Obtener etiquetas únicas de proyectos.

### **GET** `/api/projects/stats/summary`
Obtener estadísticas de proyectos.

### **GET** `/api/projects/my-projects`
Obtener proyectos del usuario actual.

---

## 📅 **Endpoints de Actividades**

### **GET** `/api/activities/`
Obtener lista de actividades.

**Query Parameters:**
- `search`: Buscar por título o descripción
- `project_id`: Filtrar por proyecto
- `assignee_id`: Filtrar por asignado
- `status`: Filtrar por estado
- `priority`: Filtrar por prioridad

### **GET** `/api/activities/my-activities`
Obtener actividades asignadas al usuario actual.

### **GET** `/api/activities/project/{project_id}`
Obtener actividades de un proyecto específico.

### **GET** `/api/activities/{activity_id}`
Obtener actividad por ID.

### **POST** `/api/activities/`
Crear nueva actividad.

**Body:**
```json
{
  "title": "Título de la Actividad",
  "description": "Descripción de la actividad",
  "status": "todo",
  "priority": "medium",
  "assignee_id": 1,
  "project_id": 1,
  "start_date": "2024-12-01T00:00:00Z",
  "due_date": "2024-12-31T23:59:59Z"
}
```

**Permisos:** Solo el propietario del proyecto o admin

### **PUT** `/api/activities/{activity_id}`
Actualizar actividad.

**Permisos:** Solo el asignado, propietario del proyecto o admin

### **DELETE** `/api/activities/{activity_id}`
Eliminar actividad.

**Permisos:** Solo el propietario del proyecto o admin

### **PATCH** `/api/activities/{activity_id}/status`
Actualizar solo el estado de una actividad.

**Body:** `"in-progress"`

### **GET** `/api/activities/stats/summary`
Obtener estadísticas de actividades.

---

## 📄 **Endpoints de Documentos**

### **GET** `/api/documents/`
Obtener lista de documentos.

**Query Parameters:**
- `search`: Buscar por nombre o descripción
- `project_id`: Filtrar por proyecto
- `uploader_id`: Filtrar por subidor
- `file_type`: Filtrar por tipo de archivo

### **GET** `/api/documents/project/{project_id}`
Obtener documentos de un proyecto específico.

### **GET** `/api/documents/{document_id}`
Obtener documento por ID.

### **POST** `/api/documents/upload`
Subir nuevo documento.

**Body (form-data):**
```
project_id: 1
name: "Nombre del Documento"
description: "Descripción del documento"
file: [archivo]
```

**Permisos:** Solo el propietario del proyecto o admin

### **GET** `/api/documents/{document_id}/download`
Descargar documento.

### **PUT** `/api/documents/{document_id}`
Actualizar documento.

**Permisos:** Solo el subidor, propietario del proyecto o admin

### **DELETE** `/api/documents/{document_id}`
Eliminar documento.

**Permisos:** Solo el subidor, propietario del proyecto o admin

### **GET** `/api/documents/stats/summary`
Obtener estadísticas de documentos.

### **GET** `/api/documents/file-types`
Obtener tipos de archivo soportados.

---

## 💼 **Endpoints de Business Model Canvas**

### **GET** `/api/business-model-canvas/`
Obtener lista de Business Model Canvas.

### **GET** `/api/business-model-canvas/project/{project_id}`
Obtener BMC de un proyecto específico.

### **POST** `/api/business-model-canvas/`
Crear nuevo BMC.

**Body:**
```json
{
  "project_id": 1,
  "key_partners": ["Partner 1", "Partner 2"],
  "key_activities": ["Activity 1", "Activity 2"],
  "key_resources": ["Resource 1", "Resource 2"],
  "value_propositions": ["Value 1", "Value 2"],
  "customer_relationships": ["Relationship 1"],
  "channels": ["Channel 1", "Channel 2"],
  "customer_segments": ["Segment 1"],
  "cost_structure": ["Cost 1", "Cost 2"],
  "revenue_streams": ["Revenue 1"]
}
```

**Permisos:** Solo el propietario del proyecto o admin

### **PUT** `/api/business-model-canvas/{canvas_id}`
Actualizar BMC.

**Permisos:** Solo el propietario del proyecto o admin

### **PATCH** `/api/business-model-canvas/{canvas_id}/element`
Actualizar un elemento específico del BMC.

**Body:**
```json
{
  "element_name": "key_partners",
  "element_data": ["New Partner 1", "New Partner 2"]
}
```

### **DELETE** `/api/business-model-canvas/{canvas_id}`
Eliminar BMC.

**Permisos:** Solo el propietario del proyecto o admin

### **GET** `/api/business-model-canvas/{canvas_id}/export`
Exportar BMC en diferentes formatos.

**Query Parameters:**
- `format`: Formato de exportación (json, csv)

### **GET** `/api/business-model-canvas/stats/summary`
Obtener estadísticas de BMC.

---

## 🔍 **Endpoints de Búsqueda y Filtros**

### **Filtros Comunes**
- **Paginación**: `skip` y `limit`
- **Búsqueda**: `search` para texto libre
- **Filtros específicos**: Por estado, categoría, tipo, etc.

### **Ordenamiento**
Los endpoints soportan ordenamiento implícito por fecha de creación (más reciente primero).

---

## 📊 **Códigos de Estado HTTP**

- **200**: OK - Operación exitosa
- **201**: Created - Recurso creado exitosamente
- **204**: No Content - Operación exitosa sin contenido
- **400**: Bad Request - Datos de entrada inválidos
- **401**: Unauthorized - Token inválido o expirado
- **403**: Forbidden - Permisos insuficientes
- **404**: Not Found - Recurso no encontrado
- **422**: Unprocessable Entity - Error de validación
- **500**: Internal Server Error - Error interno del servidor

---

## 🚀 **Ejemplos de Uso**

### **Flujo Completo de Autenticación**

```bash
# 1. Registrar usuario
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario_prueba",
    "email": "prueba@ejemplo.com",
    "full_name": "Usuario de Prueba",
    "password": "password123",
    "role": "user"
  }'

# 2. Iniciar sesión
curl -X POST "http://localhost:8000/api/auth/login" \
  -d "username=usuario_prueba&password=password123"

# 3. Usar token para operaciones protegidas
curl -X GET "http://localhost:8000/api/projects/" \
  -H "Authorization: Bearer <access_token>"
```

### **Crear Proyecto con Actividades**

```bash
# 1. Crear proyecto
curl -X POST "http://localhost:8000/api/projects/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Proyecto de Prueba",
    "description": "Descripción del proyecto",
    "category": "Tecnología",
    "location": "Bogotá",
    "status": "active",
    "tags": ["web", "react", "api"]
  }'

# 2. Crear actividad
curl -X POST "http://localhost:8000/api/activities/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Desarrollar Frontend",
    "description": "Crear interfaz de usuario",
    "status": "todo",
    "priority": "high",
    "assignee_id": 1,
    "project_id": 1,
    "start_date": "2024-12-01T00:00:00Z",
    "due_date": "2024-12-15T23:59:59Z"
  }'
```

---

## 🛠️ **Configuración y Despliegue**

### **Variables de Entorno**
```env
DATABASE_URL=mysql://user:password@localhost:3306/innovai_db
SECRET_KEY=tu-clave-secreta-super-segura
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### **Ejecutar en Desarrollo**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m app.main
```

### **Ejecutar Tests**
```bash
pytest tests/
pytest tests/ -v  # Verbose
pytest tests/ --cov=app  # Con cobertura
```

---

## 📝 **Notas Importantes**

1. **Autenticación**: Todos los endpoints protegidos requieren token válido
2. **Permisos**: Verificar permisos antes de realizar operaciones
3. **Validación**: Los datos de entrada son validados automáticamente
4. **Auditoría**: Todas las operaciones son registradas en logs de auditoría
5. **Paginación**: Usar `skip` y `limit` para listas grandes
6. **Filtros**: Aprovechar los filtros para consultas eficientes

---

## 🆘 **Soporte y Contacto**

Para soporte técnico o preguntas sobre la API:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo
- Revisar la documentación interactiva en `/docs` (Swagger UI)

---

**Última actualización**: Diciembre 2024  
**Versión de la API**: 1.0.0

