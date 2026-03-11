// Importación removida ya que no se usa


// Configuración de la API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '10000'); // 10 segundos por defecto

// Tipos de respuesta de la API
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
  status: 'success' | 'error';
}

// Configuración de headers por defecto
const getDefaultHeaders = (isFormData: boolean = false): HeadersInit => {
  const baseHeaders: HeadersInit = {
    'Accept': 'application/json',
  };
  
  // Solo agregar Content-Type si no es FormData
  if (!isFormData) {
    baseHeaders['Content-Type'] = 'application/json';
  }
  
  return baseHeaders;
};

// Función para obtener headers con autenticación
const getAuthHeaders = (token: string, isFormData: boolean = false): HeadersInit => {
  const baseHeaders: HeadersInit = {
    'Accept': 'application/json',
  };
  
  // Solo agregar Content-Type si no es FormData
  if (!isFormData) {
    baseHeaders['Content-Type'] = 'application/json';
  }
  
  return {
    ...baseHeaders,
    'Authorization': `Bearer ${token}`,
  };
};

// Función para manejar respuestas de la API
const handleResponse = async <T>(response: Response): Promise<ApiResponse<T>> => {
  try {
    // Verificar si la respuesta tiene contenido
    const contentType = response.headers.get('content-type');
    const hasJsonContent = contentType && contentType.includes('application/json');
    
    let data = null;
    if (hasJsonContent) {
      try {
        data = await response.json();
      } catch (jsonError) {
        // Para respuestas 204 No Content, es normal que no haya JSON
        data = null;
      }
    }
    
    if (response.ok) {
      return {
        data,
        status: 'success',
        message: data?.message || 'Operación exitosa'
      };
    } else {
      // Detectar token expirado (401 Unauthorized)
      if (response.status === 401) {
        // Limpiar datos de autenticación
        const TOKEN_KEY = import.meta.env.VITE_JWT_STORAGE_KEY || 'innexia_token';
        const REFRESH_TOKEN_KEY = import.meta.env.VITE_REFRESH_TOKEN_KEY || 'innexia_refresh_token';
        const USER_KEY = import.meta.env.VITE_USER_STORAGE_KEY || 'innexia_user';
        const COMPANY_KEY = 'innexia_company';
        
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        localStorage.removeItem(COMPANY_KEY);
        
        // Redirigir al login con mensaje
        const loginUrl = '/login';
        const message = 'Su sesión ha expirado por inactividad. Por favor, inicie sesión nuevamente.';
        
        // Usar replace para evitar que el usuario pueda volver atrás
        window.location.replace(`${loginUrl}?message=${encodeURIComponent(message)}&type=session_expired`);
        
        return {
          status: 'error',
          error: 'Token expirado',
          message: 'Su sesión ha expirado. Redirigiendo al login...'
        };
      }
      
      return {
        status: 'error',
        error: data?.detail || data?.message || `Error ${response.status}`,
        message: data?.detail || data?.message || `Error ${response.status}`
      };
    }
  } catch (error) {
    return {
      status: 'error',
      error: 'Error al procesar la respuesta',
      message: 'Error al procesar la respuesta'
    };
  }
};

// Función para hacer peticiones HTTP
export const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {},
  token?: string
): Promise<ApiResponse<T>> => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Detectar si es FormData
  const isFormData = options.body instanceof FormData;
  const headers = token ? getAuthHeaders(token, isFormData) : getDefaultHeaders(isFormData);
  
  const config: RequestInit = {
    ...options,
    headers: {
      ...headers,
      ...options.headers,
    },
  };

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);
    
    const response = await fetch(url, {
      ...config,
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    return await handleResponse<T>(response);
    
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      return {
        status: 'error',
        error: 'Timeout de la petición',
        message: 'La petición tardó demasiado en responder'
      };
    }
    
    return {
      status: 'error',
      error: 'Error de conexión',
      message: 'No se pudo conectar con el servidor'
    };
  }
};

// Servicios de autenticación
export const authService = {
  // Login
  login: async (username: string, password: string, companyId?: number): Promise<ApiResponse> => {
    const loginData = {
      username,
      password,
      company_id: companyId || 1
    };
    
    return apiRequest('/api/auth/login-company', {
      method: 'POST',
      body: JSON.stringify(loginData),
    });
  },

  // Registro
  register: async (userData: {
    username: string;
    email: string;
    full_name: string;
    password: string;
    confirm_password: string;
    role?: string;
    company_id: number;
  }): Promise<ApiResponse> => {
    return apiRequest('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  // Verificar token
  verifyToken: async (token: string): Promise<ApiResponse> => {
    return apiRequest('/api/auth/me', {
      method: 'GET',
    }, token);
  },

  // Refresh token
  refreshToken: async (refreshToken: string): Promise<ApiResponse> => {
    return apiRequest('/api/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  },

  // Logout
  logout: async (token: string): Promise<ApiResponse> => {
    return apiRequest('/api/auth/logout', {
      method: 'POST',
    }, token);
  },
};

// Servicios de usuarios
export const userService = {
  // Obtener todos los usuarios
  getUsers: async (token: string): Promise<ApiResponse> => {
    return apiRequest('/api/users/', {
      method: 'GET',
    }, token);
  },

  // Obtener usuario por ID
  getUser: async (id: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/users/${id}`, {
      method: 'GET',
    }, token);
  },

  // Crear usuario
  createUser: async (userData: any, token: string): Promise<ApiResponse> => {
    return apiRequest('/api/users/', {
      method: 'POST',
      body: JSON.stringify(userData),
    }, token);
  },

  // Actualizar usuario
  updateUser: async (id: string, userData: any, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/users/${id}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    }, token);
  },

  // Eliminar usuario
  deleteUser: async (id: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/users/${id}`, {
      method: 'DELETE',
    }, token);
  },
};

// Servicios de proyectos
export const projectService = {
  // Obtener todos los proyectos
  getProjects: async (token: string): Promise<ApiResponse> => {
    return apiRequest('/api/projects/', {
      method: 'GET',
    }, token);
  },

  // Obtener proyecto por ID
  getProject: async (id: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/projects/${id}`, {
      method: 'GET',
    }, token);
  },

  // Crear proyecto
  createProject: async (projectData: any, token: string): Promise<ApiResponse> => {
    return apiRequest('/api/projects/', {
      method: 'POST',
      body: JSON.stringify(projectData),
    }, token);
  },

  // Actualizar proyecto
  updateProject: async (id: number, projectData: any, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(projectData),
    }, token);
  },

  // Eliminar proyecto
  deleteProject: async (id: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/projects/${id}`, {
      method: 'DELETE',
    }, token);
  },
};

// Servicios de actividades
export const activityService = {
  // Obtener todas las actividades
  getActivities: async (token: string): Promise<ApiResponse> => {
    return apiRequest('/api/activities/', {
      method: 'GET',
    }, token);
  },

  // Obtener actividades por proyecto
  getProjectActivities: async (projectId: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activities/project/${projectId}`, {
      method: 'GET',
    }, token);
  },

  // Crear actividad
  createActivity: async (activityData: any, token: string): Promise<ApiResponse> => {
    return apiRequest('/api/activities/', {
      method: 'POST',
      body: JSON.stringify(activityData),
    }, token);
  },

  // Actualizar actividad
  updateActivity: async (id: string, activityData: any, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activities/${id}`, {
      method: 'PUT',
      body: JSON.stringify(activityData),
    }, token);
  },

  // Eliminar actividad
  deleteActivity: async (id: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activities/${id}`, {
      method: 'DELETE',
    }, token);
  },

  // ============================================================================
  // NUEVAS FUNCIONALIDADES DE TRELLO
  // ============================================================================

  // Obtener asignados de una actividad
  getActivityAssignees: async (activityId: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activity-trello/${activityId}/assignees`, {
      method: 'GET',
    }, token);
  },

  // Agregar asignado a una actividad
  addAssigneeToActivity: async (activityId: string, userId: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activity-trello/${activityId}/assignees`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    }, token);
  },

  // Remover asignado de una actividad
  removeAssigneeFromActivity: async (activityId: string, userId: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activity-trello/${activityId}/assignees/${userId}`, {
      method: 'DELETE',
    }, token);
  },

  // Obtener etiquetas de una actividad
  getActivityTags: async (activityId: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activity-trello/${activityId}/tags`, {
      method: 'GET',
    }, token);
  },

  // Agregar etiqueta a una actividad
  addTagToActivity: async (activityId: string, tagId: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activity-trello/${activityId}/tags`, {
      method: 'POST',
      body: JSON.stringify({ tag_id: tagId }),
    }, token);
  },

  // Remover etiqueta de una actividad
  removeTagFromActivity: async (activityId: string, tagId: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activity-trello/${activityId}/tags/${tagId}`, {
      method: 'DELETE',
    }, token);
  },

  // Obtener etiquetas de color de una actividad
  getActivityLabels: async (activityId: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activity-trello/${activityId}/labels`, {
      method: 'GET',
    }, token);
  },

  // Agregar etiqueta de color a una actividad
  addLabelToActivity: async (activityId: string, categoryId: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activity-trello/${activityId}/labels`, {
      method: 'POST',
      body: JSON.stringify({ category_id: categoryId }),
    }, token);
  },

  // Remover etiqueta de color de una actividad
  removeLabelFromActivity: async (activityId: string, categoryId: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activity-trello/${activityId}/labels/${categoryId}`, {
      method: 'DELETE',
    }, token);
  },

  // Obtener comentarios de una actividad
  getActivityComments: async (activityId: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activity-trello/${activityId}/comments`, {
      method: 'GET',
    }, token);
  },

  // Agregar comentario a una actividad
  addCommentToActivity: async (activityId: string, content: string, token: string): Promise<ApiResponse> => {
    const formData = new FormData();
    formData.append('content', content);
    
    return apiRequest(`/api/activity-trello/${activityId}/comments`, {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
      },
    }, token);
  },

  // Eliminar comentario de una actividad
  deleteActivityComment: async (activityId: string, commentId: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activity-trello/${activityId}/comments/${commentId}`, {
      method: 'DELETE',
    }, token);
  },

  // Obtener checklists de una actividad
  getActivityChecklists: async (activityId: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activity-trello/${activityId}/checklists`, {
      method: 'GET',
    }, token);
  },

  // Crear checklist para una actividad
  createChecklist: async (activityId: string, title: string, token: string): Promise<ApiResponse> => {
    const formData = new FormData();
    formData.append('title', title);
    
    return apiRequest(`/api/activity-trello/${activityId}/checklists`, {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
      },
    }, token);
  },

  // Agregar item a un checklist
  addChecklistItem: async (checklistId: number, content: string, token: string): Promise<ApiResponse> => {
    const formData = new FormData();
    formData.append('content', content);
    
    return apiRequest(`/api/activity-trello/checklists/${checklistId}/items`, {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
      },
    }, token);
  },

  // Cambiar estado de un item del checklist
  toggleChecklistItem: async (itemId: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activity-trello/checklist-items/${itemId}/toggle`, {
      method: 'PUT',
      body: JSON.stringify({}),
    }, token);
  },

  // Eliminar item del checklist
  deleteChecklistItem: async (itemId: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activity-trello/checklist-items/${itemId}`, {
      method: 'DELETE',
    }, token);
  },

  // Obtener adjuntos de una actividad
  getActivityAttachments: async (activityId: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activity-trello/${activityId}/attachments`, {
      method: 'GET',
    }, token);
  },

  // Subir adjunto a una actividad
  uploadActivityAttachment: async (activityId: string, file: File, description: string, token: string): Promise<ApiResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('description', description);
    
    return apiRequest(`/api/activity-trello/${activityId}/attachments`, {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
      },
    }, token);
  },

  // Eliminar adjunto de una actividad
  deleteActivityAttachment: async (attachmentId: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/activity-trello/attachments/${attachmentId}`, {
      method: 'DELETE',
    }, token);
  },
};

// Servicios de Business Model Canvas
export const bmcService = {
  // Obtener BMC por proyecto
  getProjectBMC: async (projectId: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/bmc/project/${projectId}`, {
      method: 'GET',
    }, token);
  },

  // Crear BMC
  createBMC: async (bmcData: any, token: string): Promise<ApiResponse> => {
    return apiRequest('/api/bmc/', {
      method: 'POST',
      body: JSON.stringify(bmcData),
    }, token);
  },

  // Actualizar BMC
  updateBMC: async (id: string, bmcData: any, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/bmc/${id}`, {
      method: 'PUT',
      body: JSON.stringify(bmcData),
    }, token);
  },

  // Eliminar BMC
  deleteBMC: async (id: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/bmc/${id}`, {
      method: 'DELETE',
    }, token);
  },
};

// Servicios de documentos
export const documentService = {
  // Obtener documentos por proyecto
  getProjectDocuments: async (projectId: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/documents/project/${projectId}`, {
      method: 'GET',
    }, token);
  },

  // Subir documento
  uploadDocument: async (file: File, projectId: string, description: string, token: string): Promise<ApiResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);
    formData.append('description', description);
    
    return apiRequest('/api/documents/upload', {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
      },
    }, token);
  },

  // Eliminar documento
  deleteDocument: async (id: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/documents/${id}`, {
      method: 'DELETE',
    }, token);
  },

  // Descargar documento
  downloadDocument: async (id: string, token: string): Promise<Blob> => {
    const response = await fetch(`${API_BASE_URL}/api/documents/${id}/download`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Error al descargar documento: ${response.status}`);
    }

    return response.blob();
  },

  // Obtener documento por ID
  getDocument: async (id: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/documents/${id}`, {
      method: 'GET',
    }, token);
  },
};

// Salida del agente IA (n8n)
export const agentOutputService = {
  getByProject: async (projectId: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/agent-output/project/${projectId}`, {
      method: 'GET',
    }, token);
  },
  save: async (projectId: number, payload: Record<string, unknown>, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/agent-output/project/${projectId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }, token);
  },
  /** Actualiza solo la estrategia comercial (tabla canónica). Tras guardar, volver a getByProject para ver datos. */
  updateEstrategiaComercial: async (projectId: number, data: Record<string, unknown>, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/agent-output/project/${projectId}/estrategia-comercial`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }, token);
  },
  /** Actualiza solo el roadmap (tabla canónica). */
  updateRoadmap: async (projectId: number, data: Record<string, unknown>, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/agent-output/project/${projectId}/roadmap`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }, token);
  },
  /** Actualiza solo el análisis financiero (tabla canónica). */
  updateAnalisisFinanciero: async (projectId: number, data: Record<string, unknown>, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/agent-output/project/${projectId}/analisis-financiero`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }, token);
  },
  /** Actualiza solo el análisis de riesgos (tablas canónicas). */
  updateAnalisisRiesgos: async (projectId: number, data: Record<string, unknown>, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/agent-output/project/${projectId}/analisis-riesgos`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }, token);
  },
  /** Actualiza solo el veredicto (tabla canónica). Un futuro agente puede re-analizar y actualizar. */
  updateVeredicto: async (projectId: number, data: Record<string, unknown>, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/agent-output/project/${projectId}/veredicto`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }, token);
  },
  createProjectFromPayload: async (
    payload: Record<string, unknown>,
    token: string,
    options?: { name?: string; description?: string; category_id?: number; location_id?: number }
  ): Promise<ApiResponse> => {
    return apiRequest('/api/agent-output/create-project', {
      method: 'POST',
      body: JSON.stringify({
        payload,
        name: options?.name,
        description: options?.description,
        category_id: options?.category_id,
        location_id: options?.location_id,
      }),
    }, token);
  },
};

// Servicios de maestros
export const masterService = {
  // Obtener categorías
  getCategories: async (token: string): Promise<ApiResponse> => {
    return apiRequest('/api/masters/categories', {
      method: 'GET',
    }, token);
  },

  // Crear categoría
  createCategory: async (categoryData: any, token: string): Promise<ApiResponse> => {
    return apiRequest('/api/masters/categories', {
      method: 'POST',
      body: JSON.stringify(categoryData),
    }, token);
  },

  // Obtener etiquetas
  getTags: async (token: string): Promise<ApiResponse> => {
    return apiRequest('/api/masters/tags', {
      method: 'GET',
    }, token);
  },

  // Obtener ubicaciones
  getLocations: async (token: string): Promise<ApiResponse> => {
    return apiRequest('/api/masters/locations', {
      method: 'GET',
    }, token);
  },

  // Obtener estados
  getStatuses: async (token: string): Promise<ApiResponse> => {
    return apiRequest('/api/masters/statuses', {
      method: 'GET',
    }, token);
  },

  // Actualizar categoría
  updateCategory: async (id: string, categoryData: any, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/masters/categories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(categoryData),
    }, token);
  },

  // Eliminar categoría
  deleteCategory: async (id: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/masters/categories/${id}`, {
      method: 'DELETE',
    }, token);
  },

  // Crear etiqueta
  createTag: async (tagData: any, token: string): Promise<ApiResponse> => {
    return apiRequest('/api/masters/tags', {
      method: 'POST',
      body: JSON.stringify(tagData),
    }, token);
  },

  // Actualizar etiqueta
  updateTag: async (id: string, tagData: any, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/masters/tags/${id}`, {
      method: 'PUT',
      body: JSON.stringify(tagData),
    }, token);
  },

  // Eliminar etiqueta
  deleteTag: async (id: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/masters/tags/${id}`, {
      method: 'DELETE',
    }, token);
  },

  // Crear ubicación
  createLocation: async (locationData: any, token: string): Promise<ApiResponse> => {
    return apiRequest('/api/masters/locations', {
      method: 'POST',
      body: JSON.stringify(locationData),
    }, token);
  },

  // Actualizar ubicación
  updateLocation: async (id: string, locationData: any, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/masters/locations/${id}`, {
      method: 'PUT',
      body: JSON.stringify(locationData),
    }, token);
  },

  // Eliminar ubicación
  deleteLocation: async (id: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/masters/locations/${id}`, {
      method: 'DELETE',
    }, token);
  },
};

// Servicios de empresa
export const companyService = {
  // Obtener información de mi empresa
  getMyCompany: async (token: string): Promise<ApiResponse> => {
    return apiRequest('/api/company/me', {
      method: 'GET',
    }, token);
  },

  // Obtener empresa por ID
  getCompany: async (id: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/company/${id}`, {
      method: 'GET',
    }, token);
  },

  // Obtener todas las empresas (requiere super admin)
  getAllCompanies: async (token: string): Promise<ApiResponse> => {
    return apiRequest('/api/company/', {
      method: 'GET',
    }, token);
  },

  // Actualizar empresa
  updateCompany: async (companyData: any, token: string): Promise<ApiResponse> => {
    return apiRequest('/api/company/me', {
      method: 'PUT',
      body: JSON.stringify(companyData),
    }, token);
  },

  // Crear empresa (requiere super admin)
  createCompany: async (companyData: any, token: string): Promise<ApiResponse> => {
    return apiRequest('/api/company/', {
      method: 'POST',
      body: JSON.stringify(companyData),
    }, token);
  },
};

// Servicios de bitácoras
export const auditLogService = {
  // Obtener todas las bitácoras
  getLogs: async (token: string, filters?: {
    action?: string;
    entity_type?: string;
    username?: string;
    dateFrom?: string;
    dateTo?: string;
  }): Promise<ApiResponse> => {
    let url = '/api/audit-log/';
    if (filters) {
      const params = new URLSearchParams();
      if (filters.action) params.append('action', filters.action);
      if (filters.entity_type) params.append('entity_type', filters.entity_type);
      if (filters.username) params.append('username', filters.username);
      if (filters.dateFrom) params.append('date_from', filters.dateFrom);
      if (filters.dateTo) params.append('date_to', filters.dateTo);
      if (params.toString()) url += `?${params.toString()}`;
    }
    return apiRequest(url, {
      method: 'GET',
    }, token);
  },

  // Obtener bitácoras por entidad
  getEntityLogs: async (entityType: string, entityId: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/audit-log/entity/${entityType}/${entityId}`, {
      method: 'GET',
    }, token);
  },

  // Obtener bitácoras por usuario
  getUserLogs: async (userId: string, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/audit-log/user/${userId}`, {
      method: 'GET',
    }, token);
  },
};

// Función para verificar si la API está disponible
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
};

// Función para obtener la URL base de la API
export const getApiBaseUrl = (): string => API_BASE_URL;

// Servicio de contenido educativo
export const educationalContentService = {
  // Obtener lista de contenido educativo
  getContent: async (filters: any = {}, token: string): Promise<ApiResponse> => {
    const params = new URLSearchParams();
    
    if (filters.search) params.append('search', filters.search);
    if (filters.content_type) params.append('content_type', filters.content_type);
    if (filters.difficulty) params.append('difficulty', filters.difficulty);
    if (filters.status) params.append('status', filters.status);
    if (filters.author) params.append('author', filters.author);
    if (filters.limit) params.append('limit', filters.limit.toString());
    if (filters.offset) params.append('offset', filters.offset.toString());

    const url = `/api/educational-content/?${params.toString()}`;
    return apiRequest(url, {
      method: 'GET',
    }, token);
  },

  // Obtener contenido específico por ID
  getContentById: async (id: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/educational-content/${id}`, {
      method: 'GET',
    }, token);
  },

  // Crear nuevo contenido
  createContent: async (contentData: any, token: string): Promise<ApiResponse> => {
    return apiRequest('/api/educational-content/', {
      method: 'POST',
      body: JSON.stringify(contentData),
    }, token);
  },

  // Actualizar contenido existente
  updateContent: async (id: number, contentData: any, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/educational-content/${id}`, {
      method: 'PUT',
      body: JSON.stringify(contentData),
    }, token);
  },

  // Eliminar contenido
  deleteContent: async (id: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/educational-content/${id}`, {
      method: 'DELETE',
    }, token);
  },

  // Publicar contenido
  publishContent: async (id: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/educational-content/${id}/publish`, {
      method: 'POST',
    }, token);
  },

  // Archivar contenido
  archiveContent: async (id: number, token: string): Promise<ApiResponse> => {
    return apiRequest(`/api/educational-content/${id}/archive`, {
      method: 'POST',
    }, token);
  },

  // Subir archivo de contenido
  uploadContentFile: async (file: File, contentType: string, token: string): Promise<ApiResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('content_type', contentType);

    return apiRequest('/api/educational-content/upload-file', {
      method: 'POST',
      body: formData,
    }, token);
  },

  // Subir thumbnail (imagen)
  uploadThumbnail: async (file: File, token: string): Promise<ApiResponse> => {
    return educationalContentService.uploadContentFile(file, 'image', token);
  },
};

export default {
  auth: authService,
  users: userService,
  projects: projectService,
  activities: activityService,
  bmc: bmcService,
  documents: documentService,
  masters: masterService,
  company: companyService,
  auditLog: auditLogService,
  educationalContent: educationalContentService,
  checkApiHealth,
  getApiBaseUrl,
};