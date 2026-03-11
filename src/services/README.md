# InnovAI Services

Este directorio contiene todos los servicios de la aplicación InnovAI para el frontend. Cada servicio maneja una funcionalidad específica y se comunica con el backend a través de la API.

## Estructura de Servicios

### 1. AuthService (`authService.ts`)
Maneja la autenticación y autorización de usuarios.

**Funcionalidades principales:**
- Login y registro de usuarios
- Verificación de email
- Recuperación de contraseña
- Gestión de tokens JWT
- Logout

**Ejemplo de uso:**
```typescript
import { AuthService } from './services';

const auth = new AuthService();

// Login
const response = await auth.login({
  email: 'usuario@ejemplo.com',
  password: 'contraseña123'
});

// Verificar token
const isValid = await auth.verifyToken(token);
```

### 2. ChatbotService (`chatbotService.ts`)
Gestiona las interacciones con el chatbot de IA.

**Funcionalidades principales:**
- Envío de mensajes al chatbot
- Gestión de sesiones de chat
- Análisis de contexto
- Historial de conversaciones
- Feedback y calificaciones

**Ejemplo de uso:**
```typescript
import { ChatbotService } from './services';

const chatbot = new ChatbotService(token);

// Enviar mensaje
const response = await chatbot.sendMessage({
  message: '¿Cómo puedo crear un plan de negocio?',
  context: { project_id: 123 }
});

// Obtener historial
const history = await chatbot.getChatHistory(sessionId);
```

### 3. DataAnalysisService (`dataAnalysisService.ts`)
Maneja el análisis de datos y recomendaciones personalizadas.

**Funcionalidades principales:**
- Analytics del usuario
- Generación de recomendaciones
- Insights personalizados
- Progreso de aprendizaje
- Tracking de eventos

**Ejemplo de uso:**
```typescript
import { DataAnalysisService } from './services';

const analytics = new DataAnalysisService(token);

// Obtener analytics del usuario
const userAnalytics = await analytics.getUserAnalytics();

// Generar recomendaciones
const recommendations = await analytics.generateRecommendations();

// Rastrear evento
await analytics.trackEvent({
  event_type: 'project_creation',
  event_category: 'business'
});
```

### 4. ContentService (`contentService.ts`)
Gestiona el contenido educativo y de aprendizaje.

**Funcionalidades principales:**
- Búsqueda y filtrado de contenido
- Módulos de aprendizaje
- Progreso del usuario
- Recomendaciones de contenido
- Categorías y tags

**Ejemplo de uso:**
```typescript
import { ContentService } from './services';

const content = new ContentService(token);

// Buscar contenido
const searchResult = await content.searchContent({
  search_query: 'marketing digital',
  category: 'business',
  difficulty_level: 'intermediate'
});

// Obtener módulos de aprendizaje
const modules = await content.getLearningModules('business');
```

### 5. UserService (`userService.ts`)
Maneja la gestión de perfiles y configuraciones de usuario.

**Funcionalidades principales:**
- Perfil del usuario
- Configuraciones
- Actividad del usuario
- Sesiones activas
- Suscripciones
- Notificaciones

**Ejemplo de uso:**
```typescript
import { UserService } from './services';

const user = new UserService(token);

// Obtener perfil actual
const profile = await user.getCurrentUser();

// Actualizar perfil de negocio
await user.updateBusinessProfile({
  business_name: 'Mi Empresa',
  industry: 'technology'
});

// Obtener estadísticas
const stats = await user.getUserStats();
```

### 6. ProjectService (`projectService.ts`)
Gestiona los proyectos de negocio del usuario.

**Funcionalidades principales:**
- Creación y gestión de proyectos
- Actividades del proyecto
- Documentos del proyecto
- Colaboradores
- Templates de proyecto

**Ejemplo de uso:**
```typescript
import { ProjectService } from './services';

const project = new ProjectService(token);

// Crear nuevo proyecto
const newProject = await project.createProject({
  name: 'Mi Startup',
  project_type: 'startup',
  industry: 'technology'
});

// Obtener actividades
const activities = await project.getProjectActivities(projectId);

// Completar actividad
await project.completeActivity(activityId, 'Actividad completada exitosamente');
```

### 7. DocumentService (`documentService.ts`)
Maneja la creación y gestión de documentos de negocio.

**Funcionalidades principales:**
- Creación de documentos
- Templates de documentos
- Versiones de documentos
- Colaboración en documentos
- Exportación de documentos

**Ejemplo de uso:**
```typescript
import { DocumentService } from './services';

const document = new DocumentService(token);

// Crear documento desde template
const businessPlan = await document.createDocumentFromTemplate(templateId, {
  title: 'Plan de Negocio - Mi Startup',
  project_id: 123
});

// Generar plan de negocio
const plan = await document.generateBusinessPlan(projectId);

// Exportar documento
const exportResult = await document.exportDocument(documentId, 'pdf');
```

### 8. NotificationService (`notificationService.ts`)
Gestiona las notificaciones del sistema.

**Funcionalidades principales:**
- Notificaciones del usuario
- Preferencias de notificación
- Canales de notificación
- Notificaciones programadas
- Templates de notificación

**Ejemplo de uso:**
```typescript
import { NotificationService } from './services';

const notification = new NotificationService(token);

// Obtener notificaciones no leídas
const unread = await notification.getUnreadNotifications();

// Marcar como leída
await notification.markNotificationRead(notificationId);

// Obtener preferencias
const preferences = await notification.getNotificationPreferences();
```

## Clase Principal: InnovAI

La clase `InnovAI` proporciona una interfaz unificada para todos los servicios:

```typescript
import { InnovAI } from './services';

// Inicializar con token opcional
const innovai = new InnovAI();

// O usar con token específico
const innovai = new InnovAI('your-token-here');

// Acceder a servicios
const user = await innovai.user.getCurrentUser();
const projects = await innovai.project.getProjects();
const chatResponse = await innovai.chatbot.sendMessage({ message: 'Hola' });

// Actualizar token
innovai.updateToken('new-token');

// Verificar autenticación
if (innovai.isAuthenticated()) {
  // Usuario autenticado
}
```

## Configuración

### Variables de Entorno
Asegúrate de tener configuradas las siguientes variables de entorno:

```env
REACT_APP_API_BASE_URL=http://localhost:8001
REACT_APP_CHATBOT_API_URL=http://localhost:8001/api/chatbot
```

### Configuración de la API
Los servicios utilizan la función `apiRequest` del archivo `api.ts` para todas las comunicaciones HTTP. Esta función maneja:

- Headers de autorización
- Manejo de errores
- Transformación de respuestas
- Timeouts
- Retry logic

## Manejo de Errores

Todos los servicios lanzan errores cuando las operaciones fallan:

```typescript
try {
  const user = await innovai.user.getCurrentUser();
} catch (error) {
  console.error('Error al obtener usuario:', error.message);
  // Manejar el error apropiadamente
}
```

## Tipos TypeScript

Todos los servicios incluyen tipos TypeScript completos para:

- Parámetros de entrada
- Respuestas de la API
- Estados de objetos
- Configuraciones

Esto proporciona autocompletado y verificación de tipos en tiempo de desarrollo.

## Mejores Prácticas

1. **Manejo de Tokens**: Siempre usa el método `updateToken()` para actualizar el token en todos los servicios.

2. **Error Handling**: Implementa try-catch blocks para manejar errores de red y de API.

3. **Loading States**: Usa estados de carga para mejorar la experiencia del usuario.

4. **Caching**: Considera implementar caché para datos que no cambian frecuentemente.

5. **Retry Logic**: Para operaciones críticas, implementa lógica de reintento.

## Ejemplo Completo

```typescript
import { InnovAI } from './services';

class App {
  private innovai: InnovAI;

  constructor() {
    this.innovai = new InnovAI();
  }

  async initialize() {
    try {
      // Verificar si el usuario está autenticado
      if (this.innovai.isAuthenticated()) {
        // Cargar datos del usuario
        const user = await this.innovai.user.getCurrentUser();
        
        // Cargar proyectos activos
        const projects = await this.innovai.project.getActiveProjects();
        
        // Cargar notificaciones no leídas
        const notifications = await this.innovai.notification.getUnreadNotifications();
        
        console.log('Aplicación inicializada:', { user, projects, notifications });
      } else {
        console.log('Usuario no autenticado');
      }
    } catch (error) {
      console.error('Error al inicializar:', error);
    }
  }

  async sendChatMessage(message: string) {
    try {
      const response = await this.innovai.chatbot.sendMessage({
        message,
        context: { timestamp: new Date().toISOString() }
      });
      
      return response;
    } catch (error) {
      console.error('Error al enviar mensaje:', error);
      throw error;
    }
  }
}
```

## Contribución

Al agregar nuevos servicios o modificar existentes:

1. Mantén la consistencia en el naming
2. Incluye tipos TypeScript completos
3. Documenta las funciones principales
4. Agrega ejemplos de uso
5. Actualiza este README si es necesario

