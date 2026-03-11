import { useState, useEffect, useCallback } from 'react';
import { activityTrelloService } from '../services/activityTrelloService';
import type { 
  ActivityAssignee, 
  ActivityTag, 
  ActivityLabel, 
  ActivityComment, 
  ActivityChecklist, 
  ActivityAttachment 
} from '../services/activityTrelloService';

interface UseActivityTrelloProps {
  activityId: number;
  token: string;
}

export const useActivityTrello = ({ activityId, token }: UseActivityTrelloProps) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Estados para datos
  const [assignees, setAssignees] = useState<ActivityAssignee[]>([]);
  const [tags, setTags] = useState<ActivityTag[]>([]);
  const [labels, setLabels] = useState<ActivityLabel[]>([]);
  const [comments, setComments] = useState<ActivityComment[]>([]);
  const [checklists, setChecklists] = useState<ActivityChecklist[]>([]);
  const [attachments, setAttachments] = useState<ActivityAttachment[]>([]);

  // Cargar todos los datos de la actividad
  const loadActivityData = useCallback(async () => {
    if (!token || !activityId) return;

    setLoading(true);
    setError(null);

    try {
      const [
        assigneesData,
        tagsData,
        labelsData,
        commentsData,
        checklistsData,
        attachmentsData
      ] = await Promise.all([
        activityTrelloService.getActivityAssignees(activityId, token),
        activityTrelloService.getActivityTags(activityId, token),
        activityTrelloService.getActivityLabels(activityId, token),
        activityTrelloService.getActivityComments(activityId, token),
        activityTrelloService.getActivityChecklists(activityId, token),
        activityTrelloService.getActivityAttachments(activityId, token)
      ]);

      setAssignees(assigneesData);
      setTags(tagsData);
      setLabels(labelsData);
      setComments(commentsData);
      setChecklists(checklistsData);
      setAttachments(attachmentsData);

    } catch (err) {
      console.error('Error loading activity data:', err);
      setError('Error al cargar los datos de la actividad');
    } finally {
      setLoading(false);
    }
  }, [activityId, token]);

  // Funciones para asignados
  const addAssignee = useCallback(async (userId: number) => {
    try {
      setLoading(true);
      await activityTrelloService.addAssigneeToActivity(activityId, userId, token);
      await loadActivityData(); // Recargar datos
      setSuccess('Asignado agregado exitosamente');
    } catch (err) {
      console.error('Error adding assignee:', err);
      setError('Error al agregar el asignado');
    } finally {
      setLoading(false);
    }
  }, [activityId, token, loadActivityData]);

  const removeAssignee = useCallback(async (userId: number) => {
    try {
      setLoading(true);
      await activityTrelloService.removeAssigneeFromActivity(activityId, userId, token);
      await loadActivityData(); // Recargar datos
      setSuccess('Asignado removido exitosamente');
    } catch (err) {
      console.error('Error removing assignee:', err);
      setError('Error al remover el asignado');
    } finally {
      setLoading(false);
    }
  }, [activityId, token, loadActivityData]);

  // Funciones para etiquetas
  const addTag = async (tagId: number) => {
    try {
      setLoading(true);
      await activityTrelloService.addTagToActivity(activityId, tagId, token);
      await loadActivityData(); // Recargar datos
      setSuccess('Etiqueta agregada exitosamente');
    } catch (err) {
      console.error('Error adding tag:', err);
      setError('Error al agregar la etiqueta');
    } finally {
      setLoading(false);
    }
  };

  const removeTag = async (tagId: number) => {
    try {
      setLoading(true);
      await activityTrelloService.removeTagFromActivity(activityId, tagId, token);
      await loadActivityData(); // Recargar datos
      setSuccess('Etiqueta removida exitosamente');
    } catch (err) {
      console.error('Error removing tag:', err);
      setError('Error al remover la etiqueta');
    } finally {
      setLoading(false);
    }
  };

  // Funciones para etiquetas de color
  const addLabel = async (categoryId: number) => {
    try {
      setLoading(true);
      await activityTrelloService.addLabelToActivity(activityId, categoryId, token);
      await loadActivityData(); // Recargar datos
      setSuccess('Etiqueta de color agregada exitosamente');
    } catch (err) {
      console.error('Error adding label:', err);
      setError('Error al agregar la etiqueta de color');
    } finally {
      setLoading(false);
    }
  };

  const removeLabel = async (categoryId: number) => {
    try {
      setLoading(true);
      await activityTrelloService.removeLabelFromActivity(activityId, categoryId, token);
      await loadActivityData(); // Recargar datos
      setSuccess('Etiqueta de color removida exitosamente');
    } catch (err) {
      console.error('Error removing label:', err);
      setError('Error al remover la etiqueta de color');
    } finally {
      setLoading(false);
    }
  };

  // Funciones para comentarios
  const addComment = useCallback(async (content: string) => {
    if (!content.trim()) return;
    
    try {
      setLoading(true);
      setError(null);
      const newComment = await activityTrelloService.addCommentToActivity(activityId, content, token);
      setComments(prev => [newComment, ...prev]);
      setSuccess('Comentario agregado exitosamente');
    } catch (err: any) {
      console.error('Error adding comment:', err);
      setError(err.message || 'Error al agregar el comentario');
    } finally {
      setLoading(false);
    }
  }, [activityId, token]);

  const deleteComment = useCallback(async (commentId: number) => {
    try {
      setLoading(true);
      setError(null);
      await activityTrelloService.deleteActivityComment(activityId, commentId, token);
      setComments(prev => prev.filter(c => c.id !== commentId));
      setSuccess('Comentario eliminado exitosamente');
    } catch (err: any) {
      console.error('Error deleting comment:', err);
      setError(err.message || 'Error al eliminar el comentario');
    } finally {
      setLoading(false);
    }
  }, [activityId, token]);

  // Funciones para checklists
  const createChecklist = useCallback(async (title: string) => {
    if (!title.trim()) return;
    
    try {
      setLoading(true);
      setError(null);
      const newChecklist = await activityTrelloService.createChecklist(activityId, title, token);
      setChecklists(prev => [...prev, newChecklist]);
      setSuccess('Checklist creado exitosamente');
    } catch (err: any) {
      console.error('Error creating checklist:', err);
      setError(err.message || 'Error al crear el checklist');
    } finally {
      setLoading(false);
    }
  }, [activityId, token]);

  const addChecklistItem = useCallback(async (checklistId: number, content: string) => {
    if (!content.trim()) return;
    
    try {
      setLoading(true);
      setError(null);
      const newItem = await activityTrelloService.addChecklistItem(checklistId, content, token);
      setChecklists(prev => prev.map(checklist => 
        checklist.id === checklistId 
          ? { ...checklist, items: [...checklist.items, newItem] }
          : checklist
      ));
      setSuccess('Item agregado exitosamente');
    } catch (err: any) {
      console.error('Error adding checklist item:', err);
      setError(err.message || 'Error al agregar el item');
    } finally {
      setLoading(false);
    }
  }, [token]);

  const toggleChecklistItem = useCallback(async (itemId: number) => {
    try {
      setLoading(true);
      setError(null);
      const updatedItem = await activityTrelloService.toggleChecklistItem(itemId, token);
      setChecklists(prev => prev.map(checklist => ({
        ...checklist,
        items: checklist.items.map(item => 
          item.id === itemId ? updatedItem : item
        )
      })));
      setSuccess('Item actualizado exitosamente');
    } catch (err: any) {
      console.error('Error toggling checklist item:', err);
      setError(err.message || 'Error al actualizar el item');
    } finally {
      setLoading(false);
    }
  }, [token]);

  const deleteChecklistItem = useCallback(async (itemId: number) => {
    try {
      setLoading(true);
      setError(null);
      await activityTrelloService.deleteChecklistItem(itemId, token);
      setChecklists(prev => prev.map(checklist => ({
        ...checklist,
        items: checklist.items.filter(item => item.id !== itemId)
      })));
      setSuccess('Item eliminado exitosamente');
    } catch (err: any) {
      console.error('Error deleting checklist item:', err);
      setError(err.message || 'Error al eliminar el item');
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Funciones para adjuntos
  const uploadAttachment = async (file: File, description?: string) => {
    try {
      setLoading(true);
      const newAttachment = await activityTrelloService.uploadAttachment(activityId, file, description, token);
      setAttachments(prev => [...prev, newAttachment]);
      setSuccess('Adjunto subido exitosamente');
    } catch (err) {
      console.error('Error uploading attachment:', err);
      setError('Error al subir el adjunto');
    } finally {
      setLoading(false);
    }
  };

  const deleteAttachment = async (attachmentId: number) => {
    try {
      setLoading(true);
      await activityTrelloService.deleteAttachment(attachmentId, token);
      setAttachments(prev => prev.filter(a => a.id !== attachmentId));
      setSuccess('Adjunto eliminado exitosamente');
    } catch (err) {
      console.error('Error deleting attachment:', err);
      setError('Error al eliminar el adjunto');
    } finally {
      setLoading(false);
    }
  };

  // Limpiar mensajes
  const clearMessages = useCallback(() => {
    setError(null);
    setSuccess(null);
  }, []);

  return {
    // Estados
    loading,
    error,
    success,
    assignees,
    tags,
    labels,
    comments,
    checklists,
    attachments,

    // Funciones de carga
    loadActivityData,

    // Funciones de asignados
    addAssignee,
    removeAssignee,

    // Funciones de etiquetas
    addTag,
    removeTag,

    // Funciones de etiquetas de color
    addLabel,
    removeLabel,

    // Funciones de comentarios
    addComment,
    deleteComment,

    // Funciones de checklists
    createChecklist,
    addChecklistItem,
    toggleChecklistItem,
    deleteChecklistItem,

    // Funciones de adjuntos
    uploadAttachment,
    deleteAttachment,

    // Utilidades
    clearMessages
  };
};
