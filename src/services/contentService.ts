import { apiRequest } from './api';

// Tipos para gestión de contenido
export interface ContentItem {
  id: number;
  title: string;
  description?: string;
  content_type: string;
  category?: string;
  subcategory?: string;
  difficulty_level: string;
  content_data: any;
  metadata?: any;
  tags?: string[];
  is_active: boolean;
  is_featured: boolean;
  view_count: number;
  rating?: number;
  author?: string;
  created_at: string;
  updated_at?: string;
  published_at?: string;
}

export interface ContentCategory {
  id: number;
  name: string;
  description?: string;
  icon?: string;
  color?: string;
  parent_category_id?: number;
  subcategories?: ContentCategory[];
  content_count: number;
  is_active: boolean;
  created_at: string;
}

export interface LearningModule {
  id: number;
  title: string;
  description?: string;
  category: string;
  difficulty_level: string;
  estimated_duration: number;
  content_items: ContentItem[];
  prerequisites?: string[];
  learning_objectives?: string[];
  is_active: boolean;
  is_completed?: boolean;
  progress_percentage?: number;
  created_at: string;
  updated_at?: string;
}

export interface UserContentProgress {
  id: number;
  user_id: number;
  content_id: number;
  content_type: string;
  progress_percentage: number;
  time_spent: number;
  is_completed: boolean;
  completed_at?: string;
  rating?: number;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface ContentRecommendation {
  id: number;
  user_id: number;
  content_id: number;
  recommendation_type: string;
  priority: number;
  reasoning?: string;
  is_active: boolean;
  is_viewed: boolean;
  created_at: string;
}

export interface ContentSearchFilters {
  category?: string;
  subcategory?: string;
  content_type?: string;
  difficulty_level?: string;
  tags?: string[];
  is_featured?: boolean;
  author?: string;
  min_rating?: number;
  search_query?: string;
}

// Servicio de gestión de contenido
export class ContentService {
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  // Obtener contenido por ID
  async getContentById(contentId: number): Promise<ContentItem> {
    const response = await apiRequest<ContentItem>(
      `/api/content/${contentId}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener contenido');
    }

    return response.data!;
  }

  // Obtener contenido por categoría
  async getContentByCategory(category: string, limit: number = 20, offset: number = 0): Promise<ContentItem[]> {
    const response = await apiRequest<ContentItem[]>(
      `/api/content/category/${category}?limit=${limit}&offset=${offset}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener contenido por categoría');
    }

    return response.data!;
  }

  // Buscar contenido
  async searchContent(filters: ContentSearchFilters, limit: number = 20, offset: number = 0): Promise<{
    content: ContentItem[];
    total_count: number;
    has_more: boolean;
  }> {
    const queryParams = new URLSearchParams();
    
    if (filters.category) queryParams.append('category', filters.category);
    if (filters.subcategory) queryParams.append('subcategory', filters.subcategory);
    if (filters.content_type) queryParams.append('content_type', filters.content_type);
    if (filters.difficulty_level) queryParams.append('difficulty_level', filters.difficulty_level);
    if (filters.tags) filters.tags.forEach(tag => queryParams.append('tags', tag));
    if (filters.is_featured !== undefined) queryParams.append('is_featured', filters.is_featured.toString());
    if (filters.author) queryParams.append('author', filters.author);
    if (filters.min_rating) queryParams.append('min_rating', filters.min_rating.toString());
    if (filters.search_query) queryParams.append('search_query', filters.search_query);
    
    queryParams.append('limit', limit.toString());
    queryParams.append('offset', offset.toString());

    const response = await apiRequest<{
      content: ContentItem[];
      total_count: number;
      has_more: boolean;
    }>(
      `/api/content/search?${queryParams.toString()}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al buscar contenido');
    }

    return response.data!;
  }

  // Obtener contenido destacado
  async getFeaturedContent(limit: number = 10): Promise<ContentItem[]> {
    const response = await apiRequest<ContentItem[]>(
      `/api/content/featured?limit=${limit}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener contenido destacado');
    }

    return response.data!;
  }

  // Obtener contenido relacionado
  async getRelatedContent(contentId: number, limit: number = 5): Promise<ContentItem[]> {
    const response = await apiRequest<ContentItem[]>(
      `/api/content/${contentId}/related?limit=${limit}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener contenido relacionado');
    }

    return response.data!;
  }

  // Obtener categorías
  async getCategories(): Promise<ContentCategory[]> {
    const response = await apiRequest<ContentCategory[]>(
      '/api/content/categories',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener categorías');
    }

    return response.data!;
  }

  // Obtener módulos de aprendizaje
  async getLearningModules(category?: string): Promise<LearningModule[]> {
    const url = category 
      ? `/api/content/learning-modules?category=${category}`
      : '/api/content/learning-modules';
    
    const response = await apiRequest<LearningModule[]>(
      url,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener módulos de aprendizaje');
    }

    return response.data!;
  }

  // Obtener módulo de aprendizaje por ID
  async getLearningModuleById(moduleId: number): Promise<LearningModule> {
    const response = await apiRequest<LearningModule>(
      `/api/content/learning-modules/${moduleId}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener módulo de aprendizaje');
    }

    return response.data!;
  }

  // Obtener progreso del usuario en contenido
  async getUserContentProgress(contentId?: number): Promise<UserContentProgress[]> {
    const url = contentId 
      ? `/api/content/progress?content_id=${contentId}`
      : '/api/content/progress';
    
    const response = await apiRequest<UserContentProgress[]>(
      url,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener progreso de contenido');
    }

    return response.data!;
  }

  // Actualizar progreso de contenido
  async updateContentProgress(contentId: number, progress: {
    progress_percentage: number;
    time_spent?: number;
    is_completed?: boolean;
    rating?: number;
    notes?: string;
  }): Promise<UserContentProgress> {
    const response = await apiRequest<UserContentProgress>(
      `/api/content/${contentId}/progress`,
      {
        method: 'PUT',
        body: JSON.stringify(progress)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al actualizar progreso');
    }

    return response.data!;
  }

  // Marcar contenido como completado
  async markContentCompleted(contentId: number, rating?: number, notes?: string): Promise<UserContentProgress> {
    const response = await apiRequest<UserContentProgress>(
      `/api/content/${contentId}/complete`,
      {
        method: 'POST',
        body: JSON.stringify({
          rating,
          notes,
          completed_at: new Date().toISOString()
        })
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al marcar contenido como completado');
    }

    return response.data!;
  }

  // Obtener recomendaciones de contenido
  async getContentRecommendations(limit: number = 10): Promise<ContentRecommendation[]> {
    const response = await apiRequest<ContentRecommendation[]>(
      `/api/content/recommendations?limit=${limit}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener recomendaciones de contenido');
    }

    return response.data!;
  }

  // Marcar recomendación como vista
  async markRecommendationViewed(recommendationId: number): Promise<{ success: boolean; message: string }> {
    const response = await apiRequest<{ success: boolean; message: string }>(
      `/api/content/recommendations/${recommendationId}/view`,
      {
        method: 'PUT'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al marcar recomendación como vista');
    }

    return response.data!;
  }

  // Obtener contenido para chatbot
  async getChatbotContent(query: string, category?: string, limit: number = 5): Promise<ContentItem[]> {
    const queryParams = new URLSearchParams();
    queryParams.append('query', query);
    if (category) queryParams.append('category', category);
    queryParams.append('limit', limit.toString());

    const response = await apiRequest<ContentItem[]>(
      `/api/content/chatbot-search?${queryParams.toString()}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al buscar contenido para chatbot');
    }

    return response.data!;
  }

  // Obtener contenido por tipo
  async getContentByType(contentType: string, limit: number = 20, offset: number = 0): Promise<ContentItem[]> {
    const response = await apiRequest<ContentItem[]>(
      `/api/content/type/${contentType}?limit=${limit}&offset=${offset}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener contenido por tipo');
    }

    return response.data!;
  }

  // Obtener contenido popular
  async getPopularContent(limit: number = 10): Promise<ContentItem[]> {
    const response = await apiRequest<ContentItem[]>(
      `/api/content/popular?limit=${limit}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener contenido popular');
    }

    return response.data!;
  }

  // Obtener contenido reciente
  async getRecentContent(limit: number = 10): Promise<ContentItem[]> {
    const response = await apiRequest<ContentItem[]>(
      `/api/content/recent?limit=${limit}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener contenido reciente');
    }

    return response.data!;
  }

  // Métodos de conveniencia para el chatbot
  async getBusinessContent(query: string): Promise<ContentItem[]> {
    return this.getChatbotContent(query, 'business', 3);
  }

  async getMarketingContent(query: string): Promise<ContentItem[]> {
    return this.getChatbotContent(query, 'marketing', 3);
  }

  async getFinancialContent(query: string): Promise<ContentItem[]> {
    return this.getChatbotContent(query, 'financial', 3);
  }

  async getLegalContent(query: string): Promise<ContentItem[]> {
    return this.getChatbotContent(query, 'legal', 3);
  }

  async getTechnologyContent(query: string): Promise<ContentItem[]> {
    return this.getChatbotContent(query, 'technology', 3);
  }
}

