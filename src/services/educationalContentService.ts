import { apiClient } from './api';

export interface EducationalContent {
  id: number;
  title: string;
  description?: string;
  content_type: 'article' | 'video' | 'podcast' | 'infographic' | 'course' | 'webinar';
  content_source: 'internal' | 'rss_feed' | 'youtube' | 'vimeo' | 'spotify' | 'custom_api';
  source_url?: string;
  content_data?: any;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration_minutes?: number;
  author?: string;
  instructor?: string;
  thumbnail_url?: string;
  tags?: string[];
  categories?: string[];
  status: 'draft' | 'published' | 'archived' | 'moderation';
  published_at?: string;
  created_at: string;
  updated_at: string;
  created_by: number;
  moderated_by?: number;
  moderation_notes?: string;
  view_count: number;
  like_count: number;
  bookmark_count: number;
  rating: number;
  rating_count: number;
}

export interface EducationalContentCreate {
  title: string;
  description?: string;
  content_type: 'article' | 'video' | 'podcast' | 'infographic' | 'course' | 'webinar';
  content_source: 'internal' | 'rss_feed' | 'youtube' | 'vimeo' | 'spotify' | 'custom_api';
  source_url?: string;
  content_data?: any;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration_minutes?: number;
  author?: string;
  instructor?: string;
  thumbnail_url?: string;
  tags?: string[];
  categories?: string[];
}

export interface EducationalContentUpdate {
  title?: string;
  description?: string;
  content_type?: 'article' | 'video' | 'podcast' | 'infographic' | 'course' | 'webinar';
  content_source?: 'internal' | 'rss_feed' | 'youtube' | 'vimeo' | 'spotify' | 'custom_api';
  source_url?: string;
  content_data?: any;
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
  duration_minutes?: number;
  author?: string;
  instructor?: string;
  thumbnail_url?: string;
  tags?: string[];
  categories?: string[];
  status?: 'draft' | 'published' | 'archived' | 'moderation';
}

export interface EducationalContentFilters {
  search?: string;
  content_type?: string;
  difficulty?: string;
  status?: string;
  author?: string;
  limit?: number;
  offset?: number;
}

class EducationalContentService {
  private baseUrl = '/api/educational-content';

  // Obtener lista de contenido educativo
  async getContent(filters: EducationalContentFilters = {}): Promise<EducationalContent[]> {
    const params = new URLSearchParams();
    
    if (filters.search) params.append('search', filters.search);
    if (filters.content_type) params.append('content_type', filters.content_type);
    if (filters.difficulty) params.append('difficulty', filters.difficulty);
    if (filters.status) params.append('status', filters.status);
    if (filters.author) params.append('author', filters.author);
    if (filters.limit) params.append('limit', filters.limit.toString());
    if (filters.offset) params.append('offset', filters.offset.toString());

    const response = await apiClient.get(`${this.baseUrl}/?${params.toString()}`);
    return response.data;
  }

  // Obtener contenido específico por ID
  async getContentById(id: number): Promise<EducationalContent> {
    const response = await apiClient.get(`${this.baseUrl}/${id}`);
    return response.data;
  }

  // Crear nuevo contenido
  async createContent(contentData: EducationalContentCreate): Promise<EducationalContent> {
    const response = await apiClient.post(this.baseUrl, contentData);
    return response.data;
  }

  // Actualizar contenido existente
  async updateContent(id: number, contentData: EducationalContentUpdate): Promise<EducationalContent> {
    const response = await apiClient.put(`${this.baseUrl}/${id}`, contentData);
    return response.data;
  }

  // Eliminar contenido
  async deleteContent(id: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}`);
  }

  // Publicar contenido
  async publishContent(id: number): Promise<EducationalContent> {
    const response = await apiClient.post(`${this.baseUrl}/${id}/publish`);
    return response.data;
  }

  // Archivar contenido
  async archiveContent(id: number): Promise<EducationalContent> {
    const response = await apiClient.post(`${this.baseUrl}/${id}/archive`);
    return response.data;
  }

  // Subir archivo de contenido (para contenido interno)
  async uploadContentFile(file: File, contentType: string): Promise<{ url: string; filename: string }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('content_type', contentType);

    const response = await apiClient.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  }

  // Subir imagen miniatura con redimensionamiento automático
  async uploadThumbnail(file: File): Promise<{ url: string; filename: string; size: number }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/api/educational-content/upload-thumbnail', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data.data; // La respuesta viene dentro de data.data
  }

  // Obtener estadísticas de contenido (para administradores)
  async getContentStats(): Promise<{
    total_content: number;
    published_content: number;
    draft_content: number;
    total_views: number;
    total_likes: number;
    average_rating: number;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/stats`);
    return response.data;
  }

  // Obtener contenido por categoría
  async getContentByCategory(category: string): Promise<EducationalContent[]> {
    const response = await apiClient.get(`${this.baseUrl}/category/${category}`);
    return response.data;
  }

  // Buscar contenido
  async searchContent(query: string, filters: Partial<EducationalContentFilters> = {}): Promise<EducationalContent[]> {
    return this.getContent({
      search: query,
      ...filters,
    });
  }
}

export const educationalContentService = new EducationalContentService();

