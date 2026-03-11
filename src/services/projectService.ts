import { apiRequest } from './api';

// Tipos para gestión de proyectos
export interface Project {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  project_type: string;
  industry?: string;
  business_model?: string;
  target_market?: string;
  budget_range?: string;
  timeline?: string;
  status: string;
  priority: string;
  progress_percentage: number;
  is_template: boolean;
  template_id?: number;
  metadata?: any;
  tags?: string[];
  collaborators?: number[];
  created_at: string;
  updated_at?: string;
  completed_at?: string;
}

export interface ProjectActivity {
  id: number;
  project_id: number;
  activity_type: string;
  title: string;
  description?: string;
  status: string;
  priority: string;
  difficulty_level: string;
  estimated_duration: number;
  actual_duration?: number;
  dependencies?: number[];
  assigned_to?: number;
  due_date?: string;
  completed_at?: string;
  notes?: string;
  metadata?: any;
  created_at: string;
  updated_at?: string;
}

export interface ProjectDocument {
  id: number;
  project_id: number;
  document_type: string;
  title: string;
  content: any;
  format: string;
  version: string;
  is_draft: boolean;
  is_approved: boolean;
  approved_by?: number;
  approved_at?: string;
  metadata?: any;
  created_at: string;
  updated_at?: string;
}

export interface ProjectTemplate {
  id: number;
  name: string;
  description?: string;
  project_type: string;
  industry?: string;
  difficulty_level: string;
  estimated_duration: number;
  activities: Omit<ProjectActivity, 'id' | 'project_id' | 'created_at' | 'updated_at'>[];
  documents: Omit<ProjectDocument, 'id' | 'project_id' | 'created_at' | 'updated_at'>[];
  is_active: boolean;
  is_featured: boolean;
  usage_count: number;
  rating?: number;
  created_at: string;
  updated_at?: string;
}

export interface ProjectCollaborator {
  id: number;
  project_id: number;
  user_id: number;
  role: string;
  permissions: string[];
  invited_at: string;
  joined_at?: string;
  is_active: boolean;
}

export interface ProjectComment {
  id: number;
  project_id: number;
  user_id: number;
  activity_id?: number;
  content: string;
  parent_comment_id?: number;
  is_resolved: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ProjectMilestone {
  id: number;
  project_id: number;
  title: string;
  description?: string;
  due_date: string;
  status: string;
  activities: number[];
  created_at: string;
  completed_at?: string;
}

// Servicio de gestión de proyectos
export class ProjectService {
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  // Obtener todos los proyectos del usuario
  async getProjects(status?: string, limit: number = 20, offset: number = 0): Promise<{
    projects: Project[];
    total_count: number;
    has_more: boolean;
  }> {
    const queryParams = new URLSearchParams();
    if (status) queryParams.append('status', status);
    queryParams.append('limit', limit.toString());
    queryParams.append('offset', offset.toString());

    const response = await apiRequest<{
      projects: Project[];
      total_count: number;
      has_more: boolean;
    }>(
      `/api/projects?${queryParams.toString()}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener proyectos');
    }

    return response.data!;
  }

  // Obtener proyecto por ID
  async getProjectById(projectId: number): Promise<Project> {
    const response = await apiRequest<Project>(
      `/api/projects/${projectId}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener proyecto');
    }

    return response.data!;
  }

  // Crear nuevo proyecto
  async createProject(projectData: Omit<Project, 'id' | 'user_id' | 'created_at' | 'updated_at' | 'completed_at'>): Promise<Project> {
    const response = await apiRequest<Project>(
      '/api/projects',
      {
        method: 'POST',
        body: JSON.stringify(projectData)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al crear proyecto');
    }

    return response.data!;
  }

  // Crear proyecto desde template
  async createProjectFromTemplate(templateId: number, projectData: {
    name: string;
    description?: string;
    industry?: string;
    business_model?: string;
    target_market?: string;
    budget_range?: string;
    timeline?: string;
  }): Promise<Project> {
    const response = await apiRequest<Project>(
      `/api/projects/template/${templateId}`,
      {
        method: 'POST',
        body: JSON.stringify(projectData)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al crear proyecto desde template');
    }

    return response.data!;
  }

  // Actualizar proyecto
  async updateProject(projectId: number, projectData: Partial<Project>): Promise<Project> {
    const response = await apiRequest<Project>(
      `/api/projects/${projectId}`,
      {
        method: 'PUT',
        body: JSON.stringify(projectData)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al actualizar proyecto');
    }

    return response.data!;
  }

  // Eliminar proyecto
  async deleteProject(projectId: number): Promise<{ success: boolean; message: string }> {
    const response = await apiRequest<{ success: boolean; message: string }>(
      `/api/projects/${projectId}`,
      {
        method: 'DELETE'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al eliminar proyecto');
    }

    return response.data!;
  }

  // Obtener actividades del proyecto
  async getProjectActivities(projectId: number, status?: string): Promise<ProjectActivity[]> {
    const url = status 
      ? `/api/projects/${projectId}/activities?status=${status}`
      : `/api/projects/${projectId}/activities`;
    
    const response = await apiRequest<ProjectActivity[]>(
      url,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener actividades');
    }

    return response.data!;
  }

  // Obtener actividad por ID
  async getActivityById(activityId: number): Promise<ProjectActivity> {
    const response = await apiRequest<ProjectActivity>(
      `/api/projects/activities/${activityId}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener actividad');
    }

    return response.data!;
  }

  // Crear nueva actividad
  async createActivity(projectId: number, activityData: Omit<ProjectActivity, 'id' | 'project_id' | 'created_at' | 'updated_at'>): Promise<ProjectActivity> {
    const response = await apiRequest<ProjectActivity>(
      `/api/projects/${projectId}/activities`,
      {
        method: 'POST',
        body: JSON.stringify(activityData)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al crear actividad');
    }

    return response.data!;
  }

  // Actualizar actividad
  async updateActivity(activityId: number, activityData: Partial<ProjectActivity>): Promise<ProjectActivity> {
    const response = await apiRequest<ProjectActivity>(
      `/api/projects/activities/${activityId}`,
      {
        method: 'PUT',
        body: JSON.stringify(activityData)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al actualizar actividad');
    }

    return response.data!;
  }

  // Marcar actividad como completada
  async completeActivity(activityId: number, notes?: string): Promise<ProjectActivity> {
    const response = await apiRequest<ProjectActivity>(
      `/api/projects/activities/${activityId}/complete`,
      {
        method: 'POST',
        body: JSON.stringify({
          notes,
          completed_at: new Date().toISOString()
        })
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al completar actividad');
    }

    return response.data!;
  }

  // Obtener documentos del proyecto
  async getProjectDocuments(projectId: number, documentType?: string): Promise<ProjectDocument[]> {
    const url = documentType 
      ? `/api/projects/${projectId}/documents?type=${documentType}`
      : `/api/projects/${projectId}/documents`;
    
    const response = await apiRequest<ProjectDocument[]>(
      url,
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
  async getDocumentById(documentId: number): Promise<ProjectDocument> {
    const response = await apiRequest<ProjectDocument>(
      `/api/projects/documents/${documentId}`,
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
  async createDocument(projectId: number, documentData: Omit<ProjectDocument, 'id' | 'project_id' | 'created_at' | 'updated_at'>): Promise<ProjectDocument> {
    const response = await apiRequest<ProjectDocument>(
      `/api/projects/${projectId}/documents`,
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

  // Actualizar documento
  async updateDocument(documentId: number, documentData: Partial<ProjectDocument>): Promise<ProjectDocument> {
    const response = await apiRequest<ProjectDocument>(
      `/api/projects/documents/${documentId}`,
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

  // Aprobar documento
  async approveDocument(documentId: number): Promise<ProjectDocument> {
    const response = await apiRequest<ProjectDocument>(
      `/api/projects/documents/${documentId}/approve`,
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

  // Obtener templates de proyecto
  async getProjectTemplates(projectType?: string, industry?: string): Promise<ProjectTemplate[]> {
    const queryParams = new URLSearchParams();
    if (projectType) queryParams.append('project_type', projectType);
    if (industry) queryParams.append('industry', industry);

    const url = queryParams.toString() 
      ? `/api/projects/templates?${queryParams.toString()}`
      : '/api/projects/templates';
    
    const response = await apiRequest<ProjectTemplate[]>(
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
  async getTemplateById(templateId: number): Promise<ProjectTemplate> {
    const response = await apiRequest<ProjectTemplate>(
      `/api/projects/templates/${templateId}`,
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

  // Obtener colaboradores del proyecto
  async getProjectCollaborators(projectId: number): Promise<ProjectCollaborator[]> {
    const response = await apiRequest<ProjectCollaborator[]>(
      `/api/projects/${projectId}/collaborators`,
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
  async inviteCollaborator(projectId: number, email: string, role: string, permissions: string[]): Promise<ProjectCollaborator> {
    const response = await apiRequest<ProjectCollaborator>(
      `/api/projects/${projectId}/collaborators`,
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

  // Obtener comentarios del proyecto
  async getProjectComments(projectId: number, activityId?: number): Promise<ProjectComment[]> {
    const url = activityId 
      ? `/api/projects/${projectId}/comments?activity_id=${activityId}`
      : `/api/projects/${projectId}/comments`;
    
    const response = await apiRequest<ProjectComment[]>(
      url,
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
  async createComment(projectId: number, commentData: Omit<ProjectComment, 'id' | 'user_id' | 'created_at' | 'updated_at'>): Promise<ProjectComment> {
    const response = await apiRequest<ProjectComment>(
      `/api/projects/${projectId}/comments`,
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

  // Obtener hitos del proyecto
  async getProjectMilestones(projectId: number): Promise<ProjectMilestone[]> {
    const response = await apiRequest<ProjectMilestone[]>(
      `/api/projects/${projectId}/milestones`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener hitos');
    }

    return response.data!;
  }

  // Crear hito
  async createMilestone(projectId: number, milestoneData: Omit<ProjectMilestone, 'id' | 'project_id' | 'created_at' | 'completed_at'>): Promise<ProjectMilestone> {
    const response = await apiRequest<ProjectMilestone>(
      `/api/projects/${projectId}/milestones`,
      {
        method: 'POST',
        body: JSON.stringify(milestoneData)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al crear hito');
    }

    return response.data!;
  }

  // Métodos de conveniencia para el chatbot
  async getActiveProjects(): Promise<Project[]> {
    const result = await this.getProjects('active');
    return result.projects;
  }

  async getCompletedProjects(): Promise<Project[]> {
    const result = await this.getProjects('completed');
    return result.projects;
  }

  async getProjectProgress(projectId: number): Promise<number> {
    const project = await this.getProjectById(projectId);
    return project.progress_percentage;
  }

  async getProjectActivitiesByStatus(projectId: number, status: string): Promise<ProjectActivity[]> {
    return this.getProjectActivities(projectId, status);
  }

  async getPendingActivities(projectId: number): Promise<ProjectActivity[]> {
    return this.getProjectActivities(projectId, 'pending');
  }

  async getInProgressActivities(projectId: number): Promise<ProjectActivity[]> {
    return this.getProjectActivities(projectId, 'in_progress');
  }

  async getCompletedActivities(projectId: number): Promise<ProjectActivity[]> {
    return this.getProjectActivities(projectId, 'completed');
  }

  async getBusinessPlanDocument(projectId: number): Promise<ProjectDocument | null> {
    const documents = await this.getProjectDocuments(projectId, 'business_plan');
    return documents.length > 0 ? documents[0] : null;
  }

  async getFinancialProjectionDocument(projectId: number): Promise<ProjectDocument | null> {
    const documents = await this.getProjectDocuments(projectId, 'financial_projection');
    return documents.length > 0 ? documents[0] : null;
  }

  async getMarketingPlanDocument(projectId: number): Promise<ProjectDocument | null> {
    const documents = await this.getProjectDocuments(projectId, 'marketing_plan');
    return documents.length > 0 ? documents[0] : null;
  }
}

