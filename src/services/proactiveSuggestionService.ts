import { apiRequest } from './api';

// Tipos para sugerencias proactivas
export interface ProactiveSuggestion {
  id: number;
  user_id: number;
  suggestion_type: string;
  category?: string;
  priority: number;
  title: string;
  description?: string;
  reasoning?: string;
  expected_impact?: number;
  data_sources?: string[];
  confidence_score?: number;
  action_url?: string;
  action_type?: string;
  is_active: boolean;
  is_read: boolean;
  is_dismissed: boolean;
  is_applied: boolean;
  created_at: string;
  expires_at?: string;
  read_at?: string;
  dismissed_at?: string;
  applied_at?: string;
}

export interface SuggestionRule {
  id: number;
  rule_name: string;
  rule_type: string;
  conditions: any;
  suggestion_template: any;
  is_active: boolean;
  created_at: string;
}

export interface UserSuggestionPreference {
  id: number;
  user_id: number;
  notification_frequency: string;
  preferred_categories: string[];
  excluded_categories: string[];
  priority_threshold: number;
  max_suggestions_per_day: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface SuggestionInsight {
  total_suggestions: number;
  read_suggestions: number;
  applied_suggestions: number;
  dismissed_suggestions: number;
  average_priority: number;
  most_effective_category: string;
  suggestion_effectiveness: number;
  generated_at: string;
}

// Servicio de sugerencias proactivas
export class ProactiveSuggestionService {
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  // Métodos estáticos para uso directo desde componentes
  private static getToken(): string {
    // Obtener token del localStorage o contexto de autenticación
    return localStorage.getItem('authToken') || '';
  }

  static async getDashboardSuggestions(): Promise<ProactiveSuggestion[]> {
    const token = ProactiveSuggestionService.getToken();
    if (!token) {
      throw new Error('No hay token de autenticación disponible');
    }
    
    const service = new ProactiveSuggestionService(token);
    return await service.getSuggestions(10);
  }

  static async markAsRead(suggestionId: number): Promise<{ success: boolean; message: string; data: { suggestion_id: number } }> {
    const token = ProactiveSuggestionService.getToken();
    if (!token) {
      throw new Error('No hay token de autenticación disponible');
    }
    
    const service = new ProactiveSuggestionService(token);
    return await service.markSuggestionRead(suggestionId);
  }

  static async dismissSuggestion(suggestionId: number): Promise<{ success: boolean; message: string; data: { suggestion_id: number } }> {
    const token = ProactiveSuggestionService.getToken();
    if (!token) {
      throw new Error('No hay token de autenticación disponible');
    }
    
    const service = new ProactiveSuggestionService(token);
    return await service.dismissSuggestion(suggestionId);
  }

  // Crear sugerencia
  async createSuggestion(suggestion: Omit<ProactiveSuggestion, 'id' | 'user_id' | 'created_at' | 'read_at' | 'dismissed_at' | 'applied_at'>): Promise<ProactiveSuggestion> {
    const response = await apiRequest<ProactiveSuggestion>(
      '/api/proactive-suggestions/',
      {
        method: 'POST',
        body: JSON.stringify(suggestion)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al crear sugerencia');
    }

    return response.data!;
  }

  // Obtener sugerencias
  async getSuggestions(query: {
    suggestion_type?: string;
    category?: string;
    priority_min?: number;
    is_read?: boolean;
    is_dismissed?: boolean;
    limit?: number;
  } = {}): Promise<ProactiveSuggestion[]> {
    const params = new URLSearchParams();
    if (query.suggestion_type) params.append('suggestion_type', query.suggestion_type);
    if (query.category) params.append('category', query.category);
    if (query.priority_min) params.append('priority_min', query.priority_min.toString());
    if (query.is_read !== undefined) params.append('is_read', query.is_read.toString());
    if (query.is_dismissed !== undefined) params.append('is_dismissed', query.is_dismissed.toString());
    if (query.limit) params.append('limit', query.limit.toString());

    const response = await apiRequest<ProactiveSuggestion[]>(
      `/api/proactive-suggestions/?${params.toString()}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener sugerencias');
    }

    return response.data!;
  }

  // Obtener sugerencias no leídas
  async getUnreadSuggestions(): Promise<ProactiveSuggestion[]> {
    const response = await apiRequest<ProactiveSuggestion[]>(
      '/api/proactive-suggestions/unread',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener sugerencias no leídas');
    }

    return response.data!;
  }

  // Marcar sugerencia como leída
  async markAsRead(suggestionId: number): Promise<ProactiveSuggestion> {
    const response = await apiRequest<ProactiveSuggestion>(
      `/api/proactive-suggestions/${suggestionId}/read`,
      {
        method: 'PUT'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al marcar como leída');
    }

    return response.data!;
  }

  // Descartar sugerencia
  async dismissSuggestion(suggestionId: number): Promise<ProactiveSuggestion> {
    const response = await apiRequest<ProactiveSuggestion>(
      `/api/proactive-suggestions/${suggestionId}/dismiss`,
      {
        method: 'PUT'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al descartar sugerencia');
    }

    return response.data!;
  }

  // Obtener insights de sugerencias
  async getSuggestionInsights(): Promise<SuggestionInsight> {
    const response = await apiRequest<SuggestionInsight>(
      '/api/proactive-suggestions/insights',
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

  // Obtener preferencias del usuario
  async getUserPreferences(): Promise<UserSuggestionPreference> {
    const response = await apiRequest<UserSuggestionPreference>(
      '/api/proactive-suggestions/preferences',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener preferencias');
    }

    return response.data!;
  }

  // Actualizar preferencias del usuario
  async updateUserPreferences(preferences: Partial<UserSuggestionPreference>): Promise<UserSuggestionPreference> {
    const response = await apiRequest<UserSuggestionPreference>(
      '/api/proactive-suggestions/preferences',
      {
        method: 'PUT',
        body: JSON.stringify(preferences)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al actualizar preferencias');
    }

    return response.data!;
  }

  // Generar sugerencias de proyecto
  async generateProjectSuggestions(): Promise<ProactiveSuggestion[]> {
    const response = await apiRequest<ProactiveSuggestion[]>(
      '/api/proactive-suggestions/generate/project',
      {
        method: 'POST'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al generar sugerencias de proyecto');
    }

    return response.data!;
  }

  // Generar sugerencias de aprendizaje
  async generateLearningSuggestions(): Promise<ProactiveSuggestion[]> {
    const response = await apiRequest<ProactiveSuggestion[]>(
      '/api/proactive-suggestions/generate/learning',
      {
        method: 'POST'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al generar sugerencias de aprendizaje');
    }

    return response.data!;
  }

  // Generar sugerencias basadas en tiempo
  async generateTimeBasedSuggestions(): Promise<ProactiveSuggestion[]> {
    const response = await apiRequest<ProactiveSuggestion[]>(
      '/api/proactive-suggestions/generate/time-based',
      {
        method: 'POST'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al generar sugerencias basadas en tiempo');
    }

    return response.data!;
  }

  // Generar todas las sugerencias
  async generateAllSuggestions(): Promise<ProactiveSuggestion[]> {
    const response = await apiRequest<ProactiveSuggestion[]>(
      '/api/proactive-suggestions/generate/all',
      {
        method: 'POST'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al generar todas las sugerencias');
    }

    return response.data!;
  }

  // Limpiar sugerencias expiradas
  async cleanupExpiredSuggestions(): Promise<{ message: string }> {
    const response = await apiRequest<{ message: string }>(
      '/api/proactive-suggestions/cleanup',
      {
        method: 'POST'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al limpiar sugerencias');
    }

    return response.data!;
  }
}
