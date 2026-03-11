import { apiRequest } from './api';
import type { 
  UserAnalytics, 
  RecommendationEngine, 
  AnalyticsEvent, 
  LearningPath, 
  UserInsights, 
  LearningProgress, 
  DashboardData 
} from '../types/dataAnalysis';

// Servicio de análisis de datos
export class DataAnalysisService {
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  // Métodos estáticos para uso directo desde componentes
  private static getToken(): string {
    // Obtener token del localStorage usando la misma clave que AuthContext
    return localStorage.getItem('innexia_token') || '';
  }

  static async getDashboardData(): Promise<DashboardData> {
    const token = DataAnalysisService.getToken();
    if (!token) {
      throw new Error('No hay token de autenticación disponible');
    }
    
    const service = new DataAnalysisService(token);
    return await service.getAnalyticsDashboard();
  }

  static async markRecommendationRead(recommendationId: number): Promise<{ success: boolean; message: string; data: { recommendation_id: number } }> {
    const token = DataAnalysisService.getToken();
    if (!token) {
      throw new Error('No hay token de autenticación disponible');
    }
    
    const service = new DataAnalysisService(token);
    return await service.markRecommendationRead(recommendationId);
  }

  static async markRecommendationApplied(recommendationId: number): Promise<{ success: boolean; message: string; data: { recommendation_id: number } }> {
    const token = DataAnalysisService.getToken();
    if (!token) {
      throw new Error('No hay token de autenticación disponible');
    }
    
    const service = new DataAnalysisService(token);
    return await service.markRecommendationApplied(recommendationId);
  }

  static async trackChatbotInteraction(interactionType: string, messageCount?: number): Promise<{ success: boolean; message: string; data: { event_id: number } }> {
    const token = DataAnalysisService.getToken();
    if (!token) {
      throw new Error('No hay token de autenticación disponible');
    }
    
    const service = new DataAnalysisService(token);
    return await service.trackChatbotInteraction(interactionType, messageCount);
  }

  // Rastrear evento
  async trackEvent(event: Omit<AnalyticsEvent, 'id' | 'user_id' | 'created_at'>): Promise<AnalyticsEvent> {
    const response = await apiRequest<AnalyticsEvent>(
      '/api/data-analysis/track-event',
      {
        method: 'POST',
        body: JSON.stringify(event)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al rastrear evento');
    }

    return response.data!;
  }

  // Obtener analytics del usuario
  async getUserAnalytics(): Promise<UserAnalytics> {
    const response = await apiRequest<UserAnalytics>(
      '/api/data-analysis/analytics',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener analytics');
    }

    return response.data!;
  }

  // Actualizar analytics del usuario
  async updateUserAnalytics(): Promise<UserAnalytics> {
    const response = await apiRequest<UserAnalytics>(
      '/api/data-analysis/analytics/update',
      {
        method: 'POST'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al actualizar analytics');
    }

    return response.data!;
  }

  // Obtener insights del usuario
  async getUserInsights(): Promise<UserInsights> {
    const response = await apiRequest<UserInsights>(
      '/api/data-analysis/insights',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener insights');
    }

    return response.data!;
  }

  // Obtener progreso de aprendizaje
  async getLearningProgress(): Promise<LearningProgress> {
    const response = await apiRequest<LearningProgress>(
      '/api/data-analysis/learning-progress',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener progreso de aprendizaje');
    }

    return response.data!;
  }

  // Generar recomendaciones
  async generateRecommendations(): Promise<RecommendationEngine[]> {
    const response = await apiRequest<RecommendationEngine[]>(
      '/api/data-analysis/recommendations/generate',
      {
        method: 'POST'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al generar recomendaciones');
    }

    return response.data!;
  }

  // Obtener recomendaciones
  async getRecommendations(limit: number = 10): Promise<RecommendationEngine[]> {
    const response = await apiRequest<RecommendationEngine[]>(
      `/api/data-analysis/recommendations?limit=${limit}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener recomendaciones');
    }

    return response.data!;
  }

  // Marcar recomendación como leída
  async markRecommendationRead(recommendationId: number): Promise<{ success: boolean; message: string; data: { recommendation_id: number } }> {
    const response = await apiRequest<{ success: boolean; message: string; data: { recommendation_id: number } }>(
      `/api/data-analysis/recommendations/${recommendationId}/read`,
      {
        method: 'PUT'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al marcar recomendación como leída');
    }

    return response.data!;
  }

  // Marcar recomendación como aplicada
  async markRecommendationApplied(recommendationId: number): Promise<{ success: boolean; message: string; data: { recommendation_id: number } }> {
    const response = await apiRequest<{ success: boolean; message: string; data: { recommendation_id: number } }>(
      `/api/data-analysis/recommendations/${recommendationId}/applied`,
      {
        method: 'PUT'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al marcar recomendación como aplicada');
    }

    return response.data!;
  }

  // Obtener dashboard de analytics
  async getAnalyticsDashboard(): Promise<DashboardData> {
    const response = await apiRequest<DashboardData>(
      '/api/data-analysis/dashboard',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener dashboard');
    }

    return response.data!;
  }

  // Rastrear evento de login
  async trackLoginEvent(): Promise<{ success: boolean; message: string; data: { event_id: number } }> {
    const response = await apiRequest<{ success: boolean; message: string; data: { event_id: number } }>(
      '/api/data-analysis/track-login',
      {
        method: 'POST'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al rastrear evento de login');
    }

    return response.data!;
  }

  // Rastrear evento de visualización de contenido
  async trackContentViewEvent(contentId: number, contentType: string, category?: string): Promise<{ success: boolean; message: string; data: { event_id: number } }> {
    const response = await apiRequest<{ success: boolean; message: string; data: { event_id: number } }>(
      '/api/data-analysis/track-content-view',
      {
        method: 'POST',
        body: JSON.stringify({
          content_id: contentId,
          content_type: contentType,
          category
        })
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al rastrear evento de visualización');
    }

    return response.data!;
  }

  // Rastrear evento de interacción con chatbot
  async trackChatbotInteraction(interactionType: string, messageCount?: number): Promise<{ success: boolean; message: string; data: { event_id: number } }> {
    const response = await apiRequest<{ success: boolean; message: string; data: { event_id: number } }>(
      '/api/data-analysis/track-chatbot-interaction',
      {
        method: 'POST',
        body: JSON.stringify({
          interaction_type: interactionType,
          message_count: messageCount
        })
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al rastrear evento de chatbot');
    }

    return response.data!;
  }

  // Métodos de conveniencia para el chatbot
  async trackChatbotMessage(messageContent: string, intent?: string): Promise<void> {
    await this.trackEvent({
      event_type: 'chatbot_message',
      event_category: 'interaction',
      event_data: {
        message_content: messageContent,
        intent_detected: intent,
        timestamp: new Date().toISOString()
      }
    });
  }

  async trackDocumentGeneration(documentType: string, projectId?: number): Promise<void> {
    await this.trackEvent({
      event_type: 'document_generation',
      event_category: 'business',
      event_data: {
        document_type: documentType,
        project_id: projectId,
        timestamp: new Date().toISOString()
      },
      project_id: projectId
    });
  }

  async trackProjectCreation(projectName: string): Promise<void> {
    await this.trackEvent({
      event_type: 'project_creation',
      event_category: 'business',
      event_data: {
        project_name: projectName,
        timestamp: new Date().toISOString()
      }
    });
  }

  async trackActivityCompletion(activityId: number, projectId?: number): Promise<void> {
    await this.trackEvent({
      event_type: 'activity_completion',
      event_category: 'business',
      event_data: {
        activity_id: activityId,
        timestamp: new Date().toISOString()
      },
      activity_id: activityId,
      project_id: projectId
    });
  }
}

