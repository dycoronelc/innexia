// Ejemplo de uso completo de los servicios de InnovAI
import { InnovAI } from './services';

class InnovAIExample {
  private innovai: InnovAI;

  constructor() {
    // Inicializar InnovAI con token opcional
    this.innovai = new InnovAI();
  }

  // Ejemplo de flujo completo de autenticación
  async authenticationFlow() {
    try {
      console.log('=== Flujo de Autenticación ===');

      // 1. Login del usuario
      const loginResponse = await this.innovai.auth.login({
        email: 'usuario@ejemplo.com',
        password: 'contraseña123'
      });

      console.log('Login exitoso:', loginResponse.user.email);

      // 2. Actualizar token en todos los servicios
      this.innovai.updateToken(loginResponse.access_token);

      // 3. Verificar autenticación
      if (this.innovai.isAuthenticated()) {
        console.log('Usuario autenticado correctamente');
      }

      return loginResponse;
    } catch (error) {
      console.error('Error en autenticación:', error);
      throw error;
    }
  }

  // Ejemplo de interacción con el chatbot
  async chatbotInteraction() {
    try {
      console.log('=== Interacción con Chatbot ===');

      // 1. Enviar mensaje al chatbot
      const chatResponse = await this.innovai.chatbot.sendMessage({
        message: '¿Cómo puedo crear un plan de negocio para mi startup de tecnología?',
        context: {
          user_intent: 'business_plan_creation',
          project_type: 'startup',
          industry: 'technology'
        }
      });

      console.log('Respuesta del chatbot:', chatResponse.message);

      // 2. Obtener historial de chat
      const chatHistory = await this.innovai.chatbot.getChatHistory(chatResponse.session_id);
      console.log('Historial de chat:', chatHistory.length, 'mensajes');

      // 3. Enviar feedback sobre la respuesta
      await this.innovai.chatbot.sendFeedback(chatResponse.session_id, {
        rating: 5,
        feedback_text: 'Muy útil la información proporcionada',
        helpful: true
      });

      return chatResponse;
    } catch (error) {
      console.error('Error en interacción con chatbot:', error);
      throw error;
    }
  }

  // Ejemplo de gestión de proyectos
  async projectManagement() {
    try {
      console.log('=== Gestión de Proyectos ===');

      // 1. Crear nuevo proyecto
      const newProject = await this.innovai.project.createProject({
        name: 'Mi Startup de IA',
        description: 'Una startup innovadora en el campo de la inteligencia artificial',
        project_type: 'startup',
        industry: 'technology',
        business_model: 'SaaS',
        target_market: 'Empresas medianas',
        budget_range: '50k-100k',
        timeline: '6-12 meses',
        status: 'active',
        priority: 'high'
      });

      console.log('Proyecto creado:', newProject.name);

      // 2. Obtener templates de proyecto
      const templates = await this.innovai.project.getProjectTemplates('startup', 'technology');
      console.log('Templates disponibles:', templates.length);

      // 3. Crear actividad en el proyecto
      const activity = await this.innovai.project.createActivity(newProject.id, {
        activity_type: 'market_research',
        title: 'Investigación de mercado',
        description: 'Analizar el mercado objetivo y competencia',
        status: 'pending',
        priority: 'high',
        difficulty_level: 'intermediate',
        estimated_duration: 120, // minutos
        due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString() // 7 días
      });

      console.log('Actividad creada:', activity.title);

      // 4. Completar actividad
      await this.innovai.project.completeActivity(activity.id, 'Investigación completada exitosamente');

      return newProject;
    } catch (error) {
      console.error('Error en gestión de proyectos:', error);
      throw error;
    }
  }

  // Ejemplo de generación de documentos
  async documentGeneration() {
    try {
      console.log('=== Generación de Documentos ===');

      // 1. Obtener templates de documentos
      const documentTemplates = await this.innovai.document.getDocumentTemplates('business_plan');
      console.log('Templates de documentos disponibles:', documentTemplates.length);

      // 2. Generar plan de negocio
      const businessPlan = await this.innovai.document.generateBusinessPlan(1); // projectId
      console.log('Plan de negocio generado:', businessPlan.title);

      // 3. Generar proyección financiera
      const financialProjection = await this.innovai.document.generateFinancialProjection(1);
      console.log('Proyección financiera generada:', financialProjection.title);

      // 4. Generar plan de marketing
      const marketingPlan = await this.innovai.document.generateMarketingPlan(1);
      console.log('Plan de marketing generado:', marketingPlan.title);

      // 5. Exportar documento
      const exportResult = await this.innovai.document.exportDocument(businessPlan.id, 'pdf');
      console.log('Documento exportado:', exportResult.export_url);

      return { businessPlan, financialProjection, marketingPlan };
    } catch (error) {
      console.error('Error en generación de documentos:', error);
      throw error;
    }
  }

  // Ejemplo de análisis de datos
  async dataAnalysis() {
    try {
      console.log('=== Análisis de Datos ===');

      // 1. Obtener analytics del usuario
      const userAnalytics = await this.innovai.dataAnalysis.getUserAnalytics();
      console.log('Analytics del usuario:', {
        login_frequency: userAnalytics.login_frequency,
        project_completion_rate: userAnalytics.project_completion_rate,
        activity_completion_rate: userAnalytics.activity_completion_rate
      });

      // 2. Generar recomendaciones
      const recommendations = await this.innovai.dataAnalysis.generateRecommendations();
      console.log('Recomendaciones generadas:', recommendations.length);

      // 3. Obtener insights del usuario
      const userInsights = await this.innovai.dataAnalysis.getUserInsights();
      console.log('Insights del usuario:', {
        strengths: userInsights.strengths,
        improvement_areas: userInsights.improvement_areas
      });

      // 4. Obtener progreso de aprendizaje
      const learningProgress = await this.innovai.dataAnalysis.getLearningProgress();
      console.log('Progreso de aprendizaje:', {
        overall_progress: learningProgress.overall_progress,
        next_recommendations: learningProgress.next_recommendations
      });

      // 5. Rastrear eventos
      await this.innovai.dataAnalysis.trackProjectCreation('Mi Startup de IA');
      await this.innovai.dataAnalysis.trackDocumentGeneration('business_plan', 1);

      return { userAnalytics, recommendations, userInsights, learningProgress };
    } catch (error) {
      console.error('Error en análisis de datos:', error);
      throw error;
    }
  }

  // Ejemplo de gestión de contenido
  async contentManagement() {
    try {
      console.log('=== Gestión de Contenido ===');

      // 1. Buscar contenido relacionado
      const searchResult = await this.innovai.content.searchContent({
        search_query: 'startup funding',
        category: 'business',
        difficulty_level: 'intermediate',
        is_featured: true
      });

      console.log('Contenido encontrado:', searchResult.content.length, 'elementos');

      // 2. Obtener contenido destacado
      const featuredContent = await this.innovai.content.getFeaturedContent(5);
      console.log('Contenido destacado:', featuredContent.length, 'elementos');

      // 3. Obtener módulos de aprendizaje
      const learningModules = await this.innovai.content.getLearningModules('business');
      console.log('Módulos de aprendizaje:', learningModules.length, 'módulos');

      // 4. Obtener recomendaciones de contenido
      const contentRecommendations = await this.innovai.content.getContentRecommendations(3);
      console.log('Recomendaciones de contenido:', contentRecommendations.length);

      return { searchResult, featuredContent, learningModules, contentRecommendations };
    } catch (error) {
      console.error('Error en gestión de contenido:', error);
      throw error;
    }
  }

  // Ejemplo de gestión de usuario
  async userManagement() {
    try {
      console.log('=== Gestión de Usuario ===');

      // 1. Obtener perfil actual
      const currentUser = await this.innovai.user.getCurrentUser();
      console.log('Usuario actual:', currentUser.email);

      // 2. Obtener perfil de negocio
      const businessProfile = await this.innovai.user.getBusinessProfile();
      console.log('Perfil de negocio:', {
        business_name: businessProfile.business_name,
        industry: businessProfile.industry,
        role: businessProfile.role
      });

      // 3. Actualizar perfil de negocio
      await this.innovai.user.updateBusinessProfile({
        business_name: 'InnovAI Solutions',
        industry: 'technology',
        company_size: '10-50',
        role: 'founder',
        experience_level: 'intermediate',
        goals: ['expand business', 'increase revenue', 'hire team'],
        interests: ['artificial intelligence', 'machine learning', 'startups'],
        skills: ['project management', 'business development', 'marketing']
      });

      // 4. Obtener estadísticas del usuario
      const userStats = await this.innovai.user.getUserStats();
      console.log('Estadísticas del usuario:', {
        total_projects: userStats.total_projects,
        completed_projects: userStats.completed_projects,
        days_active: userStats.days_active
      });

      // 5. Obtener actividad del usuario
      const userActivity = await this.innovai.user.getUserActivity(10);
      console.log('Actividad reciente:', userActivity.length, 'actividades');

      return { currentUser, businessProfile, userStats, userActivity };
    } catch (error) {
      console.error('Error en gestión de usuario:', error);
      throw error;
    }
  }

  // Ejemplo de gestión de notificaciones
  async notificationManagement() {
    try {
      console.log('=== Gestión de Notificaciones ===');

      // 1. Obtener notificaciones no leídas
      const unreadNotifications = await this.innovai.notification.getUnreadNotifications();
      console.log('Notificaciones no leídas:', unreadNotifications.length);

      // 2. Obtener notificaciones de alta prioridad
      const highPriorityNotifications = await this.innovai.notification.getHighPriorityNotifications();
      console.log('Notificaciones de alta prioridad:', highPriorityNotifications.length);

      // 3. Marcar notificación como leída
      if (unreadNotifications.length > 0) {
        await this.innovai.notification.markNotificationRead(unreadNotifications[0].id);
        console.log('Notificación marcada como leída');
      }

      // 4. Obtener preferencias de notificación
      const preferences = await this.innovai.notification.getNotificationPreferences();
      console.log('Preferencias de notificación:', preferences.length, 'tipos');

      // 5. Obtener canales de notificación
      const channels = await this.innovai.notification.getNotificationChannels();
      console.log('Canales de notificación:', channels.length, 'canales');

      return { unreadNotifications, highPriorityNotifications, preferences, channels };
    } catch (error) {
      console.error('Error en gestión de notificaciones:', error);
      throw error;
    }
  }

  // Ejemplo de flujo completo de la aplicación
  async completeApplicationFlow() {
    try {
      console.log('🚀 Iniciando flujo completo de InnovAI...\n');

      // 1. Autenticación
      await this.authenticationFlow();
      console.log('✅ Autenticación completada\n');

      // 2. Gestión de usuario
      await this.userManagement();
      console.log('✅ Gestión de usuario completada\n');

      // 3. Interacción con chatbot
      await this.chatbotInteraction();
      console.log('✅ Interacción con chatbot completada\n');

      // 4. Gestión de proyectos
      const project = await this.projectManagement();
      console.log('✅ Gestión de proyectos completada\n');

      // 5. Generación de documentos
      await this.documentGeneration();
      console.log('✅ Generación de documentos completada\n');

      // 6. Análisis de datos
      await this.dataAnalysis();
      console.log('✅ Análisis de datos completado\n');

      // 7. Gestión de contenido
      await this.contentManagement();
      console.log('✅ Gestión de contenido completada\n');

      // 8. Gestión de notificaciones
      await this.notificationManagement();
      console.log('✅ Gestión de notificaciones completada\n');

      console.log('🎉 ¡Flujo completo de InnovAI ejecutado exitosamente!');
      
      return {
        success: true,
        message: 'Flujo completo ejecutado correctamente',
        project: project
      };
    } catch (error) {
      console.error('❌ Error en el flujo completo:', error);
      throw error;
    }
  }

  // Método para limpiar recursos
  async cleanup() {
    try {
      console.log('🧹 Limpiando recursos...');
      
      // Limpiar token
      this.innovai.clearToken();
      
      console.log('✅ Recursos limpiados');
    } catch (error) {
      console.error('❌ Error al limpiar recursos:', error);
    }
  }
}

// Función para ejecutar el ejemplo
async function runInnovAIExample() {
  const example = new InnovAIExample();
  
  try {
    // Ejecutar flujo completo
    await example.completeApplicationFlow();
  } catch (error) {
    console.error('Error en el ejemplo:', error);
  } finally {
    // Limpiar recursos
    await example.cleanup();
  }
}

// Exportar para uso en otros archivos
export { InnovAIExample, runInnovAIExample };

// Ejecutar si este archivo se ejecuta directamente
if (typeof window !== 'undefined' && window.location) {
  // En el navegador, agregar al objeto window para debugging
  (window as any).InnovAIExample = InnovAIExample;
  (window as any).runInnovAIExample = runInnovAIExample;
}

