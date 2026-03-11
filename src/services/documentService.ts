import { apiRequest } from './api';

// Tipos para gestión de documentos
export interface Document {
  id: number;
  user_id: number;
  project_id?: number;
  document_type: string;
  title: string;
  content: any;
  format: string;
  version: string;
  status: string;
  is_draft: boolean;
  is_approved: boolean;
  approved_by?: number;
  approved_at?: string;
  metadata?: any;
  tags?: string[];
  created_at: string;
  updated_at?: string;
  published_at?: string;
}

export interface DocumentTemplate {
  id: number;
  name: string;
  description?: string;
  document_type: string;
  category?: string;
  industry?: string;
  difficulty_level: string;
  content_structure: any;
  variables?: string[];
  is_active: boolean;
  is_featured: boolean;
  usage_count: number;
  rating?: number;
  created_at: string;
  updated_at?: string;
}

export interface DocumentVersion {
  id: number;
  document_id: number;
  version: string;
  content: any;
  changes_summary?: string;
  created_by: number;
  created_at: string;
}

export interface DocumentComment {
  id: number;
  document_id: number;
  user_id: number;
  content: string;
  line_number?: number;
  section?: string;
  is_resolved: boolean;
  parent_comment_id?: number;
  created_at: string;
  updated_at?: string;
}

export interface DocumentCollaborator {
  id: number;
  document_id: number;
  user_id: number;
  role: string;
  permissions: string[];
  invited_at: string;
  joined_at?: string;
  is_active: boolean;
}

export interface DocumentAnalytics {
  id: number;
  document_id: number;
  view_count: number;
  download_count: number;
  share_count: number;
  time_spent: number;
  last_viewed_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface DocumentExport {
  id: number;
  document_id: number;
  export_format: string;
  export_url: string;
  file_size: number;
  expires_at: string;
  created_at: string;
}

// Servicio de gestión de documentos
export class DocumentService {
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  // Obtener documentos del usuario
  async getDocuments(projectId?: number, documentType?: string, limit: number = 20, offset: number = 0): Promise<{
    documents: Document[];
    total_count: number;
    has_more: boolean;
  }> {
    const queryParams = new URLSearchParams();
    if (projectId) queryParams.append('project_id', projectId.toString());
    if (documentType) queryParams.append('document_type', documentType);
    queryParams.append('limit', limit.toString());
    queryParams.append('offset', offset.toString());

    const response = await apiRequest<{
      documents: Document[];
      total_count: number;
      has_more: boolean;
    }>(
      `/api/documents?${queryParams.toString()}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener documentos');
    }

    return response.data!;
  }

  // Obtener documento por ID
  async getDocumentById(documentId: number): Promise<Document> {
    const response = await apiRequest<Document>(
      `/api/documents/${documentId}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener documento');
    }

    return response.data!;
  }

  // Crear nuevo documento
  async createDocument(documentData: Omit<Document, 'id' | 'user_id' | 'created_at' | 'updated_at' | 'published_at'>): Promise<Document> {
    const response = await apiRequest<Document>(
      '/api/documents',
      {
        method: 'POST',
        body: JSON.stringify(documentData)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al crear documento');
    }

    return response.data!;
  }

  // Crear documento desde template
  async createDocumentFromTemplate(templateId: number, documentData: {
    title: string;
    project_id?: number;
    content?: any;
    metadata?: any;
  }): Promise<Document> {
    const response = await apiRequest<Document>(
      `/api/documents/template/${templateId}`,
      {
        method: 'POST',
        body: JSON.stringify(documentData)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al crear documento desde template');
    }

    return response.data!;
  }

  // Actualizar documento
  async updateDocument(documentId: number, documentData: Partial<Document>): Promise<Document> {
    const response = await apiRequest<Document>(
      `/api/documents/${documentId}`,
      {
        method: 'PUT',
        body: JSON.stringify(documentData)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al actualizar documento');
    }

    return response.data!;
  }

  // Eliminar documento
  async deleteDocument(documentId: number): Promise<{ success: boolean; message: string }> {
    const response = await apiRequest<{ success: boolean; message: string }>(
      `/api/documents/${documentId}`,
      {
        method: 'DELETE'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al eliminar documento');
    }

    return response.data!;
  }

  // Publicar documento
  async publishDocument(documentId: number): Promise<Document> {
    const response = await apiRequest<Document>(
      `/api/documents/${documentId}/publish`,
      {
        method: 'POST',
        body: JSON.stringify({
          published_at: new Date().toISOString()
        })
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al publicar documento');
    }

    return response.data!;
  }

  // Aprobar documento
  async approveDocument(documentId: number): Promise<Document> {
    const response = await apiRequest<Document>(
      `/api/documents/${documentId}/approve`,
      {
        method: 'POST',
        body: JSON.stringify({
          approved_at: new Date().toISOString()
        })
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al aprobar documento');
    }

    return response.data!;
  }

  // Obtener versiones del documento
  async getDocumentVersions(documentId: number): Promise<DocumentVersion[]> {
    const response = await apiRequest<DocumentVersion[]>(
      `/api/documents/${documentId}/versions`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener versiones');
    }

    return response.data!;
  }

  // Crear nueva versión
  async createDocumentVersion(documentId: number, versionData: Omit<DocumentVersion, 'id' | 'document_id' | 'created_at'>): Promise<DocumentVersion> {
    const response = await apiRequest<DocumentVersion>(
      `/api/documents/${documentId}/versions`,
      {
        method: 'POST',
        body: JSON.stringify(versionData)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al crear versión');
    }

    return response.data!;
  }

  // Obtener comentarios del documento
  async getDocumentComments(documentId: number): Promise<DocumentComment[]> {
    const response = await apiRequest<DocumentComment[]>(
      `/api/documents/${documentId}/comments`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener comentarios');
    }

    return response.data!;
  }

  // Crear comentario
  async createDocumentComment(documentId: number, commentData: Omit<DocumentComment, 'id' | 'user_id' | 'created_at' | 'updated_at'>): Promise<DocumentComment> {
    const response = await apiRequest<DocumentComment>(
      `/api/documents/${documentId}/comments`,
      {
        method: 'POST',
        body: JSON.stringify(commentData)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al crear comentario');
    }

    return response.data!;
  }

  // Obtener colaboradores del documento
  async getDocumentCollaborators(documentId: number): Promise<DocumentCollaborator[]> {
    const response = await apiRequest<DocumentCollaborator[]>(
      `/api/documents/${documentId}/collaborators`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener colaboradores');
    }

    return response.data!;
  }

  // Invitar colaborador
  async inviteDocumentCollaborator(documentId: number, email: string, role: string, permissions: string[]): Promise<DocumentCollaborator> {
    const response = await apiRequest<DocumentCollaborator>(
      `/api/documents/${documentId}/collaborators`,
      {
        method: 'POST',
        body: JSON.stringify({
          email,
          role,
          permissions
        })
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al invitar colaborador');
    }

    return response.data!;
  }

  // Obtener analytics del documento
  async getDocumentAnalytics(documentId: number): Promise<DocumentAnalytics> {
    const response = await apiRequest<DocumentAnalytics>(
      `/api/documents/${documentId}/analytics`,
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

  // Exportar documento
  async exportDocument(documentId: number, format: string): Promise<DocumentExport> {
    const response = await apiRequest<DocumentExport>(
      `/api/documents/${documentId}/export`,
      {
        method: 'POST',
        body: JSON.stringify({
          format
        })
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al exportar documento');
    }

    return response.data!;
  }

  // Obtener templates de documento
  async getDocumentTemplates(documentType?: string, category?: string): Promise<DocumentTemplate[]> {
    const queryParams = new URLSearchParams();
    if (documentType) queryParams.append('document_type', documentType);
    if (category) queryParams.append('category', category);

    const url = queryParams.toString() 
      ? `/api/documents/templates?${queryParams.toString()}`
      : '/api/documents/templates';
    
    const response = await apiRequest<DocumentTemplate[]>(
      url,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener templates');
    }

    return response.data!;
  }

  // Obtener template por ID
  async getDocumentTemplateById(templateId: number): Promise<DocumentTemplate> {
    const response = await apiRequest<DocumentTemplate>(
      `/api/documents/templates/${templateId}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener template');
    }

    return response.data!;
  }

  // Buscar documentos
  async searchDocuments(query: string, filters?: {
    document_type?: string;
    project_id?: number;
    status?: string;
    tags?: string[];
  }, limit: number = 20, offset: number = 0): Promise<{
    documents: Document[];
    total_count: number;
    has_more: boolean;
  }> {
    const queryParams = new URLSearchParams();
    queryParams.append('query', query);
    if (filters?.document_type) queryParams.append('document_type', filters.document_type);
    if (filters?.project_id) queryParams.append('project_id', filters.project_id.toString());
    if (filters?.status) queryParams.append('status', filters.status);
    if (filters?.tags) filters.tags.forEach(tag => queryParams.append('tags', tag));
    queryParams.append('limit', limit.toString());
    queryParams.append('offset', offset.toString());

    const response = await apiRequest<{
      documents: Document[];
      total_count: number;
      has_more: boolean;
    }>(
      `/api/documents/search?${queryParams.toString()}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al buscar documentos');
    }

    return response.data!;
  }

  // Métodos de conveniencia para el chatbot
  async getBusinessPlanDocuments(projectId?: number): Promise<Document[]> {
    const result = await this.getDocuments(projectId, 'business_plan');
    return result.documents;
  }

  async getFinancialDocuments(projectId?: number): Promise<Document[]> {
    const result = await this.getDocuments(projectId, 'financial_projection');
    return result.documents;
  }

  async getMarketingDocuments(projectId?: number): Promise<Document[]> {
    const result = await this.getDocuments(projectId, 'marketing_plan');
    return result.documents;
  }

  async getLegalDocuments(projectId?: number): Promise<Document[]> {
    const result = await this.getDocuments(projectId, 'legal_document');
    return result.documents;
  }

  async getDraftDocuments(projectId?: number): Promise<Document[]> {
    const result = await this.getDocuments(projectId);
    return result.documents.filter(doc => doc.is_draft);
  }

  async getPublishedDocuments(projectId?: number): Promise<Document[]> {
    const result = await this.getDocuments(projectId);
    return result.documents.filter(doc => !doc.is_draft && doc.status === 'published');
  }

  async getApprovedDocuments(projectId?: number): Promise<Document[]> {
    const result = await this.getDocuments(projectId);
    return result.documents.filter(doc => doc.is_approved);
  }

  // Generar documento de plan de negocio
  async generateBusinessPlan(projectId: number, templateId?: number): Promise<Document> {
    const documentData = {
      title: 'Plan de Negocio',
      project_id: projectId,
      document_type: 'business_plan',
      content: {},
      format: 'json',
      version: '1.0',
      status: 'draft',
      is_draft: true,
      is_approved: false
    };

    if (templateId) {
      return this.createDocumentFromTemplate(templateId, documentData);
    } else {
      return this.createDocument(documentData);
    }
  }

  // Generar documento de proyección financiera
  async generateFinancialProjection(projectId: number, templateId?: number): Promise<Document> {
    const documentData = {
      title: 'Proyección Financiera',
      project_id: projectId,
      document_type: 'financial_projection',
      content: {},
      format: 'json',
      version: '1.0',
      status: 'draft',
      is_draft: true,
      is_approved: false
    };

    if (templateId) {
      return this.createDocumentFromTemplate(templateId, documentData);
    } else {
      return this.createDocument(documentData);
    }
  }

  // Generar documento de plan de marketing
  async generateMarketingPlan(projectId: number, templateId?: number): Promise<Document> {
    const documentData = {
      title: 'Plan de Marketing',
      project_id: projectId,
      document_type: 'marketing_plan',
      content: {},
      format: 'json',
      version: '1.0',
      status: 'draft',
      is_draft: true,
      is_approved: false
    };

    if (templateId) {
      return this.createDocumentFromTemplate(templateId, documentData);
    } else {
      return this.createDocument(documentData);
    }
  }
}

