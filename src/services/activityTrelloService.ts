import { apiRequest } from './api';

// ============================================================================
// TIPOS PARA LAS APIS DE TRELLO
// ============================================================================

export interface ActivityAssignee {
  id: number;
  full_name: string;
  username: string;
  role: string;
  assigned_at: string;
}

export interface ActivityTag {
  id: number;
  name: string;
  color: string;
  created_at: string;
}

export interface ActivityLabel {
  id: number;
  name: string;
  color: string;
  created_at: string;
}

export interface ActivityComment {
  id: number;
  content: string;
  author_id: number;
  author_name: string;
  created_at: string;
  updated_at: string;
}

export interface ActivityChecklistItem {
  id: number;
  content: string;
  completed: boolean;
  completed_at?: string;
  completed_by?: string;
  created_at: string;
}

export interface ActivityChecklist {
  id: number;
  title: string;
  activity_id: number;
  created_at: string;
  updated_at: string;
  items: ActivityChecklistItem[];
}

export interface ActivityAttachment {
  id: number;
  name: string;
  original_name: string;
  file_type: string;
  file_size: number;
  description?: string;
  uploader_id: number;
  uploader_name: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// SERVICIO PRINCIPAL
// ============================================================================

export const activityTrelloService = {
  // ============================================================================
  // ASIGNADOS MÚLTIPLES
  // ============================================================================

  async getActivityAssignees(activityId: number, token: string): Promise<ActivityAssignee[]> {
    const response = await apiRequest(`/api/activity-trello/${activityId}/assignees`, {
      method: 'GET',
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener asignados');
    }
    
    return (response.data as ActivityAssignee[]) || [];
  },

  async addAssigneeToActivity(activityId: number, userId: number, token: string): Promise<{ message: string }> {
    const response = await apiRequest(`/api/activity-trello/${activityId}/assignees`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al agregar asignado');
    }
    
    return (response.data as { message: string }) || { message: 'Asignado agregado exitosamente' };
  },

  async removeAssigneeFromActivity(activityId: number, userId: number, token: string): Promise<{ message: string }> {
    const response = await apiRequest(`/api/activity-trello/${activityId}/assignees/${userId}`, {
      method: 'DELETE',
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al remover asignado');
    }
    
    return (response.data as { message: string }) || { message: 'Asignado removido exitosamente' };
  },

  // ============================================================================
  // ETIQUETAS (TAGS)
  // ============================================================================

  async getActivityTags(activityId: number, token: string): Promise<ActivityTag[]> {
    const response = await apiRequest(`/api/activity-trello/${activityId}/tags`, {
      method: 'GET',
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener etiquetas');
    }
    
    return (response.data as ActivityTag[]) || [];
  },

  async addTagToActivity(activityId: number, tagId: number, token: string): Promise<{ message: string }> {
    const response = await apiRequest(`/api/activity-trello/${activityId}/tags`, {
      method: 'POST',
      body: JSON.stringify({ tag_id: tagId }),
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al agregar etiqueta');
    }
    
    return (response.data as { message: string }) || { message: 'Etiqueta agregada exitosamente' };
  },

  async removeTagFromActivity(activityId: number, tagId: number, token: string): Promise<{ message: string }> {
    const response = await apiRequest(`/api/activity-trello/${activityId}/tags/${tagId}`, {
      method: 'DELETE',
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al remover etiqueta');
    }
    
    return (response.data as { message: string }) || { message: 'Etiqueta removida exitosamente' };
  },

  // ============================================================================
  // ETIQUETAS DE COLOR (LABELS)
  // ============================================================================

  async getActivityLabels(activityId: number, token: string): Promise<ActivityLabel[]> {
    const response = await apiRequest(`/api/activity-trello/${activityId}/labels`, {
      method: 'GET',
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener etiquetas de color');
    }
    
    return (response.data as ActivityLabel[]) || [];
  },

  async addLabelToActivity(activityId: number, categoryId: number, token: string): Promise<{ message: string }> {
    const response = await apiRequest(`/api/activity-trello/${activityId}/labels`, {
      method: 'POST',
      body: JSON.stringify({ category_id: categoryId }),
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al agregar etiqueta de color');
    }
    
    return (response.data as { message: string }) || { message: 'Etiqueta de color agregada exitosamente' };
  },

  async removeLabelFromActivity(activityId: number, categoryId: number, token: string): Promise<{ message: string }> {
    const response = await apiRequest(`/api/activity-trello/${activityId}/labels/${categoryId}`, {
      method: 'DELETE',
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al remover etiqueta de color');
    }
    
    return (response.data as { message: string }) || { message: 'Etiqueta de color removida exitosamente' };
  },

  // ============================================================================
  // COMENTARIOS
  // ============================================================================

  async getActivityComments(activityId: number, token: string): Promise<ActivityComment[]> {
    const response = await apiRequest(`/api/activity-trello/${activityId}/comments`, {
      method: 'GET',
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener comentarios');
    }
    
    return (response.data as ActivityComment[]) || [];
  },

  async addCommentToActivity(activityId: number, content: string, token: string): Promise<ActivityComment> {
    try {
      const formData = new FormData();
      formData.append('content', content);

      const response = await apiRequest(`/api/activity-trello/${activityId}/comments`, {
        method: 'POST',
        body: formData
      }, token);
      
      if (response.status === 'error') {
        throw new Error(response.error || 'Error al agregar comentario');
      }
      
      if (!response.data) {
        throw new Error('No se recibió respuesta del servidor');
      }
      
      return response.data as ActivityComment;
    } catch (error: any) {
      console.error('Error in addCommentToActivity:', error);
      throw new Error(error.message || 'Error al agregar el comentario');
    }
  },

  async deleteActivityComment(activityId: number, commentId: number, token: string): Promise<{ message: string }> {
    const response = await apiRequest(`/api/activity-trello/${activityId}/comments/${commentId}`, {
      method: 'DELETE',
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al eliminar comentario');
    }
    
    return (response.data as { message: string }) || { message: 'Comentario eliminado exitosamente' };
  },

  // ============================================================================
  // CHECKLISTS
  // ============================================================================

  async getActivityChecklists(activityId: number, token: string): Promise<ActivityChecklist[]> {
    const response = await apiRequest(`/api/activity-trello/${activityId}/checklists`, {
      method: 'GET',
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener checklists');
    }
    
    return (response.data as ActivityChecklist[]) || [];
  },

  async createChecklist(activityId: number, title: string, token: string): Promise<ActivityChecklist> {
    try {
      const formData = new FormData();
      formData.append('title', title);

      const response = await apiRequest(`/api/activity-trello/${activityId}/checklists`, {
        method: 'POST',
        body: formData
      }, token);
      
      if (response.status === 'error') {
        throw new Error(response.error || 'Error al crear checklist');
      }
      
      if (!response.data) {
        throw new Error('No se recibió respuesta del servidor');
      }
      
      return response.data as ActivityChecklist;
    } catch (error: any) {
      console.error('Error in createChecklist:', error);
      throw new Error(error.message || 'Error al crear el checklist');
    }
  },

  async addChecklistItem(checklistId: number, content: string, token: string): Promise<ActivityChecklistItem> {
    try {
      const formData = new FormData();
      formData.append('content', content);

      const response = await apiRequest(`/api/activity-trello/checklists/${checklistId}/items`, {
        method: 'POST',
        body: formData
      }, token);
      
      if (response.status === 'error') {
        throw new Error(response.error || 'Error al agregar item al checklist');
      }
      
      if (!response.data) {
        throw new Error('No se recibió respuesta del servidor');
      }
      
      return response.data as ActivityChecklistItem;
    } catch (error: any) {
      console.error('Error in addChecklistItem:', error);
      throw new Error(error.message || 'Error al agregar el item');
    }
  },

  async toggleChecklistItem(itemId: number, token: string): Promise<ActivityChecklistItem> {
    const response = await apiRequest(`/api/activity-trello/checklist-items/${itemId}/toggle`, {
      method: 'PUT',
      body: JSON.stringify({}),
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al cambiar estado del item');
    }
    
    return response.data as ActivityChecklistItem;
  },

  async deleteChecklistItem(itemId: number, token: string): Promise<{ message: string }> {
    const response = await apiRequest(`/api/activity-trello/checklist-items/${itemId}`, {
      method: 'DELETE',
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al eliminar item');
    }
    
    return (response.data as { message: string }) || { message: 'Item eliminado exitosamente' };
  },

  // ============================================================================
  // ADJUNTOS
  // ============================================================================

  async getActivityAttachments(activityId: number, token: string): Promise<ActivityAttachment[]> {
    const response = await apiRequest(`/api/activity-trello/${activityId}/attachments`, {
      method: 'GET',
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener adjuntos');
    }
    
    return (response.data as ActivityAttachment[]) || [];
  },

  async uploadAttachment(activityId: number, file: File, description?: string, token?: string): Promise<ActivityAttachment> {
    const formData = new FormData();
    formData.append('file', file);
    if (description) {
      formData.append('description', description);
    }

    const response = await apiRequest(`/api/activity-trello/${activityId}/attachments`, {
      method: 'POST',
      body: formData
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al subir adjunto');
    }
    
    return response.data as ActivityAttachment;
  },

  async deleteAttachment(attachmentId: number, token: string): Promise<{ message: string }> {
    const response = await apiRequest(`/api/activity-trello/attachments/${attachmentId}`, {
      method: 'DELETE',
    }, token);
    
    if (response.status === 'error') {
      throw new Error(response.error || 'Error al eliminar adjunto');
    }
    
    return (response.data as { message: string }) || { message: 'Adjunto eliminado exitosamente' };
  }
};
